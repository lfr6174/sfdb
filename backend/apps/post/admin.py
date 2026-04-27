from django.contrib import admin

from .models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "post_type", "author", "is_pinned", "created_at")
    list_filter = ("post_type", "is_pinned")
    search_fields = ("title", "body", "author__username")
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("基本資訊", {"fields": ("author", "post_type", "title", "body")}),
        (
            "發布與狀態",
            {
                "fields": ("is_pinned",),
            },
        ),
        ("系統資訊", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    def save_model(self, request, obj, form, change):
        if not obj.author_id:
            obj.author = request.user
        super().save_model(request, obj, form, change)
