from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Listing(models.Model):
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=512)
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2)
    img_url = models.URLField(blank=True, verbose_name="Image URL")
    category = models.CharField(max_length=32, blank=True)
    add_date = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    creator = models.ForeignKey(User, related_name="listings", on_delete=models.PROTECT)
    watchers = models.ManyToManyField(User, blank=True, related_name="watchlist", null=True)

    def __str__(self):
        return f"{self.title}: {self.description}"                  


class Bid(models.Model):
    bid = models.DecimalField(max_digits=10, decimal_places=2)
    listing = models.ForeignKey(Listing, related_name="bids",on_delete=models.PROTECT)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    add_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.bid}"


class Comment(models.Model):
    comment = models.CharField(max_length=250)
    listing = models.ForeignKey(Listing, related_name="comments", on_delete=models.PROTECT)
    user = models.ForeignKey(User, related_name="comments", on_delete=models.PROTECT)
    add_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.comment}"
