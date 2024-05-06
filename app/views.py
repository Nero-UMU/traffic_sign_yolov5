import random
from django.shortcuts import render, redirect, HttpResponse
from django.views import View
import os, json
from django.http import JsonResponse
import base64
from app.models import * 
from django.utils.decorators import method_decorator
import hashlib
import re
import csv

# Create your views here.


def label_replace(list):
    all_name = ['禁止车辆临时或长时停放', '禁止驶入', '靠右侧道路行驶', '禁止鸣喇叭', '限制速度40', 'po', '限制速度50', '出入口', '限制速度80',
                '限制速度60', '禁止载货汽车驶入', '机动车行驶', '限制速度100', '限制速度30', '最低限速60', '非机动车行驶', '限制速度5',
                '注意行人', '禁止掉头', '禁止机动车驶入', '限制速度120', '最低限速80', '人行横道', '禁止向左转弯', '解除限制速度40', '限制高度4.5m',
                '合流', '禁止大型客车驶入', '注意儿童', '限制质量20T', '禁止二轮摩托车驶入', '减速让行', '限制速度70', '限制质量55T', '限制速度20', '最低限速100', '十字交叉',
                '禁止向右转弯', '禁止运输危险物品车辆驶入', '限制高度4m', '限制质量30T', 'wo', '限制高度5m', '施工', '禁止非机动车进入']
    result_list = []
    for i in list:
        result_list.append(all_name[int(i)])
    return result_list
    
# 导入题目
def import_question_from_csv(csv_path):
    with open(csv_path, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)  # 跳过标题行
        for row in reader:
            question, A, B, C, D,correct_answer = row
            QuestionBank.objects.create(question=question, a=A, b=B, c=C, d=D, correct=correct_answer)

# 导入交通标志信息
def import_traffic_sign_from_csv(csv_path):
    with open(csv_path, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)  # 跳过标题行
        for row in reader:
            sign_name, sign_img, sign_description = row
            Traffic_sign.objects.create(sign_name=sign_name, sign_img=sign_img, sign_description=sign_description)

def check_login(func):
    def wrapper(request):
        cookie = request.COOKIES.get('uid')
        if not cookie:
            return redirect('/login/')
        else:
            return func(request)
    return wrapper

# 登录
class login(View):
    def post(self, request):
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
    def get(self, request):
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


class index(View):
    @method_decorator(check_login)
    def get(self, request):
        # import_traffic_sign_from_csv('static/images/trafficSign.csv')
        obj = User.objects.filter(id=request.COOKIES.get('uid'))[0]
        name = obj.name
        tel = obj.tel
        gender = obj.gender
        address = obj.address
        email = obj.email
        words = obj.words
        
        result = {
            "name": name,
            "tel": tel,
            "gender": gender,
            "address": address,
            "email": email,
            "words": words
        }
        return render(request, 'index.html', locals())

def processSign(sign):
    all_name = ['pn', 'pne', 'i5', 'p11', 'pl40', 'po', 'pl50', 'io', 'pl80',
                'pl60', 'p26', 'i4', 'pl100', 'pl30', 'il60', 'i2', 'pl5',
                'w57', 'p5', 'p10', 'pl120', 'il80', 'ip', 'p23', 'pr40', 'ph4.5',
                'w59', 'p3', 'w55', 'pm20', 'p12', 'pg', 'pl70', 'pm55', 'pl20', 'il100', 'w13',
                'p19', 'p27', 'ph4', 'pm30', 'wo', 'ph5', 'w32', 'p6']
    if sign[0] == "p":
        kind = "禁止标志"
    elif sign[0] == "i":
        kind = "指示标志"
    elif sign[0] == "w":
        kind = "警告标志"
    return kind


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
    cmd = f'python3 {yolo5_dir}/detect.py --weights {yolo5_dir}/runs/train/exp/weights/best.pt --source {image_path} --device cpu --save-txt --hide-labels'
    
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
    filename = filename[:-4]

    file_path = os.path.join(yolo5_dir,"runs","detect",f"exp{exps}", image_path.split('/')[-1])
    filename = os.path.join(yolo5_dir,"runs","detect",f"exp{exps}","labels",f"{filename}.txt")
    
    if os.path.exists(filename):
        file = open(filename, "r")
        file_list = file.readlines()
        
        result_list = []
        for i in file_list:
            result_list.append(i.split(" ")[0])
        return result_list, file_path
    # 若未识别到物体，则返回False
    else:
        return False, False

