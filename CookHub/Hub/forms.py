from django import forms
import re
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from .models import User as User_


class RegistrationForm(forms.Form):  # form đăng ký tài khoản mới
    username = forms.CharField(label='User name', max_length=30)
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput())
    password2 = forms.CharField(label='Password (retype)', widget=forms.PasswordInput())

    def clean_password2(self): # kiểm tra mật khẩu nhập lại
        if 'password1' in self.cleaned_data:
            password1 = self.cleaned_data['password1']
            password2 = self.cleaned_data['password2']
            if password1 == password2 and password1:
                return password2
        raise forms.ValidationError("password retype incorrect")

    def clean_username(self): # kiểm tra tên đăng nhập tồn tại chưa
        username = self.cleaned_data['username']
        if not re.search(r'^\w+$', username):
            raise forms.ValidationError("username has invalid character")
        try:
            User.objects.get(username=username)
        except ObjectDoesNotExist:
            return username
        raise forms.ValidationError("Username already exist")

    def save(self): # lưu tài khoản vào cơ sở dữ liệu
        User.objects.create_user(username=self.cleaned_data['username'], password=self.cleaned_data['password1'])
        u = User_()
        u.username = self.cleaned_data['username']
        u.sign = ''
        u.save()


class ChangeInformationForm(forms.ModelForm):
    class Meta:
        model = User_
        fields = ['sign', 'image']


class Create(forms.Form):
    title = forms.CharField(label='Title', max_length=100)
    image = forms.ImageField(label='Image', allow_empty_file=True)
    description = forms.CharField(label='Description', max_length=300)
    material = forms.CharField(label='material', max_length=300)

