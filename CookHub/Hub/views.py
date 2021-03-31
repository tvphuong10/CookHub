from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.conf import settings
from .models import User, Post
from .forms import RegistrationForm
from django.core.exceptions import ObjectDoesNotExist

# req là thông điệp từ client truyền vào


def home(req):                                                  # một hàm xử lý trang chủ
    user_ = ''                                                  # tạo 1 con trỏ để
    if req.user.username:                                       # nếu như có tên tài khoản (tức đã đăng nhập)
        try:
            user_ = User.objects.get(username=req.user.username)# lấy ra dữ liệu trong User có tên giống tài khoản đang đăng nhập
        except ObjectDoesNotExist:
            return render(req, 'Hub/error.html', {"error": 'tài khoản đăng ký lỗi'})
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
        login(req, user)                                        # lưu tài khoản
        return HttpResponseRedirect('/')                        # về trang chủ
    if req.user.username:                                       # nếu đã đăng nhập r
        return HttpResponseRedirect('/')                        # về trang chủ
    return render(req, 'Hub/login.html', {'error': ''})         # truyền vào file login.html với dữ liệu


def register(req):                                              # đăng ký
    if req.user.username:                                       # nếu đã đăng nhập
        return HttpResponseRedirect('/')                        # về trang chủ
    form = RegistrationForm()                                   # tạo 1 form đang ký trong form.py
    if req.method == 'POST':                                    # nếu thông điệp là POST
        form = RegistrationForm(req.POST)                       # đưa thông điệp đó vào trong form
        if form.is_valid():                                     # nếu như form đã được khởi tạo trước đó
            form.save()                                         # gọi hàm save
            return HttpResponseRedirect('/login')               # trả về đăng nhập
    return render(req, 'Hub/register.html', {'form': form})     # trả về html register.html với form truyền vào


def logout_view(req):                                           # đăng xuất
    logout(req)                                                 # gọi hàm đăng xuất(viết sẵn)
    return HttpResponseRedirect('/')                            # về trang chủ
