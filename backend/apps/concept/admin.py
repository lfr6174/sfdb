from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from unfold.contrib.filters.admin import ChoicesDropdownFilter

from .models import Concept, ConceptLink


class ConceptLinkInline(TabularInline):
    model = ConceptLink
    extra = 0
    classes = ["collapse"]


@admin.register(Concept)
class ConceptAdmin(ModelAdmin):
    list_display = ("name", "category", "created_at", "updated_at")
    list_filter = (("category", ChoicesDropdownFilter),)
    search_fields = ("name", "slug")
    autocomplete_fields = ("related_concepts",)
    inlines = [ConceptLinkInline]
    readonly_fields = ("created_at", "updated_at")
