from django.db import models

# Create your models here.
class UserInfo(models.Model):
    username = models.CharField(validators='用户名', max_length=32)
    email = models.EmailField(validators='邮箱', max_length=32)
    mobile_phone = models.CharField(validators='手机号', max_length=32)
    password = models.CharField(validators='密码', max_length=64)

