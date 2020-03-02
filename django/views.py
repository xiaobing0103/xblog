from django.shortcuts import render,redirect
import ast
from django.http import HttpResponse,JsonResponse
from .models import User,Documents
from functools import wraps
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
from django.db.models import Q
from .sendemail import Sendmail,check_code
# Create your views here.

def check_login(func):
    @wraps(func)
    def inner(request,*args,**kwargs):
        ret = request.session.get("login")
        if ret == "success":
            return func(request, *args, **kwargs)
        else:
            return redirect('/xblog/')
    return inner

def index(request):
    sub_value = request.GET.get('submit')
    query = request.GET.get('search')
    name = request.session.get("fullname")
    alper = request.GET.get('alper')
    search = ''
    if name:
        fullname = name
    else:
        fullname = "游客"
    if alper == None:
        if query:
            alpers = query
            search = query
            document = Documents.objects.filter(Q(content__icontains=query) | Q(title__icontains=query))
        else:
            alpers = 'all'
            document = Documents.objects.all().order_by()
    else:
        if alper == 'all':
            alpers = alper
            document = Documents.objects.all().order_by()
        else:
            search = alper
            alpers = alper
            document = Documents.objects.filter(Q(content__icontains=alper) | Q(title__icontains=alper))

    paginator = Paginator(document,10)
    p_sum = paginator.num_pages 
    page_number = 1 
    if sub_value:
        if sub_value == 'pre':
            page_number = int(page_number) - 1
            if page_number < 1:
                page_number = 1
        elif sub_value == 'next':
            page_number = int(page_number) + 1
            if page_number > p_sum:
                page_number = p_sum
    strat = int(page_number - 1) * 10
    page = paginator.page(page_number)  
    desktop = Documents.objects.filter(doc_type='桌面运维文档').count()
    system = Documents.objects.filter(doc_type='系统技术文档').count()
    app = Documents.objects.filter(doc_type='应用技术文档').count()
    net = Documents.objects.filter(doc_type='网络技术文档').count()
    dev = Documents.objects.filter(doc_type='开发技术文档').count()
    msg = {
        'fullname':fullname,
        # 'count':count,
        'desktop':desktop,
        'system':system,
        'app':app,
        'net':net,
        'dev':dev,
        'alpers':alpers,
        'search':search,
    }
    return render(request,'xblog/index.html',
    {'document': page,'strat':strat,'msg':msg,'current':page_number,'sum':p_sum}) 

def login(request):
    if request.method == 'GET':
        return render(request,'xblog/index.html')
    else:
        xblog_name = request.POST.get('user_name')
        xblog_password = request.POST.get('user_password')
        try:
            ck_name = User.objects.get(name=xblog_name)
            pwd_ck = ck_name.password
            if xblog_password == pwd_ck:
                fullname = ck_name.fullname
                user = ck_name.name

                request.session["login"] = "success"
                request.session["fullname"] = fullname
                request.session["user"] = user
                request.session.set_expiry(600)

                msg = {
                    'code': '200',
                    'fullname': ck_name.fullname,
                }
                return JsonResponse(msg)
            else:
                msg = {
                    'code': '400',
                    'tips' :'密码错误，请重新输入',
                }
                return JsonResponse(msg) 
        except:
            msg = {
                'code': '401',
                'tips': '用户名不存在',
            }
            return JsonResponse(msg)

def logout(request):
    request.session.flush()
    return redirect('/xblog/')

