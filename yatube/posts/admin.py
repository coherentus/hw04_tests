from django.contrib import admin

from .models import Comment, Follow, Group, Post

EMPTY_VALUE_DISPLAY = '-пусто-'


class PostAdmin(admin.ModelAdmin):
    list_display = ('pk', 'text', 'pub_date', 'author')
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = EMPTY_VALUE_DISPLAY


class GroupAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'slug', 'description')
    search_fields = ('title', 'description', 'slug')


class CommentAdmin(admin.ModelAdmin):
    list_display = ('pk', 'text', 'created', 'author', 'post')
    search_fields = ('text', 'author', 'post')
    list_filter = ('created',)


class FollowAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'author')
    search_fields = ('user', 'author')
    list_filter = ('user',)


admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Follow, FollowAdmin)
