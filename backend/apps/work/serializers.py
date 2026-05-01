from rest_framework import serializers

from apps.agent.models import Agent
from apps.agent.serializers import AgentSerializer
from apps.concept.serializers import ConceptMinimalSerializer

from .models import (
    Catalogue,
    CatalogueEntry,
    Publication,
    PublicationCredit,
    Series,
    Work,
    WorkConcept,
    WorkCredit,
)
from .services import build_work_byline

# ============================================================================
# MINIMAL / UTILITY SERIALIZERS
# ============================================================================


class AgentMinimalSerializer(serializers.ModelSerializer):
    """
    A lightweight serializer for Agent to prevent circular imports
    and overly bloated JSON payloads when serializing nested relationships.
    """

    class Meta:
        model = Agent
        fields = ["id", "name"]


class WorkMinimalSerializer(serializers.ModelSerializer):
    """Absolute minimal serializer, useful for dropdowns and option lists."""

    class Meta:
        model = Work
        fields = ["id", "title"]


# ============================================================================
# WORK SERIALIZERS
# ============================================================================


class SeriesSerializer(serializers.ModelSerializer):
    works_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Series
        fields = ["id", "title", "note", "works_count", "created_at", "updated_at"]


class WorkCreditSerializer(serializers.ModelSerializer):
    agent_detail = AgentMinimalSerializer(source="agent", read_only=True)
    role_display = serializers.CharField(source="get_role_display", read_only=True)

    class Meta:
        model = WorkCredit
        fields = ["id", "agent", "agent_detail", "role", "role_display", "order"]


class WorkConceptSerializer(serializers.ModelSerializer):
    concept_detail = ConceptMinimalSerializer(source="concept", read_only=True)

    class Meta:
        model = WorkConcept
        fields = ["id", "concept", "concept_detail", "description"]


class WorkBriefSerializer(serializers.ModelSerializer):
    """Brief Work serializer for cards, lists, and homepage spotlights."""

    media_type_display = serializers.CharField(source="get_media_type_display", read_only=True)
    work_length_display = serializers.CharField(source="get_work_length_display", read_only=True)
    byline = serializers.SerializerMethodField()
    credits = WorkCreditSerializer(many=True, read_only=True)
    work_concepts = WorkConceptSerializer(many=True, read_only=True)

    class Meta:
        model = Work
        fields = [
            "id",
            "title",
            "year",
            "media_type_display",
            "work_length_display",
            "byline",
            "credits",
            "work_concepts",
        ]

    def get_byline(self, obj):
        return build_work_byline(obj)


# ============================================================================
# PUBLICATION SERIALIZERS
# ============================================================================


class PublicationCreditSerializer(serializers.ModelSerializer):
    agent_detail = AgentMinimalSerializer(source="agent", read_only=True)
    role_display = serializers.CharField(source="get_role_display", read_only=True)

    class Meta:
        model = PublicationCredit
        fields = ["id", "agent", "agent_detail", "display_name", "role", "role_display", "order"]


class PublicationSerializer(serializers.ModelSerializer):
    language_display = serializers.CharField(source="get_language_display", read_only=True)
    publisher = AgentSerializer(read_only=True)
    media_display = serializers.CharField(source="get_media_display", read_only=True)
    credits = PublicationCreditSerializer(many=True, read_only=True)
    works = WorkMinimalSerializer(many=True, read_only=True)

    class Meta:
        model = Publication
        fields = [
            "id",
            "works",
            "publisher",
            "title",
            "media",
            "media_display",
            "language",
            "language_display",
            "year",
            "isbn",
            "note",
            "credits",
            "created_at",
            "updated_at",
        ]


# ============================================================================
# CATALOGUE ENTRY FOR WORK SERIALIZER
# ============================================================================


class CatalogueBriefSerializer(serializers.ModelSerializer):
    catalogue_type_display = serializers.CharField(source="get_catalogue_type_display", read_only=True)
    agent_curator_detail = AgentMinimalSerializer(source="agent_curator", read_only=True)

    class Meta:
        model = Catalogue
        fields = ["id", "title", "catalogue_type_display", "year", "agent_curator_detail"]


class WorkCatalogueEntrySerializer(serializers.ModelSerializer):
    catalogue_detail = CatalogueBriefSerializer(source="catalogue", read_only=True)

    class Meta:
        model = CatalogueEntry
        fields = ["id", "catalogue_detail", "order", "note"]


# ============================================================================
# MAIN WORK SERIALIZER (The Aggregator)
# ============================================================================


class WorkSerializer(serializers.ModelSerializer):
    """
    The ultimate aggregator serializer that pulls together the Work,
    its credits, its concepts, and its physical publications.
    """

    media_type_display = serializers.CharField(source="get_media_type_display", read_only=True)
    language_display = serializers.CharField(source="get_language_display", read_only=True)
    work_length_display = serializers.CharField(source="get_work_length_display", read_only=True)

    series_detail = SeriesSerializer(source="series", read_only=True)
    credits = WorkCreditSerializer(many=True, read_only=True)
    work_concepts = WorkConceptSerializer(many=True, read_only=True)
    publications = PublicationSerializer(many=True, read_only=True)
    catalogue_entries = WorkCatalogueEntrySerializer(many=True, read_only=True)

    class Meta:
        model = Work
        fields = [
            "id",
            "title",
            "language",
            "language_display",
            "media_type",
            "media_type_display",
            "work_length",
            "work_length_display",
            "year",
            "description",
            "series",
            "series_detail",
            "series_order",
            "credits",
            "work_concepts",
            "publications",
            "catalogue_entries",
            "created_at",
            "updated_at",
        ]


# ============================================================================
# CATALOGUE SERIALIZERS
# ============================================================================


class CatalogueEntrySerializer(serializers.ModelSerializer):
    work_detail = WorkBriefSerializer(source="work", read_only=True)

    class Meta:
        model = CatalogueEntry
        fields = ["id", "catalogue", "work", "work_detail", "order", "note"]


class CatalogueSerializer(serializers.ModelSerializer):
    catalogue_type_display = serializers.CharField(source="get_catalogue_type_display", read_only=True)
    agent_curator_detail = AgentMinimalSerializer(source="agent_curator", read_only=True)
    works_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Catalogue
        fields = [
            "id",
            "title",
            "catalogue_type",
            "catalogue_type_display",
            "agent_curator",
            "agent_curator_detail",
            "year",
            "note",
            "works_count",
            "created_at",
            "updated_at",
        ]
