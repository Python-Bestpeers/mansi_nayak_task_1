from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Comment, Task, User

# Register your models here.


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = (
        "id",
        "email",
        "first_name",
        "last_name",
    )
    search_fields = ("email", "first_name", "last_name")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "text", "user")


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "status",
        "title",
        "detail",
        "priority",
        "assigned_by",
        "assigned_to",
        "priority",
    )
