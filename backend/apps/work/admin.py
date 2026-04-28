from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import reverse
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
)

# ============================================================================
# INLINES
# ============================================================================


class WorkCreditInline(TabularInline):
    model = WorkCredit
    extra = 1
    autocomplete_fields = ("person",)


class WorkConceptInline(TabularInline):
    model = WorkConcept
    extra = 1
    autocomplete_fields = ("concept",)


class PublicationInline(TabularInline):
    model = Publication
    extra = 0
    autocomplete_fields = ("publisher",)
    show_change_link = True  # Provide a link to navigate to the publication page for adding contributors

    def has_add_permission(self, request, obj=None):
        # 禁用在 Work 頁面直接新增 Publication，強制透過轉址或獨立表單新增
        return False


class PublicationCreditInline(TabularInline):
    model = PublicationCredit
    extra = 1
    fields = ("person", "display_name", "role", "order")
    autocomplete_fields = ("person",)

    def get_formset(self, request, obj=None, **kwargs):
        initial = []
        # 當網址帶有 ?work=123 且是新增模式時，抓取原作品的人物
        if request.method == "GET" and obj is None and "work" in request.GET:
            work_id = request.GET.get("work")
            try:
                work = Work.objects.get(pk=work_id)
                initial = [{"person": c.person_id, "role": c.role, "order": c.order} for c in work.credits.all()]
            except Work.DoesNotExist:
                pass

        FormSet = super().get_formset(request, obj, **kwargs)

        class CustomFormSet(FormSet):
            def __init__(self, *args, **kwargs):
                if initial and not kwargs.get("initial"):
                    kwargs["initial"] = initial
                super().__init__(*args, **kwargs)
                if initial:
                    self.extra = len(initial) + 1  # 產生填好初始值的列，外加 1 列空白給你新增譯者

        return CustomFormSet


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
    inlines = [WorkCreditInline, WorkConceptInline, PublicationInline]
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

    def response_add(self, request, obj, post_url_continue=None):
        """新增 Work 後，若不是點擊「儲存並繼續」或「儲存並新增另一個」，則預設導向至新增 Publication 頁面"""
        if "_continue" not in request.POST and "_addanother" not in request.POST:
            url = reverse("admin:work_publication_add")
            return HttpResponseRedirect(f"{url}?work={obj.id}")
        return super().response_add(request, obj, post_url_continue)

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
    list_display = ("title", "get_credits_display", "media", "work", "publisher", "language", "year", "isbn")
    list_filter = ("language", "media", "year", "publisher")
    search_fields = ("title", "isbn", "work__title", "credits__person__name", "credits__person__aliases__name")
    autocomplete_fields = ("work", "publisher")
    inlines = [PublicationCreditInline]
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        (
            "基本資訊 (Basic Info)",
            {"fields": ("work", "media", "publisher", "title", "language", "year", "isbn", "note")},
        ),
        ("系統資訊 (System Info)", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related("credits__person")

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
