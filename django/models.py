from django.db import models

# Create your models here.
class User(models.Model):
    name = models.CharField(unique=True,max_length=30)
    password = models.CharField(max_length=30)
    fullname = models.CharField(max_length=30)
    email = models.CharField(max_length=50)

class Documents(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    text = models.TextField()
    doc_type = models.CharField(max_length=10)
    author = models.CharField(max_length=20)
    createdate = models.CharField(max_length=20)
    editdate = models.CharField(null=True,max_length=20)