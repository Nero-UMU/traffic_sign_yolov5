from django.db import models

# Create your models here.

# 用户
class User(models.Model):
    GENDER_CHOICE = (
        (1, '男'),
        (0, '女'),
    )
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=128,verbose_name="用户名")
    tel = models.CharField(max_length=18,verbose_name="手机号")
    password = models.CharField(max_length=128,verbose_name="密码的md5值",default="123456")
    gender = models.BooleanField(choices=GENDER_CHOICE, verbose_name="性别",default=1)
    age = models.IntegerField(verbose_name="年龄",default=0)
    address = models.CharField(max_length=128,verbose_name="家庭住址", default="保密")
    email = models.CharField(max_length=128, verbose_name="邮箱",default="123@123.123")
    words = models.CharField(max_length=255,verbose_name="个性签名", default="我思故我在")
    class Meta:
        verbose_name_plural = '用户表'  # 此时，admin中表的名字就是verbose_name_plural

# 题库
class QuestionBank(models.Model):
    correct_CHOICE = (
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
    )
    id = models.AutoField(primary_key=True)
    question = models.CharField(max_length=128,verbose_name='题目')
    a = models.CharField(max_length=128,verbose_name='A')
    b = models.CharField(max_length=128,verbose_name='B')
    c = models.CharField(max_length=128,verbose_name='C')
    d = models.CharField(max_length=128,verbose_name='D')
    correct = models.CharField(max_length=4,verbose_name='正确答案',choices=correct_CHOICE)
    class Meta:
        verbose_name = '题库'  # 定义在管理后台显示的名称
        verbose_name_plural = verbose_name  # 定义复数时的名称（去除复数的s）
        ordering = ['id']  # 排序
    def __str__(self):
        return self.question

# 答题情况
class QuestionResult(models.Model):
    isCorrect = (
        (1, '正确'),
        (0, '错误'),
    )
    
    correct_CHOICE = (
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
    )
    
    id = models.AutoField(primary_key=True)
    user  = models.ForeignKey(User,verbose_name='用户',on_delete=models.CASCADE, default=None)
    question = models.ForeignKey(QuestionBank , verbose_name='题目', on_delete=models.CASCADE)
    questionID = models.IntegerField(verbose_name='题目ID',default=0)
    answer = models.CharField(max_length=4,verbose_name='用户回答', choices=correct_CHOICE, default=1)
    correct = models.CharField(max_length=4,verbose_name='正确答案', choices=correct_CHOICE, default=1)
    correct_or_not = models.BooleanField(default=1, choices=isCorrect, verbose_name="答题情况")
    time = models.DateField(auto_now_add=True, verbose_name='答题时间')
    class Meta:
        verbose_name = '答题结果'  # 定义在管理后台显示的名称
        verbose_name_plural = verbose_name  # 定义复数时的名称（去除复数的s）
        ordering = ['time']  # 排序

# 车牌识别结果
class Car_plate_recognition(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, verbose_name='用户', on_delete=models.CASCADE, default=None)
    plate_number = models.CharField(max_length=128, verbose_name='车牌号', default='')
    plate_color = models.CharField(max_length=128, verbose_name='车牌颜色', default='')
    plate_img = models.CharField(max_length=128, verbose_name='车牌图片', default='')
    time = models.DateField(auto_now_add=True, verbose_name='识别时间')
    class Meta:
        verbose_name = '车牌识别结果'  # 定义在管理后台显示的名称
        verbose_name_plural = verbose_name  # 定义复数时的名称（去除复数的s）
        ordering = ['time']  # 排序
        
# 交通标志
class Traffic_sign(models.Model):
    id = models.AutoField(primary_key=True)
    sign_name = models.CharField(max_length=128, verbose_name='标志名称', default='')
    sign_img = models.CharField(max_length=128, verbose_name='标志图片', default='')
    sign_description = models.CharField(max_length=128, verbose_name='标志描述', default='')
    class Meta:
        verbose_name = "交通标志"  # 定义在管理后台显示的名称
        verbose_name_plural = verbose_name  # 定义复数时的名称（去除复数的s）
        ordering = ['id']  # 排序

# 交通标志识别结果
class traffic_predict_result(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, verbose_name='用户', on_delete=models.CASCADE, default=None)
    sign_name = models.CharField(max_length=128, verbose_name='标志名称', default='')
    time = models.DateField(auto_now_add=True, verbose_name='识别时间')
    class meta:
        verbose_name = '交通标志识别结果'  # 定义在管理后台显示的名称
        verbose_name_plural = verbose_name  # 定义复数时的名称（去除复数的s）
        ordering = ['time']  # 排序