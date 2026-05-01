from django.contrib import admin
from unfold.admin import ModelAdmin, StackedInline, TabularInline
from unfold.contrib.filters.admin import ChoicesDropdownFilter, RangeNumericFilter, RelatedDropdownFilter

from .models import (
    Catalogue,
    CatalogueEntry,
    Publication,
    PublicationCredit,
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
    autocomplete_fields = ("agent",)
    classes = ["collapse"]


class WorkConceptInline(StackedInline):
    model = WorkConcept
    extra = 0
    autocomplete_fields = ("concept",)
    classes = ["collapse"]


class PublicationCreditInline(TabularInline):
    model = PublicationCredit
    extra = 0
    fields = ("agent", "display_name", "role", "order")
    autocomplete_fields = ("agent",)
    classes = ["collapse"]


class WorkPublicationInlineForWork(TabularInline):
    model = WorkPublication
    extra = 0
    autocomplete_fields = ("publication",)
    classes = ["collapse"]


class WorkPublicationInlineForPublication(TabularInline):
    model = WorkPublication
    extra = 0
    autocomplete_fields = ("work",)
    classes = ["collapse"]


class CatalogueEntryInline(TabularInline):
    model = CatalogueEntry
    extra = 0
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
    list_filter = (
        ("media_type", ChoicesDropdownFilter),
        ("work_length", ChoicesDropdownFilter),
        ("provenance", ChoicesDropdownFilter),
        ("language", ChoicesDropdownFilter),
        ("year", RangeNumericFilter),
    )
    search_fields = ("title", "description", "credits__agent__name", "credits__agent__aliases__name")
    autocomplete_fields = ("series",)
    inlines = [WorkCreditInline, WorkConceptInline, WorkPublicationInlineForWork]
    readonly_fields = ("created_at", "updated_at")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related("credits__agent")

    def get_credits_display(self, obj):
        credits = obj.credits.all()
        if not credits:
            return "佚名"
        return "、".join([f"{c.agent.name} ({c.get_role_display()})" for c in credits])

    get_credits_display.short_description = "參與人員"


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
    list_filter = (
        ("language", ChoicesDropdownFilter),
        ("media", ChoicesDropdownFilter),
        ("year", RangeNumericFilter),
        ("publisher", RelatedDropdownFilter),
    )
    search_fields = ("title", "isbn", "works__title", "credits__agent__name", "credits__agent__aliases__name")
    autocomplete_fields = ("publisher",)
    inlines = [WorkPublicationInlineForPublication, PublicationCreditInline]
    readonly_fields = ("created_at", "updated_at")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related("credits__agent", "works")

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
        return "、".join([f"{c.display_name or c.agent.name} ({c.get_role_display()})" for c in valid_credits])

    get_credits_display.short_description = "參與人員"


# ============================================================================
# CATALOGUE ADMINS
# ============================================================================


@admin.register(Catalogue)
class CatalogueAdmin(ModelAdmin):
    list_display = ("title", "catalogue_type", "agent_curator", "year")
    list_filter = (
        ("catalogue_type", ChoicesDropdownFilter),
        ("year", RangeNumericFilter),
    )
    search_fields = ("title", "agent_curator__name")
    autocomplete_fields = ("agent_curator",)
    inlines = [CatalogueEntryInline]
    readonly_fields = ("created_at", "updated_at")
