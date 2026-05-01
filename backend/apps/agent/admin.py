from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline

from .models import Agent, AgentAlias, AgentLink


class AgentAliasInline(TabularInline):
    model = AgentAlias
    extra = 0
    classes = ["collapse"]


class AgentLinkInline(TabularInline):
    model = AgentLink
    extra = 0
    classes = ["collapse"]


@admin.register(Agent)
class AgentAdmin(ModelAdmin):
    list_display = ("name", "agent_type", "short_about", "created_at", "updated_at")
    search_fields = ("name",)
    list_filter = ["agent_type", ("about", admin.EmptyFieldListFilter)]
    inlines = [AgentAliasInline, AgentLinkInline]
    readonly_fields = ("created_at", "updated_at")

    @admin.display(description="簡介")
    def short_about(self, obj):
        """Truncate the about to 50 characters for the list view."""
        if len(obj.about) > 50:
            return f"{obj.about[:50]}..."
        return obj.about
