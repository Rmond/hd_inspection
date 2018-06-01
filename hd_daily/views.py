# -*- coding:utf-8 -*-
from __future__ import print_function

import base64
import json,os,datetime,time

from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password, check_password

from models import Users,Inspection

def login_check(func):#登录检查装饰器
    def wrapper(request,*args,**kwargs):
        if 'HTTP_AUTHORIZATION' in request.META:
            auth = request.META['HTTP_AUTHORIZATION'].split()
            if len(auth) == 2:
                if auth[0].lower() == "basic":
                    uname,passwd = base64.b64decode(auth[1]).split(':')
                    user = authenticate(uname,passwd)
                    if user:
                        request.session['is_login'] = user.nickname
                        request.session['username'] = user.username
                        request.session['role'] = user.role
                        request.session['authmethod'] = "basic"
        nickname = request.session.get('is_login',None)
        if not nickname:
            return redirect('/login')
        return func(request,*args,**kwargs)
    return wrapper

def user_role(func):#用户角色检查装饰器
    def wrapper(request,*args,**kwargs):
        role = request.session.get('role',None)
        if role == 0:#管理员
            return func(request)
        elif role == 1:#普通用户
            return HttpResponse('Permission denied')
    return wrapper

def authenticate(username,password):
    try:
        user = Users.objects.get(username=username)
        if check_password(password, user.password):  # 登录判断
            return user
        else:  # 判断密码是否正确
            return None
    except Users.DoesNotExist:  # 判断用户是否存在
        return None

# Create your views here.
@csrf_exempt
def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username,password)
        if user:
            request.session['is_login'] = user.nickname
            request.session['username'] = user.username
            request.session['role'] = user.role
            return redirect('/index')
        else:#判断密码是否正确
            return render(request,"login.html",{'msg':'用户名或密码错误'})
    return render(request,"login.html")

@login_check
def index(request):
    user_count = Users.objects.count()
    return render(request,"index.html",)


@login_check
def logout(request):
    del request.session['is_login']
    return redirect('/login')


@login_check
def user_list(request):  # 用户列表展示
    results = Users.objects.all()
    return render(request, "userlist.html", {'users': results})


@csrf_exempt
@login_check
def pwd_reset(request):  # 密码重置为6个1
    if request.method == 'POST':
        username = request.POST['username']
        user = Users.objects.get(username=username)
        user.password = make_password('111111')
        user.save()
        return HttpResponse("密码重置成功！")


@csrf_exempt
@login_check
@user_role
def user_add(request):  # 用户添加或修改
    if request.method == 'POST':
        username = request.POST['username']
        nickname = request.POST['nickname']
        role = request.POST['role']
        if Users.objects.filter(username=username):  # 判断用户是否存在
            user = Users.objects.get(username=username)
            user.nickname = nickname
            user.role = role
        else:
            password = make_password('111111')
            user = Users(username=username, nickname=nickname, password=password, role=role)
        user.save()
        return redirect('userlist.html')


@csrf_exempt
@login_check
@user_role
def user_del(request):  # 用户删除
    if request.method == 'POST':
        username = request.POST['username']
        Users.objects.filter(username=username).delete()
        return HttpResponse('Success')


@csrf_exempt
@login_check
@user_role
def user_look(request):  # 用户信息查看
    if request.method == 'POST':
        username = request.POST['username']
        user = Users.objects.get(username=username)
        return HttpResponse(json.dumps({"username": user.username, "nickname": user.nickname, "role": user.role}))


@csrf_exempt
@login_check
def username_check(request):  # 添加用户时，表单查询用户是否存在
    if request.method == 'POST':
        username = request.POST['username']
        if Users.objects.filter(username=username):
            return HttpResponse(0)
        else:
            return HttpResponse(1)


@csrf_exempt
@login_check
def user_info(request):
    if request.method == 'POST':
        username = request.session.get('username', None)
        user = Users.objects.get(username=username)
        return HttpResponse(json.dumps({'username': user.username, 'nickname': user.nickname}))


@csrf_exempt
@login_check
@user_role
def user_edit(request):
    if request.method == 'POST':
        username = request.POST['username']
        nickname = request.POST['nickname']
        password = request.POST['password']
        user = Users.objects.get(username=username)
        user.nickname = nickname
        user.password = make_password(password)
        user.save()
        return HttpResponse("Success")

@csrf_exempt
@login_check
def daily_add(request):
    if request.method == 'POST':
        server_stats = request.POST['server_stats']
        backup_stats = request.POST['backup_stats']
        remark = request.POST.get('remark','')
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        if request.POST.get('date',None):
            today=request.POST['date']
        try:
            inspection = Inspection.objects.get(date_done=today)
        except Inspection.DoesNotExist:  # 判断用户是否存在
            inspection = Inspection()
            inspection.date_done = today
        inspection.server_stats = server_stats
        inspection.backup_stats = backup_stats
        inspection.remark = remark
        inspection.username = request.session.get('username','')
        inspection.save()
        if request.session.get('authmethod', None):
            return HttpResponse('Success')
        else:
            return redirect('index.html')
    return redirect('index.html')

@csrf_exempt
@login_check
def daily_list(request):
    if request.method == 'POST':
        search = request.POST.get('search[value]')
        draw = int(request.POST.get('draw'))
        start = int(request.POST.get('start'))
        length = int(request.POST.get('length'))
        end = start+length
        daily_set = Inspection.objects.all()
        if search != "":
            daily_set = daily_set.filter(Q(date_done__contains=search)|Q(username__contains=search)|Q(server_stats__contains=search)|Q(backup_stats__contains=search))
        daily_list = daily_set.values_list('date_done','username','server_stats','backup_stats','remark').order_by('-date_done')[start:end]
        daily_count = daily_set.count()
        _filter = daily_count
        all_lists = map(list,daily_list)
        data = {
            'draw':draw,
            'recordsTotal':daily_count,
            'recordsFiltered':_filter,
            'data':all_lists
        }
        return HttpResponse(json.dumps(data))