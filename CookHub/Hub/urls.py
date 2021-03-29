from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home),
    path('login/', views.login_view),
    path('logout/', views.logout_view),
    path('register/', views.register)
]
