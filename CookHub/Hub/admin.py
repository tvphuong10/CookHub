from django.contrib import admin
from .models import User, Post, Comment, Step, Like, View
# Register your models here.

admin.site.register(User)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Step)
admin.site.register(Like)
admin.site.register(View)
