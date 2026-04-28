from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin, TabularInline

from .models import Person, PersonAlias, PersonLink


class BioEmptyFilter(admin.SimpleListFilter):
    """
    Custom admin filter to easily find Persons with or without a biography.
    """

    title = _("簡歷狀態 (Bio Status)")
    parameter_name = "bio_empty"

    def lookups(self, request, model_admin):
        return (
            ("empty", _("無簡歷 (Empty)")),
            ("filled", _("有簡歷 (Filled)")),
        )

    def queryset(self, request, queryset):
        if self.value() == "empty":
            return queryset.filter(bio__exact="")
        if self.value() == "filled":
            return queryset.exclude(bio__exact="")
        return queryset


class PersonAliasInline(TabularInline):
    """
    Allows editing Person aliases horizontally on the Person edit page.
    """

    model = PersonAlias
    extra = 1


class PersonLinkInline(TabularInline):
    """
    Allows editing Person links horizontally on the Person edit page.
    """

    model = PersonLink
    extra = 1


@admin.register(Person)
class PersonAdmin(ModelAdmin):
    list_display = ("name", "short_bio", "created_at", "updated_at")
    search_fields = ("name",)
    list_filter = (BioEmptyFilter, "created_at")
    inlines = [PersonAliasInline, PersonLinkInline]

    # Display TimeStamped fields in the detail view as read-only
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("基本資訊 (Basic Info)", {"fields": ("name", "bio")}),
        (
            "系統資訊 (System Info)",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),  # 預設折疊
            },
        ),
    )

    @admin.display(description="簡歷 (Bio)", ordering="bio")
    def short_bio(self, obj):
        """Truncate the bio to 50 characters for the list view."""
        if len(obj.bio) > 50:
            return f"{obj.bio[:50]}..."
        return obj.bio


@admin.register(PersonAlias)
class PersonAliasAdmin(ModelAdmin):
    list_display = ("name", "person")
    search_fields = ("name", "person__name")
    # Use an autocomplete dropdown instead of a heavy standard select box
    autocomplete_fields = ("person",)


@admin.register(PersonLink)
class PersonLinkAdmin(ModelAdmin):
    list_display = ("title", "person", "url")
    search_fields = ("title", "person__name", "url")
    autocomplete_fields = ("person",)
    list_filter = ("title",)
