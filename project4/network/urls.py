
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("following", views.following, name="following"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("add_post", views.add_post, name="add_post"),
    path("edit_post", views.edit_post, name="edit_post"),
    path("like_post", views.like_post, name="like_post"),
    path("users/<str:id>", views.user_profile, name="user-profile"),
    path("users/<str:id>/follow", views.follow_user, name="follow_user"),

]
