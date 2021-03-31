from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home), # tạo đường dẫn mặc định (trống) về home
    path('login/', views.login_view), # tạo đường dẫn login
    path('logout/', views.logout_view), # tương tự
    path('register/', views.register)
]
