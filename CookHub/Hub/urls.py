from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.HomeView.as_view()), # tạo đường dẫn mặc định (trống) về home
    path('home', views.HomeView.as_view()),
    path('login/', views.LoginView.as_view()), # tạo đường dẫn login
    path('logout/', views.logout_view), # tương tự
    path('register/', views.RegisterView.as_view()),
    path('create/', views.create),
    path('<int:id>', views.PostView.as_view()),
    path('user/', views.EditProfile.as_view()),
    path('like-post/<int:id>/<int:user_id>/<slug:next>', views.like),
    path('edit/<int:id>', views.EditPost.as_view())
]
