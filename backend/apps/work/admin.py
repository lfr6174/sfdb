from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline

from .models import (
    Catalogue,
    CatalogueEntry,
    Publication,
    PublicationCredit,
    Publisher,
    Series,
    Work,
    WorkConcept,
    WorkCredit,
    WorkPublication,
)

# ============================================================================
# INLINES
# ============================================================================


class WorkCreditInline(TabularInline):
    model = WorkCredit
    extra = 0
    autocomplete_fields = ("person",)


class WorkConceptInline(TabularInline):
    model = WorkConcept
    extra = 1
    autocomplete_fields = ("concept",)


class PublicationCreditInline(TabularInline):
    model = PublicationCredit
    extra = 0
    fields = ("person", "display_name", "role", "order")
    autocomplete_fields = ("person",)


class WorkPublicationInlineForWork(TabularInline):
    model = WorkPublication
    extra = 0
    autocomplete_fields = ("publication",)


class WorkPublicationInlineForPublication(TabularInline):
    model = WorkPublication
    extra = 1
    autocomplete_fields = ("work",)


class CatalogueEntryInline(TabularInline):
    model = CatalogueEntry
    extra = 1
    autocomplete_fields = ("work",)


# ============================================================================
# WORK ADMINS
# ============================================================================


@admin.register(Series)
class SeriesAdmin(ModelAdmin):
    list_display = ("title", "created_at", "updated_at")
    search_fields = ("title",)
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        ("基本資訊 (Basic Info)", {"fields": ("title", "note")}),
        ("系統資訊 (System Info)", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )


@admin.register(Work)
class WorkAdmin(ModelAdmin):
    list_display = (
        "title",
        "get_credits_display",
        "media_type",
        "work_length",
        "provenance",
        "language",
        "year",
        "series",
    )
    list_filter = ("media_type", "work_length", "provenance", "language", "year")
    search_fields = ("title", "description", "credits__person__name", "credits__person__aliases__name")
    autocomplete_fields = ("series",)
    inlines = [WorkCreditInline, WorkConceptInline, WorkPublicationInlineForWork]
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        (
            "基本資訊 (Basic Info)",
            {"fields": ("title", "media_type", "work_length", "provenance", "language", "year", "description")},
        ),
        ("系列資訊 (Series Info)", {"fields": ("series", "series_order")}),
        ("系統資訊 (System Info)", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related("credits__person")

    def get_credits_display(self, obj):
        credits = obj.credits.all()
        if not credits:
            return "佚名"
        return "、".join([f"{c.person.name} ({c.get_role_display()})" for c in credits])

    get_credits_display.short_description = "參與人員"


# ============================================================================
# PUBLICATION ADMINS
# ============================================================================


@admin.register(Publisher)
class PublisherAdmin(ModelAdmin):
    list_display = ("name", "created_at", "updated_at")
    search_fields = ("name",)
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        ("基本資訊 (Basic Info)", {"fields": ("name", "description")}),
        ("系統資訊 (System Info)", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )


@admin.register(Publication)
class PublicationAdmin(ModelAdmin):
    list_display = (
        "title",
        "get_credits_display",
        "media",
        "get_works_display",
        "publisher",
        "language",
        "year",
        "isbn",
    )
    list_filter = ("language", "media", "year", "publisher")
    search_fields = ("title", "isbn", "works__title", "credits__person__name", "credits__person__aliases__name")
    autocomplete_fields = ("publisher",)
    inlines = [WorkPublicationInlineForPublication, PublicationCreditInline]
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        (
            "基本資訊 (Basic Info)",
            {"fields": ("media", "publisher", "title", "language", "year", "isbn", "note")},
        ),
        ("系統資訊 (System Info)", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related("credits__person", "works")

    def get_works_display(self, obj):
        works = obj.works.all()[:3]
        display = "、".join([w.title for w in works])
        if obj.works.count() > 3:
            display += "..."
        return display or "-"

    get_works_display.short_description = "收錄作品"

    def get_credits_display(self, obj):
        credits = obj.credits.all()
        valid_credits = []
        for c in credits:
            # 如果是原作者且沒填寫別名，就不顯示在列表摘要中
            if c.role in ["author", "co_author", "story", "art"] and not c.display_name:
                continue
            valid_credits.append(c)

        if not valid_credits:
            return "-"
        return "、".join([f"{c.display_name or c.person.name} ({c.get_role_display()})" for c in valid_credits])

    get_credits_display.short_description = "參與人員"


# ============================================================================
# CATALOGUE ADMINS
# ============================================================================


@admin.register(Catalogue)
class CatalogueAdmin(ModelAdmin):
    list_display = ("title", "catalogue_type", "curator", "year")
    list_filter = ("catalogue_type", "year")
    search_fields = ("title", "curator__name")
    autocomplete_fields = ("curator",)
    inlines = [CatalogueEntryInline]
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("基本資訊 (Basic Info)", {"fields": ("title", "catalogue_type", "curator", "year", "note")}),
        ("系統資訊 (System Info)", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )
