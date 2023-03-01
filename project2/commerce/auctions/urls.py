from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("add_listing", views.add_listing, name="add_listing"),
    path("listing/<str:listing_id>", views.listing, name="listing"),
    path("comment", views.comment, name="comment"),
    path("bid", views.bid, name="bid"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("close_listing", views.close_listing, name="close_listing"),
    path("category/<str:category>", views.category_view, name="category_view"),
    path("categories", views.categories, name="categories")
]
