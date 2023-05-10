from django.contrib import admin
from .models import User, Post

# Register your models here.
class CustomPost(admin.ModelAdmin):
    list_display = ('id', 'poster', 'content',)
    list_display_links = ('id', 'poster', 'content',)
    list_filter = ('poster',)
    filter_horizontal = ('likes',)

admin.site.register(Post, CustomPost)
admin.site.register(User)