@check_login
def main(request):  
    sub_value = request.GET.get('submit')
    alper = request.GET.get('alper')
    all = request.GET.get('bu_all')
    query = request.GET.get('search')
    fullname = request.session.get("fullname")
    name = request.session.get("user")
    search = ''
    if alper == None:
        if query:
            alpers = query
            search = query
            document = Documents.objects.filter(Q(content__icontains=query) | Q(title__icontains=query)).order_by()
        elif all:
            alpers = 'all'
            document = Documents.objects.all().order_by()
        else:
            alpers = 'personal'
            document = Documents.objects.filter(author=name).order_by()
    else:
        if alper == 'all':
            alpers = 'all'
            document = Documents.objects.all().order_by()
        elif alper == 'personal':
            alpers = 'personal'
            document = Documents.objects.filter(author=name).order_by()
        else:
            alpers = alper
            search = alper
            document = Documents.objects.filter(Q(content__icontains=alper) | Q(title__icontains=alper)).order_by()

    print(alpers)
    paginator = Paginator(document,10)
    p_sum = paginator.num_pages 
    page_number = 1 
    # if sub_value:
    if sub_value == 'pre':
        page_number = int(page_number) - 1
        if page_number < 1:
            page_number = 1
    elif sub_value == 'next':
        page_number = int(page_number) + 1
        if page_number > p_sum:
            page_number = p_sum
    strat = int(page_number - 1) * 10
    page = paginator.page(page_number)  
    count = Documents.objects.filter(author=name).count()
    desktop = Documents.objects.filter(Q(author=name) & Q(doc_type='桌面运维文档')).count()
    system = Documents.objects.filter(Q(author=name) & Q(doc_type='系统技术文档')).count()
    app = Documents.objects.filter(Q(author=name) & Q(doc_type='应用技术文档')).count()
    net = Documents.objects.filter(Q(author=name) & Q(doc_type='网络技术文档')).count()
    dev = Documents.objects.filter(Q(author=name) & Q(doc_type='开发技术文档')).count()
    msg = {
        'fullname':fullname,
        'count':count,
        'desktop':desktop,
        'system':system,
        'app':app,
        'net':net,
        'dev':dev,
        'alpers':alpers,
        'search':search,
    }
    return render(request,'xblog/main.html',
    {'document': page,'strat':strat,'msg':msg,'current':page_number,'sum':p_sum})

@check_login
def new(request):
    if request.method == 'GET':
        return render(request,'xblog/new.html')
    else:
        f_title = request.POST.get('title')
        f_content = request.POST.get('content') 
        f_type = request.POST.get('type_doc')
        f_text = request.POST.get('text')
        f_date = request.POST.get('datetime')
        f_author = request.session.get('user')

        add_doc = Documents(title=f_title,content=f_content,doc_type=f_type,text=f_text,createdate=f_date,author=f_author);
        add_doc.save();
        msg = {
                    'code': '200',
                }
        return JsonResponse(msg)

def details(request,doc_id):
    name = request.session.get("fullname")
    username = request.session.get("user")
    if name:
        fullname = name
    else:
        fullname = "游客"
    s_doc = Documents.objects.get(id=doc_id)
    msg = {
        'fullname':fullname,
        'username':username,
    }
    return render(request,'xblog/details.html',{'doc': s_doc,'msg':msg})

@check_login
def delete(request):
    if request.method == 'POST':
        delete_id = request.POST.get('delete_data')
        Documents.objects.get(id=delete_id).delete()
        del_statu={
            'code':200,
        }
        return JsonResponse(del_statu)

@check_login
def alter(request):
    if request.method == 'GET':
        id = request.GET.get('alter_id')
        alter_data = Documents.objects.get(id=id)
    else:
        f_id = request.POST.get('data_id')
        f_title = request.POST.get('title')
        f_content = request.POST.get('content') 
        f_type = request.POST.get('type_doc')
        f_text = request.POST.get('text')
        f_date = request.POST.get('datetime')
        Documents.objects.filter(id=f_id).update(title=f_title,content=f_content,doc_type=f_type,text=f_text,editdate=f_date);
        msg = {
                    'code': '200',
                }
        return JsonResponse(msg)
    return render(request,'xblog/alter.html',{'data': alter_data,})

def register(request):
    if request.method == 'GET':
        return render(request,'xblog/register.html')
    elif request.method == 'POST':
        check_char = request.POST.get('check_char')
        email = request.POST.get('email')
        if check_char:
            code = check_code(6)
            Sendmail(email,code)
            msg = {
                'code':code,
            }
            return JsonResponse(msg)
        else:
            email = request.POST.get('email')
            username = request.POST.get('user_name')
            password = request.POST.get('user_password')
            fullname = request.POST.get('fullname')
            check = request.POST.get('check')
            recode = request.POST.get('recode')

            code2 = check[0:6]
            c1 = code2.lower()
            c2 = recode.lower()
            if c1 == c2:
                adduser = User(name=username,password=password,fullname=fullname,email=email);
                adduser.save();
                msg = {
                    'code': '200',
                }              
            else:
                msg = {
                    'code': '500'
                }
            return JsonResponse(msg)