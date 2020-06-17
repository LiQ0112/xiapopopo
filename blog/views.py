from django.shortcuts import render,HttpResponse,redirect
from blog.forms import RegForm
from django.http import JsonResponse
from blog import forms
from blog import models
from django.views.decorators.csrf import csrf_exempt
from geetest import GeetestLib
from django.contrib.auth import authenticate
from django.contrib import auth
import json
from django.db.models import F
pc_geetest_id = "b46d1900d0a894591916ea94ea91bd2c"
pc_geetest_key = "36fc3fe98530eea08dfc6ce76e3d24c4"
# Create your views here.
def login(request):
    if request.method == "POST":
        ret = {"status":0,"msg":""}
        username = request.POST.get("username")
        password = request.POST.get("password")
        gt = GeetestLib(pc_geetest_id, pc_geetest_key)
        challenge = request.POST.get(gt.FN_CHALLENGE, '')
        validate = request.POST.get(gt.FN_VALIDATE, '')
        seccode = request.POST.get(gt.FN_SECCODE, '')
        status = request.session[gt.GT_STATUS_SESSION_KEY]
        user_id = request.session["user_id"]
        if status:
            result = gt.success_validate(challenge, validate, seccode, user_id)
        else:
            result = gt.failback_validate(challenge, validate, seccode)
        if result:
            user = authenticate(username=username,password=password)
            if user:
                auth.login(request,user)
                ret["msg"] = "/index/"
            else:
                ret["status"] = 1
                ret["msg"] = "用户名或密码错误！"
        else:
            ret["status"] = 1
            ret["msg"] = "验证码错误"
        return JsonResponse(ret)
    return render(request,'login.html')

def get_geetest(request):
    user_id = 'test'
    # print("*"*120)
    gt = GeetestLib(pc_geetest_id, pc_geetest_key)
    status = gt.pre_process(user_id)
    request.session[gt.GT_STATUS_SESSION_KEY] = status
    request.session["user_id"] = user_id
    response_str = gt.get_response_str()
    return HttpResponse(response_str)

def index(request):
    article_list = models.Article.objects.all()
    return render(request,"index.html",{"article_list":article_list})

@csrf_exempt
def register(request):
    if request.method == "POST":
        # print(request.POST)
        ret = {"status": 0,"msg":""}
        form_obj = forms.RegForm(request.POST)
        # print(form_obj.is_valid())
        if form_obj.is_valid():
            form_obj.cleaned_data.pop("re_password")
            avatar_img = request.FILES.get("avatar")
            models.UserInfo.objects.create_user(**form_obj.cleaned_data,avatar=avatar_img)
            ret["msg"] = "/login/"
            return JsonResponse(ret)
        else:
            ret["status"] = 1
            ret["msg"] = form_obj.errors
            return JsonResponse(ret)
        # print(form_obj)
    form_obj = forms.RegForm()

    return render(request,'register.html',{"form_obj":form_obj})

def check_username(request):
    if request.method == "POST":
        ret = {"status": 0,"msg":""}
        username = request.POST.get("username")
        user = models.UserInfo.objects.filter(username =username)
        if user:
            ret["status"] = 1
            ret["msg"] = "用户名已存在！"
            return JsonResponse(ret)
        return JsonResponse(ret)

def logout(request):
    auth.logout(request)
    return redirect("/index/")

#个人博客主页
def home(request,username):
    # print(username)
    user = models.UserInfo.objects.filter(username = username).first()
    if not user:
        return HttpResponse("404")
    #如果用户存在，需要将用户写的所有文章拿出来
    blog = user.blog
    #文章列表
    article_list = models.Article.objects.filter(user=user)
    #文章分类及分类下文章的数量

    # print(archive_list)
    return render(request,"home.html",{
        "username":username,
        "blog":blog,
        "article_list":article_list,
    })

# 博客详情页
def article_detail(request,username,pk):
    '''
    :param pk:访问文章的主键id值
    :return:
    '''
    user = models.UserInfo.objects.filter(username=username).first()
    if not user:
        return HttpResponse("404")
    blog = user.blog
    article = models.Article.objects.filter(pk=pk).first()
    comment_list = models.Comment.objects.filter(article_id=pk)
    return render(request,
                  'article_detail.html',
                  {
                      "username":username,
                      "article":article,
                      "blog":blog,
                      "comment_list":comment_list
                  })


def up_down(request):
    response = {"state":True}
    article_id = request.POST.get("article_id")
    is_up = json.loads(request.POST.get("is_up"))
    user = request.user
    try:
        models.ArticleUpDown.objects.create(article_id=article_id,is_up=is_up,user=user)
        if is_up:
            models.Article.objects.filter(pk=article_id).update(up_count=F("up_count")+1)
        else:
            models.Article.objects.filter(pk=article_id).update(down_count=F("down_count") + 1)
    except Exception as e:
        response["state"]=False
        response["first_action"] = models.ArticleUpDown.objects.filter(user=user,article_id=article_id).first().is_up
        print(response["first_action"])
    return JsonResponse(response)

#评论视图
def comment(request):
    print(request.POST)
    pid = request.POST.get("pid")
    article_id = request.POST.get("article_id")
    content = request.POST.get("comment_content")
    user_pk = request.user.pk
    response = {}
    if not pid:
        com_obj = models.Comment.objects.create(article_id=article_id,content=content,user_id=user_pk)
    if pid:
        com_obj = models.Comment.objects.create(article_id=article_id, content=content, user_id=user_pk,parent_comment_id=pid)
    response["create_time"] = com_obj.create_time
    response["content"] = com_obj.content
    response["username"] = com_obj.user.username

    return JsonResponse(response,safe=False)

# 评论树
def comment_tree(request,article_id):
    ret = list(models.Comment.objects.filter(article_id=article_id).values("pk","content","parent_comment_id"))
    return JsonResponse(ret,safe=False)

def add_article(request):
    return render(request,"add_article.html")
from bbs import settings
import os
def upload(request):
    # print(request.FILES)
    obj = request.FILES.get("upload_img")
    path = os.path.join(settings.MEDIA_ROOT,"add_article",obj.name)
    with open(path,"wb") as f:
        for line in obj:
            f.write(line)
    response = {
        "error":0,
        "url":"/media/add_article/"+obj.name
    }
    return JsonResponse(response)