from django.urls import include,path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path('login/',views.login,name='login'),
    path('logout/',views.logout,name='logout'),
    path('main/',views.main,name='main'),
    path('new/',views.new,name='new'),
    path('delete/',views.delete,name='delete'),
    path('alter/',views.alter,name='alter'),
    path('register/',views.register,name='register'),
    path(r'^details(?P<doc_id>\d+)/',views.details,name='details'),
] + static(settings.STATIC_URL,document_root = settings.STATIC_ROOT)