def car_img_recognition(image_path):
    # 图片路径
    image_path  = os.path.abspath(image_path)
    print("图片路径为 "+image_path)
    
    # 当前路径
    current_dir = os.path.abspath(os.path.curdir)
    print("当前路径为 "+current_dir)
    
    # Car_recognition路径
    Car_recognition_dir =  os.path.join(current_dir,"Car_recognition")
    print("Car_recognition的路径为 "+ Car_recognition_dir)
    
    os.chdir(Car_recognition_dir)
    cmd = f'python3 Car_recognition.py --detect_model weights/detect.pt --rec_model weights/plate_rec_color.pth --image_path {image_path} --output {current_dir}/static/recognitionResult'
    os.system(cmd)
    os.chdir(current_dir)
    filename = image_path.split('/')[-1]
    json_path = os.path.join(current_dir,"static/recognitionResult",f"{filename}.json")
    if os.path.exists(json_path):
        result = json.load(open(json_path,"r"))
        # 返回Json文件和识别后的文件路径
        print("识别后的文件路径为 "+ json_path[:-5])
        return result, json_path[:-5]
    # 若未识别到物体，则返回False
    else:
        return False, False
    
def predict_video(video_path):
    # 视频路径
    video_path  = os.path.abspath(video_path)
    print("视频路径为 "+video_path)
    
    # 当前路径
    current_dir = os.path.abspath(os.path.curdir)
    print("当前路径为 "+current_dir)
    
    # yolov5路径
    yolo5_dir =  os.path.join(current_dir,"yolov5")
    print("yolov5的路径为 "+yolo5_dir)
    
    cmd = f'python3 {yolo5_dir}/detect.py --weights {yolo5_dir}/runs/train/exp/weights/best.pt --source {video_path} --device cpu'
    
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
    
    filename = video_path.split('/')[-1]
    name = filename[:-4]
    suffix = filename[-4:]
    
    processedVideo = os.path.join(yolo5_dir,"runs","detect",f"exp{exps}",filename)
    # 移动处理后的视频到static下
    os.system(f'mv {processedVideo} static/processedVideo/')
    
    # 将yolov5处理后的视频用ffmpeg处理为可有浏览器播放的h264格式
    os.system(f'ffmpeg -y -i static/processedVideo/{filename} -c:v libx264 static/processedVideo/{name}-1{suffix}')
    os.system(f'mv static/processedVideo/{name}-1{suffix} static/processedVideo/{filename}')
    
    detected_video_path = f'/static/processedVideo/{filename}'
    print("检测后的视频位置 "+ detected_video_path)
    return detected_video_path
    
def car_video_recognition(video_path):
    # 视频路径
    video_path  = os.path.abspath(video_path)
    print("视频路径为 "+video_path)
    
    # 当前路径
    current_dir = os.path.abspath(os.path.curdir)
    print("当前路径为 "+current_dir)
    
    # Car_recognition路径
    Car_recognition_dir =  os.path.join(current_dir,"Car_recognition")
    print("Car_recognition的路径为 "+ Car_recognition_dir)
    
    os.chdir(Car_recognition_dir)
    cmd = f'python3 Car_recognition.py --detect_model weights/detect.pt --rec_model weights/plate_rec_color.pth --video {video_path} --output {current_dir}/static/recognitionResult'
    os.system(cmd)
    os.chdir(current_dir)
    
    filename = video_path.split('/')[-1]
    name = filename[:-4]
    suffix = filename[-4:]
    
    recognitionVideo = os.path.join(current_dir,"static/recognitionResult",f"{filename}_result.mp4")
    # 将处理后的视频用ffmpeg处理为可有浏览器播放的h264格式
    os.system(f'ffmpeg -y -i static/recognitionResult/{filename}_result.mp4 -c:v libx264 static/recognitionResult/{name}{suffix}')
    os.system(f'rm static/recognitionResult/{filename}_result.mp4')
    
    recognition_video_path = f'/static/recognitionResult/{filename}'
    print("检测后的视频位置 "+ recognition_video_path)
    return recognition_video_path
   
    

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
        
        
class detection(View):
    # 导入题库
    # import_question_from_csv('static/images/questionBank.csv')
    @method_decorator(check_login)
    def get(self, request):
        uid = int(request.COOKIES.get('uid', -1))
        username = User.objects.filter(id=uid)[0].name
        questionId_all = [i.id for i in QuestionBank.objects.all()]
        # 随机抽取1个题目到一个数组中
        questionId = random.sample(questionId_all , 1)
        question = QuestionBank.objects.filter(id__in=questionId)[0]
        return render(request, "detection.html", locals())

