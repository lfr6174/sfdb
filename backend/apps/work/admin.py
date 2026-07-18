import datetime

from django import forms
from django.contrib import admin
from django.utils.safestring import mark_safe
from import_export.admin import ImportMixin
from simple_history.admin import SimpleHistoryAdmin
from unfold.admin import ModelAdmin, TabularInline
from unfold.contrib.filters.admin import (
    ChoicesDropdownFilter,
    RangeDateFilter,
    RangeNumericFilter,
    RelatedDropdownFilter,
)

from apps.core.admin import RestrictedImportMixin, SizeLimitedImportForm

from .models import (
    Catalogue,
    Category,
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
    WorkRelation,
)
from .resources import PublicationResource, WorkResource

# --- Partial-date widget / field / forms ---

_CY = datetime.date.today().year
_YEAR_CHOICES = [("", "---")] + [(y, y) for y in range(_CY + 1, 1899, -1)]
_MONTH_CHOICES = [("", "---")] + [(m, f"{m:02d}") for m in range(1, 13)]
_DAY_CHOICES = [("", "---")] + [(d, f"{d:02d}") for d in range(1, 32)]


class PartialDateWidget(forms.MultiWidget):
    def __init__(self, attrs=None):
        super().__init__(
            widgets=[
                forms.Select(choices=_YEAR_CHOICES, attrs={"style": "width:auto"}),
                forms.Select(choices=_MONTH_CHOICES, attrs={"style": "width:auto"}),
                forms.Select(choices=_DAY_CHOICES, attrs={"style": "width:auto"}),
            ],
            attrs=attrs,
        )

    def render(self, name, value, attrs=None, renderer=None):
        if not isinstance(value, list):
            value = self.decompress(value)

        final_attrs = self.build_attrs(attrs or {})
        base_id = final_attrs.get("id", "")
        labels = ["年", "月", "日"]
        parts = []

        for i, (widget, label) in enumerate(zip(self.widgets, labels, strict=True)):
            sub_attrs = {**final_attrs, "id": f"{base_id}_{i}" if base_id else ""}
            rendered = widget.render(
                f"{name}_{i}",
                value[i] if i < len(value) else "",
                sub_attrs,
                renderer=renderer,
            )
            parts.append(f"{rendered} <span style='margin:0 8px 0 2px'>{label}</span>")

        return mark_safe("".join(parts))  # noqa: S308 — label is hardcoded; rendered is Django-escaped widget HTML

    def decompress(self, value):
        if not value:
            return ["", "", ""]
        date, precision = value
        return [
            date.year,
            date.month if precision in ("month", "day") else "",
            date.day if precision == "day" else "",
        ]


class PartialDateField(forms.MultiValueField):
    """Combines three dropdown values into a (date, precision) tuple."""

    widget = PartialDateWidget

    def __init__(self, *args, **kwargs):
        fields = (
            forms.ChoiceField(choices=_YEAR_CHOICES, required=False),
            forms.ChoiceField(choices=_MONTH_CHOICES, required=False),
            forms.ChoiceField(choices=_DAY_CHOICES, required=False),
        )
        super().__init__(*args, fields=fields, require_all_fields=False, **kwargs)

    def compress(self, data_list):
        y, m, d = [v or None for v in (data_list or ["", "", ""])]
        if not y:
            return None
        if d and not m:
            raise forms.ValidationError("填寫日時，月份不能空白。")
        try:
            date = datetime.date(int(y), int(m) if m else 1, int(d) if d else 1)
        except ValueError as e:
            raise forms.ValidationError(f"日期無效：{e}") from e
        precision = "day" if d else "month" if m else "year"
        return (date, precision)


def _format_partial_date(date_val, precision):
    """Format a partial date for display in list_display."""
    if not date_val:
        return "-"
    if precision == "day":
        return date_val.strftime("%Y-%m-%d")
    if precision == "month":
        return date_val.strftime("%Y-%m")
    return str(date_val.year)


