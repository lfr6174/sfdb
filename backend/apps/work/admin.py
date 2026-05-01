from django.contrib import admin
from unfold.admin import ModelAdmin, StackedInline, TabularInline
from unfold.contrib.filters.admin import ChoicesDropdownFilter, RangeNumericFilter, RelatedDropdownFilter

from .models import (
    Catalogue,
    CatalogueEntry,
    Manifestation,
    Publication,
    PublicationAgent,
    Role,
    Series,
    Work,
    WorkAgent,
    WorkConcept,
)

# ============================================================================
# INLINES
# ============================================================================


class WorkAgentInline(TabularInline):
    model = WorkAgent
    extra = 0
    autocomplete_fields = ("agent", "role")
    classes = ["collapse"]


class WorkConceptInline(StackedInline):
    model = WorkConcept
    extra = 0
    autocomplete_fields = ("concept",)
    classes = ["collapse"]


class PublicationAgentInline(TabularInline):
    model = PublicationAgent
    extra = 0
    fields = ("agent", "display_name", "role", "order")
    autocomplete_fields = ("agent", "role")
    classes = ["collapse"]


class ManifestationInlineForWork(TabularInline):
    model = Manifestation
    extra = 0
    autocomplete_fields = ("publication",)
    classes = ["collapse"]


class ManifestationInlineForPublication(TabularInline):
    model = Manifestation
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


@admin.register(Role)
class RoleAdmin(ModelAdmin):
    list_display = ("code", "noun", "verb", "description", "order")
    search_fields = ("code", "noun", "verb")
    ordering = ("order", "code")


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
        "get_contributions_display",
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
    search_fields = ("title", "description", "contributions__agent__name", "contributions__agent__aliases__name")
    autocomplete_fields = ("series",)
    inlines = [WorkAgentInline, WorkConceptInline, ManifestationInlineForWork]
    readonly_fields = ("created_at", "updated_at")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related("contributions__agent", "contributions__role")

    def get_contributions_display(self, obj):
        contributions = obj.contributions.all()
        if not contributions:
            return "佚名"
        return "、".join([f"{c.agent.name} ({c.role.noun})" for c in contributions])

    get_contributions_display.short_description = "參與人員"


@admin.register(Publication)
class PublicationAdmin(ModelAdmin):
    list_display = (
        "title",
        "get_contributions_display",
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
    search_fields = (
        "title",
        "isbn",
        "works__title",
        "contributions__agent__name",
        "contributions__agent__aliases__name",
    )
    autocomplete_fields = ("publisher",)
    inlines = [ManifestationInlineForPublication, PublicationAgentInline]
    readonly_fields = ("created_at", "updated_at")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related("contributions__agent", "contributions__role", "works")

    def get_works_display(self, obj):
        works = obj.works.all()[:3]
        display = "、".join([w.title for w in works])
        if obj.works.count() > 3:
            display += "..."
        return display or "-"

    get_works_display.short_description = "收錄作品"

    def get_contributions_display(self, obj):
        contributions = obj.contributions.all()
        valid_agents = []
        for c in contributions:
            # 如果是原作者且沒填寫別名，就不顯示在列表摘要中
            if c.role.code in ["author", "co_author", "story", "art"] and not c.display_name:
                continue
            valid_agents.append(c)

        if not valid_agents:
            return "-"
        return "、".join([f"{c.display_name or c.agent.name} ({c.role.noun})" for c in valid_agents])

    get_contributions_display.short_description = "參與人員"


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
