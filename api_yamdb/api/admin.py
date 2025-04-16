from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User  # Replace with your actual model name if different

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    pass
