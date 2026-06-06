from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from unfold.admin import ModelAdmin

from .models import SiteSetting, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "display_name", "email", "is_active", "is_staff", "date_joined")


@admin.register(SiteSetting)
class SiteSettingAdmin(ModelAdmin):
    list_display = ("key", "description", "is_active", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("key", "description", "value")
