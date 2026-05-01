from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import ChoicesDropdownFilter

from .models import Page, Post


@admin.register(Post)
class PostAdmin(ModelAdmin):
    list_display = ("title", "post_type", "author", "is_pinned", "created_at", "updated_at")
    search_fields = ("title", "body", "author__username")
    list_filter = (("post_type", ChoicesDropdownFilter), "is_pinned")
    readonly_fields = ("created_at", "updated_at")

    def save_model(self, request, obj, form, change):
        if not obj.author_id:
            obj.author = request.user
        super().save_model(request, obj, form, change)


@admin.register(Page)
class PageAdmin(ModelAdmin):
    list_display = ("title", "slug", "created_at", "updated_at")
    search_fields = ("title", "slug", "body")
    readonly_fields = ("created_at", "updated_at")
