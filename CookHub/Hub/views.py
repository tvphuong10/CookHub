from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.conf import settings
from .models import User, Post
from  .forms import RegistrationForm

# Create your views here.


def home(req):
    user_ = ''
    if req.user.username:
        user_ = User.objects.get(username=req.user.username)
    post_ = Post.objects.all()
    context = {"user_": user_, "posts": post_, "media_url": settings.MEDIA_URL}
    return render(req, 'Hub/home.html', context)


def login_view(req):
    if req.method == 'POST':
        username = req.POST.get('username')
        password = req.POST.get('password')
        user = authenticate(req, username=username, password=password)
        if user is None:
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
