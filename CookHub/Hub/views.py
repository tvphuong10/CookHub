from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout, decorators
from django.conf import settings
from .models import *
from .forms import RegistrationForm, ChangeInformationForm
from django.core.exceptions import ObjectDoesNotExist
from datetime import date, timedelta
from django.views import View as ViewBase
from plotly.offline import plot
from plotly.graph_objs import Scatter
import urllib.parse

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
        search = req.POST.get('search').lower().strip()
        if search == "":
            return HttpResponseRedirect("/")
        return HttpResponseRedirect('search/' + urllib.parse.quote(search))


class Search(ViewBase):
    def get(self, req, search):
        user_ = get_user(req)
        if user_ == -1:
            return render(req, 'Hub/error.html', {"error": 'tài khoản đăng ký lỗi'})

        posts = []
        s = urllib.parse.unquote(search)
        post_ = Post.objects.all()
        for i in range(len(post_)):
            if post_[i].title.lower().strip().find(s) != -1:
                posts.append(post_[i])

        return render(req, 'Hub/search.html', {
            "user_": user_,
            "posts": posts,
            "search": s,
            "len": len(posts),
            "media_url": settings.MEDIA_URL})

    def post(self, req, search):
        s = req.POST.get('search').lower().strip()
        if s == "":
            return HttpResponseRedirect("/")
        return HttpResponseRedirect(urllib.parse.quote(s))


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


class ForgotPassword(ViewBase):
    def get(self,req):
        if req.user.username:
            return HttpResponseRedirect('/')
        return render(req, 'Hub/forgot_pass.html', {'error': ''})


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


def pretty_request(request):
    headers = ''
    for header, value in request.META.items():
        if not header.startswith('HTTP'):
            continue
        header = '-'.join([h.capitalize() for h in header[5:].lower().split('_')])
        headers += '{}: {}\n'.format(header, value)

    return (
        '{method} HTTP/1.1\n'
        'Content-Length: {content_length}\n'
        'Content-Type: {content_type}\n'
        '{headers}\n\n'
        '{body}'
    ).format(
        method=request.method,
        content_length=request.META['CONTENT_LENGTH'],
        content_type=request.META['CONTENT_TYPE'],
        headers=headers,
        body=request.body,
    )


def create(req):
    if not req.user.username:
        return HttpResponseRedirect('/')

    #print(req)
    if req.method == 'POST':
        return pretty_request(req)
    return render(req, 'Hub/create_post.html')


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

        total_view = 0
        total_like = Like.objects.filter().count()
        post_ = Post.objects.get(id=1)
        view_ = View.objects.filter(post_id=post_)
        x = []
        y = []

        for day in range(20):
            x.append(date.today() - timedelta(days=day))
            v = View.objects.filter(date=date.today() - timedelta(days=day))
            view = 0
            for v_ in v:
                view += v_.count

            total_view += view
            y.append(view)

        lk_num = []
        view_num = []
        posts = Offer.objects.all()
        for p in posts:
            lk_num.append(Like.objects.filter(post_id=p.post_id).count())
            view_ = View.objects.filter(post_id=p.post_id)
            v = 0
            for i in view_:
                v += i.count
            view_num.append(v)

        plot_div = plot([Scatter(x=x, y=y,
                                 mode='lines', name='test',
                                 opacity=0.8)],
                        output_type='div')
        context = {"user_": user_,
                   "select": 0,
                   "post": post_,
                   "total_like": total_like,
                   "total_view": total_view,
                   "posts": zip(posts, lk_num, view_num),
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

        posts = Post.objects.all()
        lk_num = []
        view_num = []
        for p in posts:
            lk_num.append(Like.objects.filter(post_id=p).count())
            view_ = View.objects.filter(post_id=p)
            v = 0
            for i in view_:
                v += i.count
            view_num.append(v)

        return render(req, 'Hub/admin_manager.html',
                      {"user_": user_,
                       "posts": zip(posts, lk_num, view_num),
                       "len": len(posts),
                       "select": 2,
                       "media_url": settings.MEDIA_URL})

    def post(self, req):
        search = req.POST.get('search').lower().strip()
        if search == "":
            return HttpResponseRedirect("/admin_manager")
        return HttpResponseRedirect('search/' + urllib.parse.quote(search))


class AdminSearch(ViewBase):
    def get(self, req, search):
        user_ = get_user(req)
        if user_ == -1 or user_ == 0:
            return render(req, 'Hub/error.html', {"error": 'tài khoản đăng ký lỗi'})

        posts =[]
        s = urllib.parse.unquote(search)
        post_ = Post.objects.all()
        for i in range(len(post_)):
            if post_[i].title.lower().strip().find(s) != -1:
                posts.append(post_[i])

        lk_num = []
        view_num = []
        for p in posts:
            lk_num.append(Like.objects.filter(post_id=p).count())
            view_ = View.objects.filter(post_id=p)
            v = 0
            for i in view_:
                v += i.count
            view_num.append(v)
        return render(req, 'Hub/admin_manager.html', {
            "user_": user_,
            "posts": zip(posts, lk_num, view_num),
            "src": True,
            "len": len(posts),
            "search": s,
            "select": 2,
            "media_url": settings.MEDIA_URL})

    def post(self, req, search):
        s = req.POST.get('search').lower().strip()
        if s == "":
            return HttpResponseRedirect("/admin_manager")
        return HttpResponseRedirect(urllib.parse.quote(s))


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

    def post(self, req, id):
        user_ = get_user(req)
        if user_ == -1 or user_ == 0:
            return render(req, 'Hub/error.html', {"error": 'tài khoản đăng ký lỗi'})

        post_ = Post.objects.get(id=id)
        type = req.POST.get('send')
        if type == "Send":
            user2_ = post_.user_id
            body = req.POST.get('message')
            messenger = Messenger()
            messenger.post_id = post_.id
            messenger.user_receive = user2_
            messenger.user_send = user_
            messenger.body = body
            messenger.save()
        elif type == "Offer":
            lg = len(Offer.objects.all())
            if lg >= 4:
                first = Offer.objects.first()
                first.delete()

            new_offer = Offer()
            new_offer.post_id = post_
            new_offer.save()
        else:
            steps = Step.objects.filter(post_id=post_)
            for s in steps:
                s.delete()
            post_.delete()
            return HttpResponseRedirect('admin_manager/')
        return HttpResponseRedirect(str(id))
