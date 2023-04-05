from django.contrib import admin
from .models import Post, Comment, Account, Tag, Like
from markdownx.admin import MarkdownxModelAdmin

admin.site.register(Post, MarkdownxModelAdmin)

admin.site.register(Comment)

admin.site.register(Tag) #追加部分

admin.site.register(Account)

admin.site.register(Like)