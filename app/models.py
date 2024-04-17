from django.db import models

# Create your models here.

class User(models.Model):
    GENDER_CHOICE = (
        (1, '男'),
        (0, '女'),
    )
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=128,verbose_name="用户名")
    tel = models.CharField(max_length=18,verbose_name="手机号")
    password = models.CharField(max_length=128,verbose_name="密码",default="123456")
    gender = models.BooleanField(choices=GENDER_CHOICE, verbose_name="性别",default=1)
    age = models.IntegerField(verbose_name="年龄",default=0)
    address = models.CharField(max_length=128,verbose_name="家庭住址", default="保密")
    email = models.CharField(max_length=128, verbose_name="邮箱",default="123@123.123")
    words = models.CharField(max_length=255,verbose_name="个性前面", default="我思故我在")
    class Meta:
        verbose_name_plural = '用户表'  # 此时，admin中表的名字就是verbose_name_plural