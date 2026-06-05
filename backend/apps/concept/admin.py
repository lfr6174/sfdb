from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from unfold.contrib.filters.admin import ChoicesDropdownFilter

from .models import Concept, ConceptLink


class ConceptLinkInline(TabularInline):
    model = ConceptLink
    extra = 0
    classes = ["collapse"]
    ordering_field = "order"
    hide_ordering_field = True


@admin.register(Concept)
class ConceptAdmin(ModelAdmin):
    list_display = ("name", "category", "is_featured", "featured_order", "created_at", "updated_at")
    list_editable = ("category", "is_featured", "featured_order")
    list_filter = (("category", ChoicesDropdownFilter), "is_featured")
    search_fields = ("name", "slug")
    autocomplete_fields = ("related_concepts",)
    inlines = [ConceptLinkInline]
    readonly_fields = ("created_at", "updated_at")
