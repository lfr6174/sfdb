from django.contrib import admin
from unfold.admin import ModelAdmin

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
)

# ============================================================================
# INLINES
# ============================================================================


class WorkCreditInline(admin.TabularInline):
    model = WorkCredit
    extra = 1
    autocomplete_fields = ("person",)


class WorkConceptInline(admin.TabularInline):
    model = WorkConcept
    extra = 1
    autocomplete_fields = ("concept",)


class PublicationInline(admin.TabularInline):
    model = Publication
    extra = 1
    autocomplete_fields = ("publisher",)
    show_change_link = True  # Provide a link to navigate to the publication page for adding contributors


class PublicationCreditInline(admin.TabularInline):
    model = PublicationCredit
    extra = 1
    fields = ("person", "display_name", "role", "order")
    autocomplete_fields = ("person",)


class CatalogueEntryInline(admin.TabularInline):
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
    list_display = ("title", "media_type", "work_length", "language", "year", "series")
    list_filter = ("media_type", "work_length", "language", "year")
    search_fields = ("title", "description")
    autocomplete_fields = ("series",)
    inlines = [WorkCreditInline, WorkConceptInline, PublicationInline]
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        (
            "基本資訊 (Basic Info)",
            {"fields": ("title", "media_type", "work_length", "language", "year", "description")},
        ),
        ("系列資訊 (Series Info)", {"fields": ("series", "series_order")}),
        ("系統資訊 (System Info)", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )


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
    list_display = ("title", "work", "publisher", "language", "year", "isbn")
    list_filter = ("language", "year", "publisher")
    search_fields = ("title", "isbn", "work__title")
    autocomplete_fields = ("work", "publisher")
    inlines = [PublicationCreditInline]
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("基本資訊 (Basic Info)", {"fields": ("work", "publisher", "title", "language", "year", "isbn", "note")}),
        ("系統資訊 (System Info)", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )


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
