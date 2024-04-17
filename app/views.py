from django.shortcuts import render, redirect, HttpResponse
from django.views import View
import os, json
from django.http import JsonResponse
import base64
from app.models import * 
from django.utils.decorators import method_decorator
import hashlib
import re

# Create your views here.


def check_login(func):
    def wrapper(request):
        cookie = request.COOKIES.get('uid')
        if not cookie:
            return redirect('/login/')
        else:
            return func(request)
    return wrapper

# 登录
def login(request):
    if request.method == "POST":
        name = request.POST.get('name')
        pwd = request.POST.get('pwd')
        
        md5 = hashlib.md5()
        md5.update(pwd.encode('utf-8'))
        pwd = md5.hexdigest()
        print("用户名 ",name, "\n密码的md5值 ", pwd)
        if User.objects.filter(name=name, password=pwd):
            obj = redirect('/')
            obj.set_cookie('uid', User.objects.filter(name=name, password=pwd)[0].id, max_age=60 * 60 * 24)
            return obj
        else:
            msg = "用户信息错误，请重新输入！！"
            return render(request, 'login.html', {"msg":msg})
    else:
        uid = int(request.COOKIES.get('uid', -1))
        if uid != -1:
            return redirect('/')
        else:
            return render(request, 'login.html', locals())

# 注销
def logout(request):
    obj = redirect('/')
    obj.delete_cookie('uid')
    return obj    

# 注册
class register(View):
    def post(self, request):
        name = request.POST.get('name')
        tel = request.POST.get('tel')
        pwd = request.POST.get('pwd') 
        pwd1 = request.POST.get('pwd1')
        
        if len(tel) == 0 or not re.search(r"^\d{11}$", tel) :
            msg = "请填入正确的手机号码！"
            
        elif len(name) == 0:
            msg = "请填入用户名！"

        elif User.objects.filter(name=name):
            msg = "用户名已存在，请登录！"
        
        elif not re.search(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,18}$", pwd):
            msg = "密码必须包含大小写字母、数字，且长度为8-18位!"
        
        elif len(pwd1) == 0:
            msg = "请再次输入密码！"
        
        elif pwd != pwd1:
            msg = "两次密码不相同，请重试！"
        
        else:
            md5 = hashlib.md5()
            md5.update(pwd.encode('utf-8'))
            pwd = md5.hexdigest()
            User.objects.create(name=name, tel=tel, password=pwd)
            print("用户名 ",name, "\n电话号码 ", tel, "\n密码的md5值 ", pwd)
            msg = "注册成功!"
            return render(request, 'login.html', {"msg":msg})
        
        return render(request, "register.html",locals())
    def get(self, request):
        msg = ""
        return render(request, 'register.html',locals())





@check_login
def index(request):
    return render(request, 'index.html', locals())

def predict_img_label(image_path):
    # 图片路径
    image_path  = os.path.abspath(image_path)
    print("图片路径为 "+image_path)
    
    # 当前路径
    current_dir = os.path.abspath(os.path.curdir)
    print("当前路径为 "+current_dir)
    
    # yolov5路径
    yolo5_dir =  os.path.join(current_dir,"yolov5")
    print("yolov5的路径为 "+yolo5_dir)
    
    result = {}
    cmd = f'python3 {yolo5_dir}/detect.py --weights {yolo5_dir}/meiyanshi.engine --source {image_path} --device 0 --data {yolo5_dir}/data/meiganshi.yaml'
    
    os.system(cmd)
    # 若识别到了物体，则继续进行
    exps = os.listdir(os.path.join(yolo5_dir,"runs","detect"))
        
    calc = 0
    for i in exps:
        if len(i) > 3:
            exps[calc] = int(i.replace("exp", ""))
        calc += 1
    
    exps = [x for x in exps if isinstance(x, int)]
    if len(exps) == 0:
        exps = ""
    else:
        exps = str(max(exps))
    print("exp"+exps)
    
    filename = image_path.split('/')[-1]
    filename = os.path.join(yolo5_dir,"runs","detect",f"exp{exps}",f"{filename}.json")
    if os.path.exists(filename):
        result = json.load(open(filename,"r"))
        # 返回Json文件和识别后的文件路径
        print("识别后的文件路径为 "+filename[:-5])
        return result, filename[:-5]
    # 若未识别到物体，则返回False
    else:
        return False, False
    
    
    
