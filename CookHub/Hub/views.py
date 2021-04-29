from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout, decorators
from django.conf import settings
from .models import *
from .forms import RegistrationForm, ChangeInformationForm
from django.core.exceptions import ObjectDoesNotExist
from datetime import date
from django.views import View as ViewBase
from plotly.offline import plot
from plotly.graph_objs import Scatter

# req là thông điệp từ client truyền vào


def get_user(req):
    if req.user.username:                                       # nếu như có tên tài khoản (tức đã đăng nhập)
        try:
            return User.objects.get(username=req.user.username)# lấy ra dữ liệu trong User có tên giống tài khoản đang đăng nhập
        except ObjectDoesNotExist:
            return -1
    return 0


class HomeView(ViewBase):
    def get(self, req):
        user_ = get_user(req)
        if user_ == -1:
            return render(req, 'Hub/error.html', {"error": 'tài khoản đăng ký lỗi'})

        offer_ = Offer.objects.all()
        users = User.objects.all()
        post_ = Post.objects.all()  # lấy toàn bộ model Post
        context = {"user_": user_, "posts": post_, "offers": offer_, 'users': users,
                   "media_url": settings.MEDIA_URL}  # tạo 1 biến lưu dữ liệu truyền vào file html
        return render(req, 'Hub/home.html', context)

    def post(self, req):
        arr = []
        user_ = get_user(req)
        if user_ == -1:
            return render(req, 'Hub/error.html', {"error": 'tài khoản đăng ký lỗi'})

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


class LoginView(ViewBase):
    def get(self, req):
        if req.user.username:
            return HttpResponseRedirect('/')
        return render(req, 'Hub/login.html', {'error': ''})

    def post(self, req):
        username = req.POST.get('username')  # lấy username
        password = req.POST.get('password')  # lấy pass
        user = authenticate(req, username=username, password=password)
        if user is None:  # nếu tài khoản này lỗi
            return render(req, 'Hub/login.html', {'error': 'username or password wrong'})
        login(req, user)
        return HttpResponseRedirect('/')


