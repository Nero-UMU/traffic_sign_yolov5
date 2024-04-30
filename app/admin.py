from django.contrib import admin
from app.models import *

# admin.py
admin.site.site_header = '交通标志识别管理系统'  # 登录显示
admin.site.site_title = '交通标志识别管理系统'  # title
admin.site.index_title = '交通标志识别管理系统' 

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    # list_display用于设置列表页面要显示的不同字段
    list_display = ['id', 'name', 'gender', 'age', 'tel','address', 'email', 'words', 'password']
    # search_fields用于设置搜索栏中要搜索的不同字段,如有外键应使用双下划线连接两个模型的字段
    search_fields = ['id', 'name', 'tel', 'email']

@admin.register(QuestionBank)
class QuestionBankAdmin(admin.ModelAdmin):
    list_display = ['id', 'question', 'a', 'b', 'c', 'd', 'correct']
    search_fields = ['id', 'question']

@admin.register(QuestionResult)
class QuestionResultAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'time', 'question', 'answer', 'correct', 'correct_or_not','questionID']
    search_fields = ['id', 'user']

@admin.register(Car_plate_recognition)
class Car_plate_recognitionAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'plate_number', 'plate_color','plate_img', 'time']
    search_fields = ['id', 'user']

from django.contrib.auth.models import Group, User
admin.site.unregister(Group)
admin.site.unregister(User)