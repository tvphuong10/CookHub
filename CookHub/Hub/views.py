from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth import authenticate, login, logout, decorators
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import pandas as pd
from .models import *
from .forms import RegistrationForm, ChangeInformationForm
from django.core.exceptions import ObjectDoesNotExist
from datetime import date, timedelta
from django.views import View as ViewBase
from plotly.offline import plot
from plotly.graph_objs import Scatter
import plotly.express as px
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
        post_ = Post.objects.all()
        like_offer = []
        like_post = []
        for o in offer_:
            if user_ != 0:
                like_offer.append(Like.objects.filter(post_id=o.post_id, user_id=user_.id).exists())
            else:
                like_offer.append('')
        for p in post_:
            if user_ != 0:
                like_post.append(Like.objects.filter(post_id=p, user_id=user_.id).exists())  # lấy toàn bộ model Post
            else:
                like_post.append('')

        context = {"user_": user_,
                   "posts_zip": zip(post_, like_post),
                   "offers_zip": zip(offer_, like_offer),
                   'users': users,
                   "media_url": settings.MEDIA_URL}  # tạo 1 biến lưu dữ liệu truyền vào file html
        return render(req, 'Hub/home.html', context)

    def post(self, req):
        search = req.POST.get('search').lower().strip()
        if search == "":
            return HttpResponseRedirect("/")
        return HttpResponseRedirect('search/' + urllib.parse.quote(search))


class HomeView2(ViewBase):
    def get(self, req):
        user_ = get_user(req)
        if user_ == -1:
            return render(req, 'Hub/error.html', {"error": 'tài khoản đăng ký lỗi'})

        offer_ = Offer.objects.all()
        users = User.objects.all()[:3]
        post_ = Post.objects.all()


        x = []
        y = []
        z = []

        for day in range(20):
            for i in range(3):
                x.append(date.today() - timedelta(days=day))
                v =View.objects.filter(post_id=offer_[i].post_id, date=date.today() - timedelta(days=day))
                count = 0
                for v_ in v:
                    count += v_.count

                y.append(count)
                z.append(offer_[i].post_id.title)

        fig = px.line({"day": x, "view": y, "post": z}, x="day", y="view", color='post',
                      template="plotly_dark")

        plot_div = plot(fig, output_type='div')

        return render(req, 'Hub/test.html', {
            "user_": user_,
            "offer_first": offer_[0],
            "offers": offer_[1:],
            "img_data": plot_div,
            "posts": post_,
            "users": users,
            "media_url": settings.MEDIA_URL
        })

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
        if req.method == 'POST':
            print(1 + req)
        return render(req, 'Hub/edit_post.html', {
            "user_": user_,
            "post": post_,
            "steps": zip(steps, range(1, len(steps) + 1)),
            "len": len(steps),
            "media_url": settings.MEDIA_URL
        })


def create(req):
    user_ = get_user(req)
    if user_ == -1 or user_ == 0:
        return render(req, 'Hub/error.html', {"error": 'tài khoản đăng ký lỗi'})

    if req.method == 'POST':
        new_post = Post()
        new_post.user_id = user_
        new_post.title = req.POST.get('dish')
        new_post.description = req.POST.get('des')
        new_post.image = req.FILES['image']
        new_post.material = req.POST.get('textField')
        new_post.save()

        num_step = req.POST.get('numberStep')
        for n in range(int(num_step)):
            new_step = Step()
            new_step.post_id = new_post
            new_step.body = req.POST.get('recipe' + str(n + 1))
            new_step.image = req.FILES.get('anh' + str(n + 1))
            new_step.save()

        id = Post.objects.latest('id').id
        return HttpResponseRedirect('/' + str(id))
    return render(req, 'Hub/create_post.html', {
        "user_": user_,
        "media_url": settings.MEDIA_URL})


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
        is_liked = []

        if user_ != 0:
            for o in offers:
                is_liked.append(Like.objects.filter(post_id=o, user_id=user_.id).exists())

        enable_edit = False
        if post_.user_id == user_:
            enable_edit = True

        context = {
            "user_": user_,
            "post": post_,
            "steps": steps,
            "like": lk,
            "like_num": lk_num,
            "comments": cmt,
            "offers_zip": zip(is_liked, offers),
            "enable_edit": enable_edit,
            "media_url": settings.MEDIA_URL
        }
        return render(req, 'Hub/post.html', context)


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


def like(req):
    if req.is_ajax and req.method == "POST":
        u_id = req.POST.get("user_id", None)
        p_id = req.POST.get("post_id", None)
        user_ = User.objects.get(id=u_id)
        post_ = Post.objects.get(id=p_id)

        obj = Like.objects.filter(post_id=post_, user_id=user_)
        if obj.exists():
            obj.delete()
            count = len(Like.objects.filter(post_id=post_))
            return JsonResponse({"valid": False, "len": count}, status=200)
        else:
            lk = Like()
            lk.user_id = user_
            lk.post_id = post_
            lk.save()
            count = len(Like.objects.filter(post_id=post_))
            return JsonResponse({"valid": True, "len": count}, status=200)

    return JsonResponse({}, status=400)


def comment(req):
    if req.is_ajax and req.method == "POST":
        u_id = req.POST.get("user_id", None)
        p_id = req.POST.get("post_id", None)
        body = req.POST.get("body", None)
        user_ = User.objects.get(id=u_id)
        post_ = Post.objects.get(id=p_id)
        print(body)

        cmt = Comment()
        cmt.user_id = user_
        cmt.post_id = post_
        cmt.body = body
        cmt.save()
        return JsonResponse({"valid": True}, status=200)
    return JsonResponse({}, status=400)


def test(req):
    x = [1, 2, 3, 4, 5, 1, 2, 3, 4, 5]
    y = [2, 4, 3, 0, 6, 4, 3, 4, 4, 4]
    z = ["t", "t", "t", "t", "t", "n", "n", "n", "n", "n"]
    fig = px.line({"day": x, "view": y, "post": z}, x="day", y="view", color='post',
                     template="plotly_dark")

    plot_div = plot(fig, output_type='div')

    return render(req, 'Hub/test.html', {"img_data": plot_div})
