from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("wiki/<str:entry>", views.article, name="article"),
    path("search", views.search, name="search"),
    path("random", views.random_page, name="random"),
    path("new", views.new_page, name="new"),
    path("wiki/<str:entry>/edit", views.edit_page, name="edit")
]
