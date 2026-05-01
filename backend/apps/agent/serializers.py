from rest_framework import serializers

from .models import Agent, AgentAlias, AgentLink
from .services import (
    get_agent_publications,
    get_agent_top_concepts,
    get_agent_works,
)


class AgentAliasSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentAlias
        fields = ["id", "name"]


class AgentLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentLink
        fields = ["id", "label", "url"]


class AgentSerializer(serializers.ModelSerializer):
    aliases = AgentAliasSerializer(many=True, read_only=True)
    links = AgentLinkSerializer(many=True, read_only=True)
    works_count = serializers.IntegerField(read_only=True)
    top_concepts = serializers.SerializerMethodField()

    class Meta:
        model = Agent
        fields = [
            "id",
            "name",
            "agent_type",
            "about",
            "aliases",
            "links",
            "works_count",
            "top_concepts",
            "created_at",
            "updated_at",
        ]

    def get_top_concepts(self, obj):
        return get_agent_top_concepts(obj)


class AgentDetailSerializer(AgentSerializer):
    participated_works = serializers.SerializerMethodField()
    participated_publications = serializers.SerializerMethodField()

    class Meta(AgentSerializer.Meta):
        fields = AgentSerializer.Meta.fields + ["participated_works", "participated_publications"]

    def get_participated_works(self, obj):
        return get_agent_works(obj)

    def get_participated_publications(self, obj):
        return get_agent_publications(obj)
