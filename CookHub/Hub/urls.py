from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home), # tạo đường dẫn mặc định (trống) về home
    path('home', views.Home.as_view()),
    path('login/', views.login_view), # tạo đường dẫn login
    path('logout/', views.logout_view), # tương tự
    path('register/', views.register),
    path('create/', views.create),
    path('<int:id>', views.post),
    path('user/', views.change_information),
    path('like-post/<int:id>/<int:user_id>/<slug:next>', views.like)
]
