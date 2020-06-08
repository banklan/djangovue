from django.contrib import admin
from .models import Post, Review


class PostAdmin(admin.ModelAdmin):
    list_display = ('author', 'title', 'created',)
    prepopulated_fields = {'slug': ['title']}
    list_filter = ['title', 'created']


admin.site.register(Post, PostAdmin)


class ReviewAdmin(admin.ModelAdmin):
    list_display = ('author', 'title', 'created',)
    list_filter = ['title', 'author']


admin.site.register(Review, ReviewAdmin)
