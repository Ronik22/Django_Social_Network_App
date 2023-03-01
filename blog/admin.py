from django.contrib import admin

from .models import Comment, Image, Post

admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Image)