class predict(View):
    @method_decorator(check_login)
    def get(self, request):
        return render(request, 'predict.html', locals())

    @method_decorator(check_login)
    def post(self, request):
        print("图片上传中...")
        # 从前端获取文件
        if request.FILES.get('file'):
            file = request.FILES.get('file')
            # 把文件放入项目的upload目录中
            current_path = os.path.abspath(os.path.curdir)
            filename = os.path.join(current_path,'static', 'upload', file.name)
            
            f = open(filename, 'wb')
            for line in file.chunks():  # 分块接收上传的文件
                f.write(line)
            f.close()
            
            image_path = filename
            result, filename = predict_img_label(image_path=image_path)
            if (result == False):
                return JsonResponse({'status':200,'msg':'操作失败',"result":None,"img":None} )
            
            with open(filename,"rb") as img_file:
                # image_data = base64.b64encode(img_file.read()).decode('utf-8')
                image_data = 'data:image/jpeg;base64,' + str(base64.b64encode(img_file.read()), 'utf-8')

            result = result[0]
            print(result)
            return JsonResponse({'status':200,'msg':'操作成功',"result":result,"img":image_data} )

        else:
            return JsonResponse({'code': 200, 'msg': '上传失败'})

class me(View):
    @method_decorator(check_login)
    def get(self, request):
        uid = int(request.COOKIES.get('uid', -1))
        my_info = User.objects.filter(id=uid)[0]
        return render(request, "me.html", locals())

class update(View):
    @method_decorator(check_login)
    def get(self, request):
        uid = int(request.COOKIES.get('uid', -1))
        my_info = User.objects.filter(id=uid)[0]
        return render(request, "update.html", locals())
    
    @method_decorator(check_login)
    def post(self, request):
        uid = int(request.COOKIES.get('uid', -1))
        my_info = User.objects.filter(id=uid)[0]
        work_type = request.POST.get('type')
        # 若进行修改密码操作
        if int(work_type) == 1:
            name = request.POST.get('name')
            tel = request.POST.get('tel')
            old_pwd = request.POST.get('old_password') 
            pwd = request.POST.get('password')
            pwd1 = request.POST.get('password1')
            
            
            
            # 对旧密码进行md5计算
            md5 = hashlib.md5()
            md5.update(old_pwd.encode('utf-8'))
            old_pwd = md5.hexdigest()
            
            if name != my_info.name:
                msg = "不可修改他人密码！"
                
            elif not User.objects.filter(id=uid, tel=tel):
                msg = "当前账户手机号码错误！"
            
            elif not User.objects.filter(id=uid, name=name, password=old_pwd):
                msg = "旧密码错误！"
            
            elif not re.search(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,18}$", pwd):
                msg = "新密码必须包含大小写字母、数字，且长度为8-18位!"
            
            elif pwd != pwd1:
                msg = "两次密码不相同，请重试！"
                
            else:
                # 对新密码进行md5计算
                md5 = hashlib.md5()
                md5.update(pwd.encode('utf-8'))
                pwd = md5.hexdigest()
                
                User.objects.filter(id=uid).update(name=name,password=pwd)
                return redirect("/logout/")
            
            return render(request, "update.html", locals())
            
        elif int(work_type)==2:
            name = request.POST.get('name')
            tel = request.POST.get('tel')
            gender = request.POST.get('gender')
            age = request.POST.get('age')
            addr1 = request.POST.get('addr1')
            addr2 = request.POST.get('addr2')
            addr3 = request.POST.get('addr3')
            address = request.POST.get('address')
            email = request.POST.get('email')
            words = request.POST.get('words')
            
            address = addr1 + addr2 + addr3 + address
            User.objects.filter(id=uid).update(name=name, tel=tel, gender=gender,age=age,address=address,email=email,words=words)
            return render(request, "me.html",locals())