class detectionResault(View):
    @method_decorator(check_login)
    def post(self, request):
        uid = int(request.COOKIES.get('uid', -1))
        username = User.objects.filter(id=uid)[0].name
        select = request.POST.get('select')
        questionId = request.POST.get('questionId')
        
        # 正确答案
        correct = QuestionBank.objects.filter(id=questionId)[0].correct
        # 题目实例
        question = QuestionBank(id=questionId)
        # 用户实例
        user = User(id=uid)
        # 答题情况
        correct_or_not = int(correct == select)
        # 用户回答
        answer = select
        
        QuestionResult.objects.create(user=user,question=question,answer=answer,correct=correct,correct_or_not=correct_or_not,questionID=int(questionId))
        return redirect('/detectionResault/')
    
    @method_decorator(check_login)
    def get(self, request):
        uid = int(request.COOKIES.get('uid', -1))
        username = User.objects.filter(id=uid)[0].name
        user = User(id=uid)
        
        resault_list = []
        questionObj = QuestionResult.objects.filter(user=user)
        for obj in questionObj:
            # 题目
            question = obj.question
            # 用户回答
            answer = obj.answer
            # 正确答案
            correct = obj.correct
            # 答题情况
            correct_or_not =  obj.correct_or_not
            # 答题时间
            time = obj.time
            # 题目id
            id = obj.questionID
            resault = {
                'question':str(question.question),
                'answer':answer,
                'correct':correct,
                'correct_or_not':str(correct_or_not),
                'time':time,
                'id': id,
            }
            resault_list.append(resault)
        
        return render(request, "detectionResault.html", locals())
     
class questionResearch(View):
    @method_decorator(check_login)
    def get(self, request):
        questionID = request.GET.get('id')
        print(questionID)
        
        if not QuestionBank.objects.filter(id=questionID):
            return redirect('/detectionResault')
        obj = QuestionBank.objects.filter(id=questionID)
        
        question = obj[0].question
        a = obj[0].a
        b = obj[0].b
        c = obj[0].c
        d = obj[0].d
        correct = obj[0].correct
        result = {
            'id': questionID,
            'question': question,
            'a': a,
            'b': b,
            'c': c,
            'd': d,
            'correct': correct,
        }
        return render(request, "questionResearch.html", locals())
     
        
class predictPic(View):
    @method_decorator(check_login)
    def get(self, request):
        return render(request, 'predictPic.html', locals())

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

            
            result = label_replace(result)
            
            for i in result:
                user = User(id=int(request.COOKIES.get('uid', -1)))
                sign_name = i
                traffic_predict_result.objects.create(user=user,sign_name=sign_name)
            
            print(result)
            return JsonResponse({'status':200,'msg':'操作成功',"result":result,"img":image_data})

        else:
            return JsonResponse({'code': 200, 'msg': '上传失败'})
        
class predictVideo(View):
    @method_decorator(check_login)
    def get(self, request):
        return render(request, 'predictVideo.html',locals())
    
    def post(self, request):
        file = request.FILES.get('file')
        current_path = os.path.abspath(os.path.curdir)
        filename = os.path.join(current_path,'static', 'upload', file.name)
        f = open(filename, 'wb')
        for line in file.chunks():  # 分块接收上传的文件
            f.write(line)
        f.close()
        orignialVideo =  os.path.join('/static', 'upload', file.name)
        os.system(f'ffmpeg -y -i {current_path}{orignialVideo} -c:v libx264 {current_path}{orignialVideo}.mp4')
        os.system(f'mv {current_path}{orignialVideo}.mp4 {current_path}{orignialVideo}')
        processedVideo = predict_video(filename)
        
        return JsonResponse({'code':200, 'msg':'success', 'orignialVideo': orignialVideo, 'processedVideo':processedVideo})

class predictPicResult(View):
    @method_decorator(check_login)
    def get(self, request):
        uid = int(request.COOKIES.get('uid', -1))
        user = User(id=uid)
        result_Obj = traffic_predict_result.objects.filter(user=user)

        resault_list = []
        for obj in result_Obj:
            sign_name = obj.sign_name
            time = obj.time
            resault = {
                'sign_name':sign_name,
                'time':time,
            }
            
            resault_list.append(resault)
        return render(request, 'predictPicResult.html', locals())

class car_plate_recognition(View):
    @method_decorator(check_login)
    def get(self, request):
        return render(request, 'car_plate_recognition.html', locals())
    def post(self, request):
        file = request.FILES.get('file')
        current_path = os.path.abspath(os.path.curdir)
        filename = os.path.join(current_path,'static', 'upload', file.name)
        f = open(filename, 'wb')
        for line in file.chunks():  # 分块接收上传的文件
            f.write(line)
        f.close()
        result, filename = car_img_recognition(filename)
        filename = os.path.relpath(filename)
        result = result[0]
        print(result)
        with open(filename,"rb") as f:
            image_data = 'data:image/jpeg;base64,' + str(base64.b64encode(f.read()), 'utf-8')
        
        plate = result["result"].split(" ")
        plate_number = plate[0]
        plate_color = plate[1]
        
        plate_img = os.path.relpath(result["name"])
        Car_plate_recognition.objects.create(user=User(id=1),plate_number=plate_number,plate_color=plate_color,plate_img=plate_img)
        return JsonResponse({'code':200, 'msg':'操作成功', 'result':result,'img':image_data})        
    
