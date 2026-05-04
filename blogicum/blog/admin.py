from django.contrib import admin
from .models import Post, Category, Location

admin.site.site_header = 'Администрирование Блогикума'
admin.site.site_title = 'Блогикум'
admin.site.index_title = 'Админка'

admin.site.register(Category)
admin.site.register(Location)
admin.site.register(Post)
