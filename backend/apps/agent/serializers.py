from rest_framework import serializers

from .models import Agent, AgentAlias, AgentLink
from .services import (
    get_agent_concepts,
    get_agent_publications,
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

    class Meta:
        model = Agent
        fields = [
            "id",
            "name",
            "agent_type",
            "about",
            "aliases",
            "links",
            "updated_at",
        ]


class AgentDetailSerializer(AgentSerializer):
    participated_works = serializers.SerializerMethodField()
    participated_publications = serializers.SerializerMethodField()
    concepts = serializers.SerializerMethodField()

    class Meta(AgentSerializer.Meta):
        fields = AgentSerializer.Meta.fields + ["participated_works", "participated_publications", "concepts"]

    def get_participated_works(self, obj):
        return get_agent_works(obj)

    def get_participated_publications(self, obj):
        return get_agent_publications(obj)

    def get_concepts(self, obj):
        return get_agent_concepts(obj)
