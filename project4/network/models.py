from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    followings = models.ManyToManyField("self", symmetrical=False, related_name="followers")

class Post(models.Model):
    poster = models.ForeignKey(User, related_name="posts", on_delete=models.CASCADE)
    content = models.TextField(max_length=500)
    add_date = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User)