class RegisterView(ViewBase):
    def get(self, req):
        form = RegistrationForm()
        if req.user.username:
            return HttpResponseRedirect('/')
        return render(req, 'Hub/register.html', {'form': form})

    def post(self, req):
        form = RegistrationForm(req.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/login')
        return render(req, 'Hub/register.html', {'form': form})


def logout_view(req):
    logout(req)
    return HttpResponseRedirect('/')


class EditProfile(ViewBase):
    def get(self, req):
        user_ = get_user(req)
        if user_ == -1 or user_ == 0:
            return render(req, 'Hub/error.html', {"error": 'tài khoản đăng ký lỗi'})
        form = ChangeInformationForm(instance=user_)
        post_ = Post.objects.filter(user_id=user_)
        mess = Messenger.objects.filter(user_receive=user_)
        return render(req, 'Hub/change_information.html',
                      {'form': form, 'user_': user_, 'posts': post_, 'mess': mess, "media_url": settings.MEDIA_URL})

    def post(self, req):
        user_ = get_user(req)
        if user_ == -1 or user_ == 0:
            return render(req, 'Hub/error.html', {"error": 'tài khoản đăng ký lỗi'})
        form = ChangeInformationForm(req.POST, req.FILES or None, instance=user_)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/')

class EditPost(ViewBase):
    def get(self, req, id):
        user_ = get_user(req)
        if user_ == -1 or user_ == 0:
            return render(req, 'Hub/error.html', {"error": 'tài khoản đăng ký lỗi'})
        form = ChangeInformationForm(instance=user_)
        post_ = Post.objects.get(id=id)
        steps = Step.objects.filter(post_id=post_)
        return render(req, 'Hub/edit_post.html', {"post": post_, "steps": steps})

def create(req):
    if not req.user.username:
        return HttpResponseRedirect('/')
    if req.method == 'POST':
        print(req)
    return render(req, 'Hub/create.html')


class PostView(ViewBase):
    @staticmethod
    def increase_view(post_):
        views = View.objects.filter(date=date.today(), post_id=post_)
        if len(views) == 0:
            v = View()
            v.count = 1
            v.post_id = post_
            v.save()
        else:
            views[0].count += 1
            views[0].save()

    def get(self, req, id):
        user_ = get_user(req)
        if user_ == -1:
            return render(req, 'Hub/error.html', {"error": 'tài khoản đăng ký lỗi'})
        post_ = Post.objects.get(id=id)
        self.increase_view(post_)
        lk = ''
        if user_ != 0:
            lk = Like.objects.filter(post_id=post_.id, user_id=user_.id).exists()

        steps = Step.objects.filter(post_id=post_)
        lk_num = Like.objects.filter(post_id=post_.id).count()
        cmt = Comment.objects.filter(post_id=post_)
        offers = Post.objects.filter(user_id=post_.user_id)
        enable_edit = False;
        if post_.user_id == user_:
            enable_edit = True

        context = {
            "user_": user_,
            "post": post_,
            "steps": steps,
            "like": lk,
            "like_num": lk_num,
            "comments": cmt,
            "offers": offers,
            "enable_edit": enable_edit,
            "media_url": settings.MEDIA_URL
        }
        return render(req, 'Hub/post.html', context)

    def post(self, req, id):
        user_ = get_user(req)
        post_ = Post.objects.get(id=id)
        if user_ == 0:
            return render(req, 'Hub/error.html', {"error": 'chưa đăng nhập'})
        c = Comment()
        c.body = req.POST.get('cmt')
        c.user_id = user_
        c.post_id = post_
        c.save()
        return HttpResponseRedirect('/' + str(id))


@decorators.login_required(login_url='/login/')
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


class Report(ViewBase):
    def get(self, req, id):
        user_ = get_user(req)
        if user_ == -1 or user_ == 0:
            return render(req, 'Hub/error.html', {"error": 'tài khoản đăng ký lỗi'})

        return render(req, 'Hub/report.html', {"user_": user_, "media_url": settings.MEDIA_URL})

    def post(self, req, id):
        user_ = get_user(req)
        if user_ == -1 or user_ == 0:
            return render(req, 'Hub/error.html', {"error": 'tài khoản đăng ký lỗi'})

        post_ = Post.objects.get(id=id)
        user2_ = post_.user_id
        body = req.POST.get('report')
        messenger = Messenger()
        messenger.post_id = post_.id
        messenger.user_receive = user2_
        messenger.user_send = user_
        messenger.body = body
        messenger.save()

        return HttpResponseRedirect('/')


class Notifications(ViewBase):
    def get(self, req):
        user_ = get_user(req)
        if user_ == -1 or user_ == 0:
            return render(req, 'Hub/error.html', {"error": 'tài khoản đăng ký lỗi'})

        mess = Messenger.objects.filter(user_receive=user_)
        return render(req, 'Hub/notifications.html',
                      {"user_": user_, 'mess': mess, "media_url": settings.MEDIA_URL})


class User_page(ViewBase):
    def get(self, req, id):
        user_ = get_user(req)
        if user_ == -1:
            return render(req, 'Hub/error.html', {"error": 'tài khoản đăng ký lỗi'})

        user2 = User.objects.get(id=id)
        guess = req.user.username != user2.username
        form = ''
        if user_ != 0:
            form = ChangeInformationForm(instance=user_)
        post_ = Post.objects.filter(user_id=user2)
        post_count = len(post_)
        like_count = 0
        view_count = 0
        for p in post_:
            like_count += len(Like.objects.filter(post_id=p))
            views = View.objects.filter(post_id=p)
            for v in views:
                view_count += v.count

        return render(req, 'Hub/user_page.html',
                      {'form': form,
                       'user_': user_,
                       'user2': user2,
                       'posts': post_,
                       'guess': guess,
                       'post_count': post_count,
                       'like_count': like_count,
                       'view_count': view_count,
                       "media_url": settings.MEDIA_URL})


class AdminSite(ViewBase):
    def get(self, req):
        user_ = get_user(req)
        if user_ == -1 or user_ == 0:
            return render(req, 'Hub/error.html', {"error": 'tài khoản đăng ký lỗi'})

        post_ = Post.objects.get(id=1)
        view_ = View.objects.filter(post_id=post_)
        x = []
        y = []

        for v in view_:
            y.append(v.count)
            x.append(v.date.strftime('%m/%d/%Y'))

        lk_num = Like.objects.filter(post_id=post_).count()
        cmt_num = Comment.objects.filter(post_id=post_).count()
        plot_div = plot([Scatter(x=x, y=y,
                                 mode='lines', name='test',
                                 opacity=0.8)],
                        output_type='div')
        context = {"user_": user_,
                   "select": 0,
                   "post": post_,
                   "like_num": lk_num,
                   "comment_num": cmt_num,
                   "img_data": plot_div,
                   "media_url": settings.MEDIA_URL}
        return render(req, 'Hub/admin_site.html', context)


class AdminNotifications(ViewBase):
    def get(self, req):
        user_ = get_user(req)
        if user_ == -1 or user_ == 0:
            return render(req, 'Hub/error.html', {"error": 'tài khoản đăng ký lỗi'})

        mess = Messenger.objects.all()
        return render(req, 'Hub/admin_notifications.html',
                      {"user_": user_,
                       "mess": mess,
                       "select": 1,
                       "media_url": settings.MEDIA_URL})


class AdminPostsManager(ViewBase):
    def get(self, req):
        user_ = get_user(req)
        if user_ == -1 or user_ == 0:
            return render(req, 'Hub/error.html', {"error": 'tài khoản đăng ký lỗi'})

        return render(req, 'Hub/admin_manager.html',
                      {"user_": user_,
                       "select": 2,
                       "media_url": settings.MEDIA_URL})


class AdminPost(ViewBase):
    def get(self, req, id):
        user_ = get_user(req)
        if user_ == -1 or user_ == 0:
            return render(req, 'Hub/error.html', {"error": 'tài khoản đăng ký lỗi'})

        post_ = Post.objects.get(id=id)
        view_ = View.objects.filter(post_id=post_)
        x = []
        y = []

        for v in view_:
            y.append(v.count)
            x.append(v.date.strftime('%m/%d/%Y'))

        lk_num = Like.objects.filter(post_id=post_).count()
        views = View.objects.filter(post_id=post_)
        view = 0
        for v in views:
            view += v.count
        comments = Comment.objects.filter(post_id=post_)
        plot_div = plot([Scatter(x=x, y=y,
                                 mode='lines', name='test',
                                 opacity=0.8)],
                        output_type='div')

        return render(req, 'Hub/admin_post.html',
                      {"user_": user_,
                       "select": 3,
                       "post": post_,
                       "comments": comments,
                       "view_num": view,
                       "like_num": lk_num,
                       "img_data": plot_div,
                       "media_url": settings.MEDIA_URL})