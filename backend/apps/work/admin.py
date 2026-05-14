from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from unfold.contrib.filters.admin import ChoicesDropdownFilter, RangeNumericFilter, RelatedDropdownFilter

from .models import (
    Catalogue,
    Cycle,
    Manifestation,
    ManifestationAgent,
    Publication,
    PublicationAgent,
    Role,
    Series,
    Work,
    WorkAgent,
    WorkCatalogue,
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


class WorkConceptInline(TabularInline):
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


class ManifestationAgentInline(TabularInline):
    model = ManifestationAgent
    extra = 0
    fields = ("agent", "display_name", "role", "order")
    autocomplete_fields = ("agent", "role")
    classes = ["collapse"]


class ManifestationInlineForWork(TabularInline):
    model = Manifestation
    extra = 0
    fields = ("publication", "name")
    autocomplete_fields = ("publication",)
    show_change_link = True
    classes = ["collapse"]


class ManifestationInlineForPublication(TabularInline):
    model = Manifestation
    extra = 0
    fields = ("work", "name")
    autocomplete_fields = ("work",)
    show_change_link = True
    classes = ["collapse"]


class WorkCatalogueInlineForWork(TabularInline):
    model = WorkCatalogue
    extra = 0
    autocomplete_fields = ("catalogue",)
    classes = ["collapse"]


class WorkCatalogueInlineForCatalogue(TabularInline):
    model = WorkCatalogue
    extra = 0
    autocomplete_fields = ("work",)
    classes = ["collapse"]


# ============================================================================
# WORK ADMINS
# ============================================================================


@admin.register(Role)
class RoleAdmin(ModelAdmin):
    list_display = ("code", "noun", "verb", "description", "order")
    search_fields = ("code", "noun", "verb")
    ordering = ("order", "code")


@admin.register(Cycle)
class CycleAdmin(ModelAdmin):
    list_display = ("title", "created_at", "updated_at")
    search_fields = ("title",)
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        ("基本資訊 (Basic Info)", {"fields": ("title", "note")}),
        ("系統資訊 (System Info)", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )


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
        "cycle",
    )
    list_filter = (
        ("media_type", ChoicesDropdownFilter),
        ("work_length", ChoicesDropdownFilter),
        ("provenance", ChoicesDropdownFilter),
        ("language", ChoicesDropdownFilter),
        ("year", RangeNumericFilter),
    )
    search_fields = ("title", "description", "contributions__agent__name", "contributions__agent__aliases__name")
    autocomplete_fields = ("cycle",)
    inlines = [WorkAgentInline, WorkConceptInline, ManifestationInlineForWork, WorkCatalogueInlineForWork]
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
        "series",
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
        "subtitle",
        "isbn",
        "works__title",
        "contributions__agent__name",
        "contributions__agent__aliases__name",
    )
    autocomplete_fields = ("publisher", "series")
    inlines = [ManifestationInlineForPublication, PublicationAgentInline]
    readonly_fields = ("created_at", "updated_at")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("publisher", "series").prefetch_related(
            "contributions__agent", "contributions__role", "works"
        )

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


@admin.register(Manifestation)
class ManifestationAdmin(ModelAdmin):
    list_display = ("publication", "work", "name", "get_contributions_display")
    search_fields = ("work__title", "publication__title", "name", "contributions__agent__name")
    autocomplete_fields = ("work", "publication")
    inlines = [ManifestationAgentInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("work", "publication").prefetch_related("contributions__agent", "contributions__role")

    def get_contributions_display(self, obj):
        contributions = obj.contributions.all()
        if not contributions:
            return "-"
        return "、".join([f"{c.display_name or c.agent.name} ({c.role.noun})" for c in contributions])

    get_contributions_display.short_description = "單篇參與人員"


# ============================================================================
# CATALOGUE ADMINS
# ============================================================================


@admin.register(Catalogue)
class CatalogueAdmin(ModelAdmin):
    list_display = ("title", "catalogue_type", "year")
    list_filter = (
        ("catalogue_type", ChoicesDropdownFilter),
        ("year", RangeNumericFilter),
    )
    search_fields = ("title", "agents__name")
    autocomplete_fields = ("agents",)
    inlines = [WorkCatalogueInlineForCatalogue]
    readonly_fields = ("created_at", "updated_at")
