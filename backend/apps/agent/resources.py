from import_export.resources import ModelResource

from .models import Agent


class AgentResource(ModelResource):
    """force_init_instance: every row creates a new Agent, never matches an existing one."""

    class Meta:
        model = Agent
        fields = ("name", "agent_type", "about")
        force_init_instance = True
        clean_model_instances = True  # runs full_clean(): rejects bad agent_type, enforces max_length, etc.
