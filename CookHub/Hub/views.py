from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.conf import settings
from .models import User, Post, Like, Step, Comment, View
from .forms import RegistrationForm, ChangeInformationForm
from django.core.exceptions import ObjectDoesNotExist
from datetime import date
from django.views import View

# req là thông điệp từ client truyền vào


def get_user(req):
    if req.user.username:                                       # nếu như có tên tài khoản (tức đã đăng nhập)
        try:
            user_ = User.objects.get(username=req.user.username)# lấy ra dữ liệu trong User có tên giống tài khoản đang đăng nhập
        except ObjectDoesNotExist:
            return -1


class Home(View):
    def get(self, req):
        user_ = get_user(req)
        if user_ == -1:
            render(req, 'Hub/error.html', {"error": 'tài khoản đăng ký lỗi'})

        post_ = Post.objects.all()  # lấy toàn bộ model Post
        context = {"user_": user_, "posts": post_,
                   "media_url": settings.MEDIA_URL}  # tạo 1 biến lưu dữ liệu truyền vào file html
        return render(req, 'Hub/home.html', context)

    def post(self, req):
        arr = []
        user_ = get_user(req)
        if user_ == -1:
            render(req, 'Hub/error.html', {"error": 'tài khoản đăng ký lỗi'})

        search = req.POST.get('search').lower().strip()
        post_ = Post.objects.all()
        for i in range(len(post_)):
            if post_[i].title.lower().strip().find(search) != -1:
                arr.append(post_[i])
        return render(req, 'Hub/search.html', {
            "user_": user_,
            "posts": arr,
            "search": search,
            "len": len(arr),
            "media_url": settings.MEDIA_URL})


def home(req):                                                  # một hàm xử lý trang chủ
    arr = []
    user_ = get_user(req)                                                  # tạo 1 con trỏ để
    if user_ == -1:
        render(req, 'Hub/error.html', {"error": 'tài khoản đăng ký lỗi'})

    if req.method == 'POST':  # nếu như thông điệp là POST
        search = req.POST.get('search').lower().strip()
        post_ = Post.objects.all()
        for i in range(len(post_)):
            if post_[i].title.lower().strip().find(search) != -1:
                arr.append(post_[i])
        return render(req, 'Hub/search.html', {
            "user_": user_,
            "posts": arr,
            "search": search,
            "len": len(arr),
            "media_url": settings.MEDIA_URL})
    post_ = Post.objects.all()                                  # lấy toàn bộ model Post
    context = {"user_": user_, "posts": post_, "media_url": settings.MEDIA_URL}# tạo 1 biến lưu dữ liệu truyền vào file html
    return render(req, 'Hub/home.html', context)                # trả về thông điệp http với tham số là template và dữ liệu truyền vào


def login_view(req):                                            # đăng nhập
    if req.method == 'POST':                                    # nếu như thông điệp là POST
        username = req.POST.get('username')                     # lấy username
        password = req.POST.get('password')                     # lấy pass
        user = authenticate(req, username=username, password=password)  # tạo một tài khoản
        if user is None:                                        # nếu tài khoản này lỗi
            return render(req, 'Hub/login.html', {'error': 'username or password wrong'})
        login(req, user)
        return HttpResponseRedirect('/')
    if req.user.username:
        return HttpResponseRedirect('/')
    return render(req, 'Hub/login.html', {'error': ''})


def register(req):
    if req.user.username:
        return HttpResponseRedirect('/')
    form = RegistrationForm()
    if req.method == 'POST':
        form = RegistrationForm(req.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/login')
    return render(req, 'Hub/register.html', {'form': form})


def logout_view(req):
    logout(req)
    return HttpResponseRedirect('/')


def change_information(req):
    if not req.user.username:
        return HttpResponseRedirect('/')
    user_ = ''
    if req.user.username:
        try:
            user_ = User.objects.get(username=req.user.username)
        except ObjectDoesNotExist:
            return render(req, 'Hub/error.html', {"error": 'tài khoản đăng ký lỗi'})

    if req.method == 'POST':
        form = ChangeInformationForm(req.POST, req.FILES or None, instance=user_)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/')
    else:
        form = ChangeInformationForm(instance=user_)
    return render(req, 'Hub/change_information.html', {'form': form, 'user_': user_, "media_url": settings.MEDIA_URL})


def create(req):
    if not req.user.username:
        return HttpResponseRedirect('/')
    if req.method == 'POST':
        print(req)
    return render(req, 'Hub/create.html')


def post(req, id):
    user_ = ''
    if req.user.username:
        try:
            user_ = User.objects.get(username=req.user.username)
        except ObjectDoesNotExist:
            return render(req, 'Hub/error.html', {"error": 'tài khoản đăng ký lỗi'})
    post_ = Post.objects.get(id=id)
    steps = Step.objects.filter(post_id=post_)

    views = View.objects.filter(date=date.today(), post_id=post_)
    if len(views) == 0:
        v = View()
        v.count = 1
        v.post_id = post_
        v.save()
    else:
        views[0].count += 1
        views[0].save()

    lk = ''
    lk_num = ''
    if req.user.username:
        if req.method == 'POST':
            c = Comment()
            c.body = req.POST.get('cmt')
            c.user_id = user_
            c.post_id = post_
            c.save()

        lk = Like.objects.filter(post_id=post_.id, user_id=user_.id).exists()
        lk_num = Like.objects.filter(post_id=post_.id).count()

    cmt = Comment.objects.filter(post_id=post_)
    context = {
        "user_": user_,
        "post": post_,
        "steps": steps,
        "like": lk,
        "like_num": lk_num,
        "comments": cmt,
        "media_url": settings.MEDIA_URL
    }
    return render(req, 'Hub/post.html', context)


def like(req, id, user_id, next):
    if req.user.username:
        try:
            user_ = User.objects.get(id=user_id).username
        except ObjectDoesNotExist:
            return render(req, 'Hub/error.html', {"error": 'đường dẫn sai'})
    else:
        return HttpResponseRedirect('/login')

    if user_ != req.user.username:
        return render(req, 'Hub/error.html', {"error": 'đăng nhập sai'})
    else:
        try:
            obj = Like.objects.filter(post_id=id, user_id=user_id)
            if obj.exists():
                obj.delete()
                return HttpResponseRedirect('/' + next)
            else:
                lk = Like()
                lk.user_id = User.objects.get(id=user_id)
                lk.post_id = Post.objects.get(id=id)
                lk.save()

                return HttpResponseRedirect('/' + next)
        except ObjectDoesNotExist:
            return render(req, 'Hub/error.html', {"error": 'tài khoản đăng ký lỗi'})
