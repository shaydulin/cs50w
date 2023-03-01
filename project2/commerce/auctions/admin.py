from django.contrib import admin

from .models import User, Listing, Bid, Comment
# Register your models here.

class AdminListing(admin.ModelAdmin):
    filter_horizontal = ("watchers",)

admin.site.register(User)
admin.site.register(Listing, AdminListing)
admin.site.register(Bid)
admin.site.register(Comment)

