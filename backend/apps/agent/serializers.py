# file: apps/agent/serializers.py
# description: These serializers are migrated from the 'person' app.
# They now serialize the 'Agent' model and its related data.

from rest_framework import serializers

from .models import Agent, AgentAlias, AgentLink
from .services import (
    build_participated_publications_list,
    build_participated_works_list,
    calculate_agent_concept_stats,
)


class AgentAliasSerializer(serializers.ModelSerializer):
    """Serializer for AgentAlias."""

    class Meta:
        model = AgentAlias
        fields = ["id", "name"]


class AgentLinkSerializer(serializers.ModelSerializer):
    """Serializer for AgentLink."""

    class Meta:
        model = AgentLink
        fields = ["id", "label", "url"]  # NOTE: Field name changed from 'title' to 'label'


class AgentSerializer(serializers.ModelSerializer):
    """
    Serializer for Agent.
    Includes nested aliases and links as read-only fields.
    (Migrated from PersonSerializer)
    """

    aliases = AgentAliasSerializer(many=True, read_only=True)
    links = AgentLinkSerializer(many=True, read_only=True)
    works_count = serializers.IntegerField(read_only=True)
    roles = serializers.SerializerMethodField()
    concept_stats = serializers.SerializerMethodField()

    class Meta:
        model = Agent
        fields = [
            "id",
            "name",
            "agent_type",
            "about",  # NOTE: Field name changed from 'bio' to 'about'
            "aliases",
            "links",
            "works_count",
            "roles",
            "concept_stats",
            "created_at",
            "updated_at",
        ]

    def get_roles(self, obj):
        # Avoid duplicate roles using set. These related names are now on the Agent model.
        work_roles = {credit.get_role_display() for credit in obj.work_credits.all()}
        pub_roles = {credit.get_role_display() for credit in obj.publication_credits.all()}
        return sorted(list(work_roles | pub_roles))

    def get_concept_stats(self, obj):
        return calculate_agent_concept_stats(obj)


class AgentDetailSerializer(AgentSerializer):
    """
    Serializer for Agent detail view.
    Includes a comprehensive list of all participated works and publications.
    (Migrated from PersonDetailSerializer)
    """

    participated_works = serializers.SerializerMethodField()
    participated_publications = serializers.SerializerMethodField()

    class Meta(AgentSerializer.Meta):
        fields = AgentSerializer.Meta.fields + ["participated_works", "participated_publications"]

    def get_participated_works(self, obj):
        return build_participated_works_list(obj)

    def get_participated_publications(self, obj):
        return build_participated_publications_list(obj)
