from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import ChoicesDropdownFilter

from .models import Commit, Contributor


@admin.register(Contributor)
class ContributorAdmin(SimpleHistoryAdmin, ModelAdmin):
    list_display = ("name", "is_anonymous", "commit_count", "created_at", "updated_at")
    list_filter = ("is_anonymous",)
    search_fields = ("name", "about")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Commit)
class CommitAdmin(SimpleHistoryAdmin, ModelAdmin):
    list_display = (
        "title",
        "contributor",
        "commit_type",
        "scale",
        "contributed_on",
        "created_at",
    )
    list_filter = (
        ("commit_type", ChoicesDropdownFilter),
        ("scale", ChoicesDropdownFilter),
        "contributed_on",
    )
    search_fields = ("title", "body", "contributor__name")
    autocomplete_fields = ("contributor",)
    readonly_fields = ("created_at", "updated_at")
