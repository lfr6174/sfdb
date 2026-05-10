from rest_framework import serializers

from apps.agent.models import Agent
from apps.agent.serializers import AgentSerializer
from apps.concept.serializers import ConceptMinimalSerializer

from .models import (
    Catalogue,
    Manifestation,
    ManifestationAgent,
    Publication,
    PublicationAgent,
    Series,
    Work,
    WorkAgent,
    WorkCatalogue,
    WorkConcept,
)
from .services import get_byline, get_credits

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
        fields = ["id", "name", "agent_type"]


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


class WorkAgentSerializer(serializers.ModelSerializer):
    agent = AgentMinimalSerializer(read_only=True)
    role = serializers.SlugRelatedField(slug_field="code", read_only=True)
    role_display = serializers.CharField(source="role.noun", read_only=True)

    class Meta:
        model = WorkAgent
        fields = ["id", "agent", "role", "role_display", "order"]


class WorkConceptSerializer(serializers.ModelSerializer):
    concept = ConceptMinimalSerializer(read_only=True)

    class Meta:
        model = WorkConcept
        fields = ["id", "concept", "description"]


class WorkBriefSerializer(serializers.ModelSerializer):
    """Brief Work serializer for cards, lists, and homepage spotlights."""

    media_type_display = serializers.CharField(source="get_media_type_display", read_only=True)
    work_length_display = serializers.CharField(source="get_work_length_display", read_only=True)
    byline = serializers.SerializerMethodField()
    contributions = WorkAgentSerializer(many=True, read_only=True)
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
            "contributions",
            "work_concepts",
        ]

    def get_byline(self, obj):
        return get_byline(obj.contributions.all())


# ============================================================================
# PUBLICATION SERIALIZERS
# ============================================================================


class ManifestationAgentSerializer(serializers.ModelSerializer):
    agent = AgentMinimalSerializer(read_only=True)
    role = serializers.SlugRelatedField(slug_field="code", read_only=True)
    role_display = serializers.CharField(source="role.noun", read_only=True)

    class Meta:
        model = ManifestationAgent
        fields = ["id", "agent", "display_name", "role", "role_display", "order"]


class ManifestationSerializer(serializers.ModelSerializer):
    work = WorkMinimalSerializer(read_only=True)
    contributions = ManifestationAgentSerializer(many=True, read_only=True)
    display_name = serializers.SerializerMethodField()

    class Meta:
        model = Manifestation
        fields = ["id", "work", "name", "display_name", "contributions"]

    def get_display_name(self, obj):
        return obj.name if obj.name else obj.publication.title


class PublicationAgentSerializer(serializers.ModelSerializer):
    agent = AgentMinimalSerializer(read_only=True)
    role = serializers.SlugRelatedField(slug_field="code", read_only=True)
    role_display = serializers.CharField(source="role.noun", read_only=True)

    class Meta:
        model = PublicationAgent
        fields = ["id", "agent", "display_name", "role", "role_display", "order"]


class PublicationSerializer(serializers.ModelSerializer):
    language_display = serializers.CharField(source="get_language_display", read_only=True)
    publisher = AgentSerializer(read_only=True)
    media_display = serializers.CharField(source="get_media_display", read_only=True)
    contributions = PublicationAgentSerializer(many=True, read_only=True)
    manifestations = ManifestationSerializer(many=True, read_only=True)
    works = WorkMinimalSerializer(many=True, read_only=True)
    credit = serializers.SerializerMethodField()

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
            "manifestations",
            "contributions",
            "credit",
            "created_at",
            "updated_at",
        ]

    def get_credit(self, obj):
        return get_credits(obj.contributions.all())


# ============================================================================
# CATALOGUE ENTRY FOR WORK SERIALIZER
# ============================================================================


class CatalogueBriefSerializer(serializers.ModelSerializer):
    catalogue_type_display = serializers.CharField(source="get_catalogue_type_display", read_only=True)
    agent_curator = AgentMinimalSerializer(read_only=True)

    class Meta:
        model = Catalogue
        fields = ["id", "title", "catalogue_type_display", "year", "agent_curator"]


class WorkCatalogueSerializer(serializers.ModelSerializer):
    catalogue = CatalogueBriefSerializer(read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = WorkCatalogue
        fields = ["id", "catalogue", "category", "status", "status_display", "note"]


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

    series = SeriesSerializer(read_only=True)
    contributions = WorkAgentSerializer(many=True, read_only=True)
    work_concepts = WorkConceptSerializer(many=True, read_only=True)
    publications = serializers.SerializerMethodField()
    work_catalogues = WorkCatalogueSerializer(many=True, read_only=True)
    credit = serializers.SerializerMethodField()

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
            "series_order",
            "contributions",
            "credit",
            "work_concepts",
            "publications",
            "work_catalogues",
            "created_at",
            "updated_at",
        ]

    def get_credit(self, obj):
        return get_credits(obj.contributions.all())

    def get_publications(self, obj):
        # Rely on prefetch_related from ViewSet to avoid N+1 queries.
        manifestations = obj.manifestations.all()
        if not manifestations:
            return []

        # Batch serialize publications to avoid serialization overhead in loops.
        publications = [man.publication for man in manifestations]
        pub_data_list = PublicationSerializer(publications, many=True, context=self.context).data

        # Merge manifestation-specific metadata back into the serialized publication data.
        for man, pub_data in zip(manifestations, pub_data_list):
            pub_data["manifestation_id"] = man.id
            pub_data["manifestation_name"] = man.name
            pub_data["manifestation_display_name"] = man.name if man.name else man.publication.title

            man_credit = get_credits(man.contributions.all())
            pub_credit = pub_data.get("credit", [])
            pub_data["credit"] = man_credit + pub_credit

        return pub_data_list


# ============================================================================
# CATALOGUE SERIALIZERS
# ============================================================================


class CatalogueSerializer(serializers.ModelSerializer):
    catalogue_type_display = serializers.CharField(source="get_catalogue_type_display", read_only=True)
    agent_curator = AgentMinimalSerializer(read_only=True)
    works_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Catalogue
        fields = [
            "id",
            "title",
            "catalogue_type",
            "catalogue_type_display",
            "agent_curator",
            "year",
            "note",
            "works_count",
            "created_at",
            "updated_at",
        ]