class car_plate_recognition_video(View):
    @method_decorator(check_login)
    def get(self, request):
        return render(request, 'car_plate_recognition_video.html', locals())
    
    def post(self, request):
        file = request.FILES.get('file')
        current_path = os.path.abspath(os.path.curdir)
        filename = os.path.join(current_path,'static', 'upload', file.name)
        f = open(filename, 'wb')
        for line in file.chunks():  # 分块接收上传的文件
            f.write(line)
        f.close()
        
        os.system(f'ffmpeg -y -i {filename} -c:v libx264 {filename}.mp4')
        os.system(f'mv {filename}.mp4 {filename}')

        orignialVideo =  os.path.join('/static', 'upload', file.name)
        recognition_video = car_video_recognition(filename)
        return JsonResponse({'code':200, 'msg':'success', 'orignialVideo': orignialVideo, "recognition_video":recognition_video})

class car_plate_recognition_result(View):
    @method_decorator(check_login)
    def get(self, request):
        uid = int(request.COOKIES.get('uid', -1))
        user = User(id=uid)
        resault_list = []
        car_recognition_Obj = Car_plate_recognition.objects.filter(user=user)

        for obj in car_recognition_Obj:
            # 车牌号
            plate_number = obj.plate_number
            # 车牌颜色
            plate_color = obj.plate_color
            # 车牌图片
            plate_img = obj.plate_img
            # 识别时间
            time = obj.time
            resault = {
                "plate_color": plate_color,
                "plate_number": plate_number,
                "plate_img":"/" + plate_img,
                "time": time,
            }
            resault_list.append(resault)
        return render(request, "car_plate_recognition_result.html", locals())
        
class trafficSignResearch(View):
    @method_decorator(check_login)
    def get(self, request):
        uid = int(request.COOKIES.get('uid', -1))
        sign_name = request.GET.get('name')
        traffic_sign_research_history.objects.create(user=User(id=uid), search_history=sign_name)
        if not Traffic_sign.objects.filter(sign_name=sign_name):
            return redirect(f'/trafficSignResearchError/?name={sign_name}')
        obj = Traffic_sign.objects.filter(sign_name=sign_name)[0]
        sign_name = obj.sign_name
        sign_img = obj.sign_img
        sign_description = obj.sign_description
        result = {
            "sign_name": sign_name,
            "sign_img":  sign_img,
            "sign_description": sign_description,
        }

        comment_obj = traffic_sign_comment.objects.filter(sign_name=sign_name)
        comment_list = []
        for obj in comment_obj:
            user = obj.user
            comment = obj.comment
            time = obj.time
            comment = {
                "user": user,
                "comment": comment,
                "time": time,
            }
            comment_list.append(comment)
        print(comment_list)
        
        return render(request, 'trafficSignResearch.html', locals())
    
    def post(self, request):
        sign_name = request.POST.get('sign_name')
        comment = request.POST.get('comment')
        uid = int(request.COOKIES.get('uid', -1))
        user = User(id=uid)
        traffic_sign_comment.objects.create(user=user, sign_name=sign_name, comment=comment)
        
        return redirect(f'/trafficSignResearch/?name={sign_name}')
    
class trafficSignResearchError(View):
    def get(self, request):
        sign_name = request.GET.get('name')
        return render(request, 'trafficSignResearchError.html', locals())

class trafficSignPage(View):
    @method_decorator(check_login)
    def get(self,request):
        sign_all = [i.id for i in Traffic_sign.objects.all()]
        result_list = []
        for i in sign_all:
            obj = Traffic_sign.objects.filter(id=i)[0]
            sign_name = obj.sign_name
            sign_img = obj.sign_img
            sign_description = obj.sign_description
            result = {
                "sign_name": sign_name,
                "sign_img":  sign_img,
                "sign_description": sign_description,
            }
            result_list.append(result)
        random.shuffle(result_list)
        return render(request, 'trafficSignPage.html', locals())
    
    def post(self,request):
        search = request.POST.get('search')
        
        # return render(request, 'trafficSignResearchHistory.html', locals())
        return redirect(f'/trafficSignResearch/?name={search}')
    
class trafficSignResearchHistory(View):
    def get(self,request):
        uid = int(request.COOKIES.get('uid', -1))

        obj_all = traffic_sign_research_history.objects.filter(user=User(id=uid))
        result_list = []
        for obj in obj_all:
            search_history =  obj.search_history
            time = obj.time
            result = {
                'search_history': search_history,
                'time': time,
            }
            result_list.append(result)
        return render(request, 'trafficSignResearchHistory.html', locals())