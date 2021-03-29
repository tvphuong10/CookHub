from django.db import models


class User(models.Model): # lưu các thông tin bổ xung của user
    username = models.CharField(max_length=150)
    sign = models.CharField(max_length=200)
    image = models.ImageField(null=True, blank=True, upload_to="images/")


class Post(models.Model): # lưu bài viết
    image = models.ImageField(null=True, blank=True, upload_to="images/")
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=300)
    material = models.CharField(max_length=300)
    view = models.IntegerField
    like = models.IntegerField
    date = models.DateTimeField
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)


class Comment(models.Model): # lưu bình luận
    body = models.CharField(max_length=400)
    date = models.DateTimeField
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    post_id = models.ForeignKey(Post, on_delete=models.CASCADE)


class Step(models.Model): # lưu các bước làm
    body = models.CharField(max_length=300)
    image = models.ImageField(null=True, blank=True, upload_to="images/")
    post_id = models.ForeignKey(Post, on_delete=models.CASCADE)

class Like(models.Model): # lưu các lượt thích
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    post_id = models.ForeignKey(Post, on_delete=models.CASCADE)