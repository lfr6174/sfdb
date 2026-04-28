from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import Concept, ConceptLink


class ConceptLinkInline(admin.TabularInline):
    """
    Allows editing Concept links horizontally on the Concept edit page.
    """

    model = ConceptLink
    extra = 1


@admin.register(Concept)
class ConceptAdmin(ModelAdmin):
    list_display = ("name", "category", "created_at", "updated_at")
    list_filter = ("category",)
    search_fields = ("name", "slug")
    autocomplete_fields = ("related_concepts",)
    inlines = [ConceptLinkInline]
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("基本資訊 (Basic Info)", {"fields": ("name", "slug", "category", "description")}),
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
class ConceptLinkAdmin(ModelAdmin):
    list_display = ("title", "concept", "url", "order")
    search_fields = ("title", "concept__name", "url")
    autocomplete_fields = ("concept",)
    list_filter = ("concept__category",)
