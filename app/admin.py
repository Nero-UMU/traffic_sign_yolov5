from django.contrib import admin
from app.models import *

# admin.py
admin.site.site_header = '交通信号识别管理系统'  # 登录显示
admin.site.site_title = '交通信号识别管理系统'  # title
admin.site.index_title = '交通信号识别管理系统' 

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    # list_display用于设置列表页面要显示的不同字段
    list_display = ['id', 'name', 'tel', 'password']
    # search_fields用于设置搜索栏中要搜索的不同字段,如有外键应使用双下划线连接两个模型的字段
    search_fields = ['id', 'name', 'tel', 'password']


from django.contrib.auth.models import Group, User
admin.site.unregister(Group)
admin.site.unregister(User)