from django.db import models


class User(models.Model): # lưu các thông tin bổ xung của user
    username = models.CharField(max_length=150)
    sign = models.CharField(max_length=200)
    image = models.ImageField(null=True, blank=True, upload_to="images/")

    def __str__(self):
        return self.username


class Post(models.Model): # lưu bài viết
    image = models.ImageField(null=True, blank=True, upload_to="images/")
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=300)
    material = models.CharField(max_length=300)
    views = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Comment(models.Model): # lưu bình luận
    body = models.CharField(max_length=400)
    date = models.DateTimeField(auto_now_add=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    post_id = models.ForeignKey(Post, on_delete=models.CASCADE)

    def __str__(self):
        return self.body


class Step(models.Model): # lưu các bước làm
    body = models.CharField(max_length=300)
    image = models.ImageField(null=True, blank=True, upload_to="images/")
    post_id = models.ForeignKey(Post, on_delete=models.CASCADE)

    def __str__(self):
        return self.body


class Like(models.Model): # lưu các lượt thích
    date = models.DateField(auto_now_add=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    post_id = models.ForeignKey(Post, on_delete=models.CASCADE)

    def __str__(self):
        return self.date


class View(models.Model):
    count = models.IntegerField(default=0)
    date = models.DateField(auto_now_add=True)
    post_id = models.ForeignKey(Post, on_delete=models.CASCADE)

    def __str__(self):
        return self.date

