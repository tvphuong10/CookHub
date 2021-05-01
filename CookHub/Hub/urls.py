from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.HomeView.as_view()), # tạo đường dẫn mặc định (trống) về home
    path('home', views.HomeView.as_view()),
    path('login/', views.LoginView.as_view()), # tạo đường dẫn login
    path('forgot_password/', views.ForgotPassword.as_view()),
    path('logout/', views.logout_view), # tương tự
    path('register/', views.RegisterView.as_view()),
    path('create/', views.create),
    path('<int:id>', views.PostView.as_view()),
    path('user_edit/', views.EditProfile.as_view()),
    path('like-post/<int:id>/<int:user_id>/<slug:next>', views.like),
    path('edit/<int:id>', views.EditPost.as_view()),
    path('report/<int:id>', views.Report.as_view()),
    path('notification/', views.Notifications.as_view()),
    path('user_page/<int:id>', views.User_page.as_view()),
    path('admin_site/', views.AdminSite.as_view()),
    path('admin_notify/', views.AdminNotifications.as_view()),
    path('admin_manager/', views.AdminPostsManager.as_view()),
    path('admin_post/<int:id>', views.AdminPost.as_view()),
]