class WorkForm(forms.ModelForm):
    ori_date_partial = PartialDateField(label="首度發表日期", required=False)

    class Meta:
        model = Work
        fields = (
            "title",
            "ori_date_partial",
            "genre",
            "work_length",
            "language",
            "provenance",
            "encoding_level",
            "description",
            "cycle",
            "cycle_order",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk and self.instance.ori_date:
            self.initial["ori_date_partial"] = (
                self.instance.ori_date,
                self.instance.ori_date_precision,
            )

    def save(self, commit=True):
        obj = super().save(commit=False)
        result = self.cleaned_data.get("ori_date_partial")
        if result:
            obj.ori_date, obj.ori_date_precision = result
        else:
            obj.ori_date = None
            obj.ori_date_precision = "year"
        if commit:
            obj.save()
            self.save_m2m()
        return obj


class PublicationForm(forms.ModelForm):
    pub_date_partial = PartialDateField(label="出版日期", required=False)

    class Meta:
        model = Publication
        fields = (
            "title",
            "publisher",
            "pub_date_partial",
            "source",
            "media",
            "binding",
            "language",
            "isbn",
            "subtitle",
            "series",
            "series_order",
            "note",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk and self.instance.pub_date:
            self.initial["pub_date_partial"] = (
                self.instance.pub_date,
                self.instance.pub_date_precision,
            )

    def save(self, commit=True):
        obj = super().save(commit=False)
        result = self.cleaned_data.get("pub_date_partial")
        if result:
            obj.pub_date, obj.pub_date_precision = result
        else:
            obj.pub_date = None
            obj.pub_date_precision = "year"
        if commit:
            obj.save()
            self.save_m2m()
        return obj


# --- Inlines ---


class WorkAgentInline(TabularInline):
    model = WorkAgent
    extra = 0
    autocomplete_fields = ("agent", "role")
    ordering_field = "order"
    hide_ordering_field = True


class WorkConceptInline(TabularInline):
    model = WorkConcept
    extra = 0
    autocomplete_fields = ("concept",)
    classes = ["collapse"]
    ordering_field = "order"
    hide_ordering_field = True


class OutgoingRelationInline(TabularInline):
    model = WorkRelation
    fk_name = "subject_work"
    verbose_name = "關聯設定"
    verbose_name_plural = "設定關聯對象 (設定本作衍生/接續自哪部作品)"
    extra = 0
    autocomplete_fields = ("object_work",)
    classes = ["collapse"]


class IncomingRelationInline(TabularInline):
    model = WorkRelation
    fk_name = "object_work"
    verbose_name = "衍生紀錄"
    verbose_name_plural = "相關衍生紀錄 (本作有哪些續集或衍生作)"
    extra = 0
    can_delete = False
    readonly_fields = ("subject_work", "kind", "note")
    classes = ["collapse"]

    def has_add_permission(self, request, obj=None):
        return False


class PublicationAgentInline(TabularInline):
    model = PublicationAgent
    extra = 0
    fields = ("agent", "display_name", "role", "order")
    autocomplete_fields = ("agent", "role")
    classes = ["collapse"]
    ordering_field = "order"
    hide_ordering_field = True


class ManifestationAgentInline(TabularInline):
    model = ManifestationAgent
    extra = 0
    fields = ("agent", "display_name", "role", "order")
    autocomplete_fields = ("agent", "role")
    classes = ["collapse"]
    ordering_field = "order"
    hide_ordering_field = True


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


class WorkCatalogueInlineForWork(TabularInline):
    model = WorkCatalogue
    extra = 0
    fields = ("catalogue", "year", "category", "result", "note")
    # Category cannot be scoped here because each row may target a different catalogue;
    # an invalid (catalogue, category) pairing is rejected by WorkCatalogue.clean().
    autocomplete_fields = ("catalogue", "category")
    classes = ["collapse"]


class CategoryInline(TabularInline):
    model = Category
    extra = 0


class WorkCatalogueInlineForCatalogue(TabularInline):
    model = WorkCatalogue
    extra = 0
    fields = ("work", "year", "category", "result", "note")
    autocomplete_fields = ("work",)
    classes = ["collapse"]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Scope the category dropdown to the catalogue currently being edited.
        if db_field.name == "category":
            catalogue_id = request.resolver_match.kwargs.get("object_id")
            kwargs["queryset"] = (
                Category.objects.filter(catalogue_id=catalogue_id) if catalogue_id else Category.objects.none()
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


# --- Work admins ---


@admin.register(Role)
class RoleAdmin(ModelAdmin):
    list_display = ("code", "noun", "verb", "description", "order")
    search_fields = ("code", "noun", "verb")
    ordering = ("order", "code")
    ordering_field = "order"
    hide_ordering_field = True


@admin.register(Cycle)
class CycleAdmin(SimpleHistoryAdmin, ModelAdmin):
    list_display = ("title", "created_at", "updated_at")
    search_fields = ("title",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(Series)
class SeriesAdmin(SimpleHistoryAdmin, ModelAdmin):
    list_display = ("title", "created_at", "updated_at")
    search_fields = ("title",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(Work)
class WorkAdmin(RestrictedImportMixin, SimpleHistoryAdmin, ImportMixin, ModelAdmin):
    resource_classes = [WorkResource]
    import_form_class = SizeLimitedImportForm
    form = WorkForm
    list_display = (
        "title",
        "get_contributions_display",
        "genre",
        "work_length",
        "provenance",
        "language",
        "encoding_level",
        "get_date_display",
        "cycle",
    )
    list_filter = (
        ("description", admin.EmptyFieldListFilter),
        ("genre", ChoicesDropdownFilter),
        ("work_length", ChoicesDropdownFilter),
        ("provenance", ChoicesDropdownFilter),
        ("language", ChoicesDropdownFilter),
        ("encoding_level", ChoicesDropdownFilter),
        ("ori_date", RangeDateFilter),
    )
    search_fields = ("title", "description", "contributions__agent__name", "contributions__agent__aliases__name")
    autocomplete_fields = ("cycle",)
    inlines = [
        WorkAgentInline,
        WorkConceptInline,
        OutgoingRelationInline,
        IncomingRelationInline,
        ManifestationInlineForWork,
        WorkCatalogueInlineForWork,
    ]
    readonly_fields = ("created_at", "updated_at")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related("contributions__agent", "contributions__role")

    def get_contributions_display(self, obj):
        contributions = obj.contributions.all()
        if not contributions:
            return "佚名"
        return "、".join([f"{c.agent.name} ({c.role.noun})" for c in contributions])

    get_contributions_display.short_description = "作品創作者"

    def get_date_display(self, obj):
        return _format_partial_date(obj.ori_date, obj.ori_date_precision)

    get_date_display.short_description = "發表日期"
    get_date_display.admin_order_field = "ori_date"


@admin.register(Publication)
class PublicationAdmin(RestrictedImportMixin, SimpleHistoryAdmin, ImportMixin, ModelAdmin):
    resource_classes = [PublicationResource]
    import_form_class = SizeLimitedImportForm
    form = PublicationForm
    list_display = (
        "title",
        "get_date_display",
        "publisher",
        "source",
        "media",
        "isbn",
        "series",
    )
    list_filter = (
        ("language", ChoicesDropdownFilter),
        ("source", ChoicesDropdownFilter),
        ("media", ChoicesDropdownFilter),
        ("binding", ChoicesDropdownFilter),
        ("pub_date", RangeDateFilter),
        ("publisher", RelatedDropdownFilter),
        ("series", RelatedDropdownFilter),
    )
    search_fields = (
        "title",
        "subtitle",
        "isbn",
        "works__title",
        "contributions__agent__name",
        "contributions__agent__aliases__name",
        "series__title",
    )
    autocomplete_fields = ("publisher", "series")
    inlines = [ManifestationInlineForPublication, PublicationAgentInline]
    readonly_fields = ("created_at", "updated_at")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("publisher", "series").prefetch_related("contributions__agent", "contributions__role")

    def get_date_display(self, obj):
        return _format_partial_date(obj.pub_date, obj.pub_date_precision)

    get_date_display.short_description = "出版日期"
    get_date_display.admin_order_field = "pub_date"


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

    get_contributions_display.short_description = "收錄作品的參與者"


@admin.register(WorkConcept)
class WorkConceptAdmin(SimpleHistoryAdmin, ModelAdmin):
    list_display = ("work", "concept", "description", "order")
    list_filter = (("concept", RelatedDropdownFilter),)
    search_fields = ("work__title", "concept__name", "description")
    autocomplete_fields = ("work", "concept")
    ordering = ("work", "order")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("work", "concept")


# --- Catalogue admins ---


@admin.register(Catalogue)
class CatalogueAdmin(SimpleHistoryAdmin, ModelAdmin):
    list_display = ("title", "catalogue_type")
    list_filter = (("catalogue_type", ChoicesDropdownFilter),)
    search_fields = ("title",)
    inlines = [CategoryInline, WorkCatalogueInlineForCatalogue]
    readonly_fields = ("created_at", "updated_at")


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ("name", "catalogue", "order")
    list_filter = (("catalogue", RelatedDropdownFilter),)
    search_fields = ("name", "catalogue__title")
    autocomplete_fields = ("catalogue",)


@admin.register(WorkCatalogue)
class WorkCatalogueAdmin(ModelAdmin):
    list_display = ("catalogue", "year", "category", "work", "result")
    list_filter = (
        ("catalogue", RelatedDropdownFilter),
        ("year", RangeNumericFilter),
        ("category", RelatedDropdownFilter),
    )
    search_fields = ("work__title", "catalogue__title")
    autocomplete_fields = ("catalogue", "work", "category")
