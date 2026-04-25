from django.contrib import admin

from .models import Concept, ConceptGroup, ConceptLink


class ConceptLinkInline(admin.TabularInline):
    """
    Allows editing Concept links horizontally on the Concept edit page.
    """

    model = ConceptLink
    extra = 1


@admin.register(ConceptGroup)
class ConceptGroupAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "created_at", "updated_at")
    list_filter = ("category",)
    search_fields = ("name",)
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("基本資訊 (Basic Info)", {"fields": ("name", "category")}),
        (
            "進階資訊 (Advanced Info)",
            {
                "fields": ("description",),
                "classes": ("collapse",),  # 預設折疊，保持介面乾淨
            },
        ),
        (
            "系統資訊 (System Info)",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )


@admin.register(Concept)
class ConceptAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "group", "created_at", "updated_at")
    list_filter = ("category", "group")
    search_fields = ("name", "slug")
    autocomplete_fields = ("group", "related_concepts")
    inlines = [ConceptLinkInline]
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("基本資訊 (Basic Info)", {"fields": ("name", "slug", "category", "group", "description")}),
        (
            "關聯 (Relations)",
            {
                "fields": ("related_concepts",),
                "description": "Search and select related concepts to build the horizontal exploration network.",
            },
        ),
        (
            "系統資訊 (System Info)",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),  # Hide this section by default
            },
        ),
    )


@admin.register(ConceptLink)
class ConceptLinkAdmin(admin.ModelAdmin):
    list_display = ("title", "concept", "url", "order")
    search_fields = ("title", "concept__name", "url")
    autocomplete_fields = ("concept",)
    list_filter = ("concept__category",)
