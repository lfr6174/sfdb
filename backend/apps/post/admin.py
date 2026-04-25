from django.contrib import admin

from .models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "post_type", "is_pinned", "created_at")
    list_filter = ("post_type", "is_pinned")
    search_fields = ("title", "body")
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("基本資訊", {"fields": ("post_type", "title", "body")}),
        (
            "發布與狀態",
            {
                "fields": ("is_pinned",),
            },
        ),
        ("系統資訊", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )
