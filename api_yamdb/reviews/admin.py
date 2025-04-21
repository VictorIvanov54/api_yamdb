from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User, Genre, Category, Title, Review, Comment


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'role', 'is_staff', 'is_superuser')
    list_filter = ('role', 'is_staff', 'is_superuser')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('title', 'text', 'score', 'author', 'pub_date')
    list_filter = ('title', 'author', 'score', 'pub_date')
    search_fields = ('text', 'author__username', 'title__name')
    date_hierarchy = 'pub_date'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('review', 'text', 'author', 'pub_date')
    list_filter = ('review', 'author', 'pub_date')
    search_fields = ('text', 'author__username', 'review__title__name')
    date_hierarchy = 'pub_date'


admin.site.register(Genre)
admin.site.register(Category)
admin.site.register(Title)
