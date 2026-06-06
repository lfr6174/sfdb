from rest_framework import serializers

from apps.agent.models import Agent
from apps.concept.serializers import ConceptMinimalSerializer

from .models import (
    Catalogue,
    Cycle,
    Publication,
    PublicationAgent,
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
    class Meta:
        model = Agent
        fields = ["id", "name", "agent_type"]


# ============================================================================
# WORK SERIALIZERS
# ============================================================================


class CycleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cycle
        fields = ["id", "title", "note", "created_at", "updated_at"]


class WorkAgentSerializer(serializers.ModelSerializer):
    agent = AgentMinimalSerializer(read_only=True)
    role = serializers.SlugRelatedField(slug_field="code", read_only=True)
    role_display = serializers.CharField(source="role.noun", read_only=True)

    class Meta:
        model = WorkAgent
        fields = ["id", "agent", "role", "role_display", "order"]


class WorkConceptListSerializer(serializers.ModelSerializer):
    concept = ConceptMinimalSerializer(read_only=True)

    class Meta:
        model = WorkConcept
        fields = ["id", "concept"]


class WorkConceptSerializer(serializers.ModelSerializer):
    concept = ConceptMinimalSerializer(read_only=True)

    class Meta:
        model = WorkConcept
        fields = ["id", "concept", "description"]


# ============================================================================
# PUBLICATION SERIALIZERS
# ============================================================================


class PublicationAgentSerializer(serializers.ModelSerializer):
    agent = AgentMinimalSerializer(read_only=True)
    role = serializers.SlugRelatedField(slug_field="code", read_only=True)
    role_display = serializers.CharField(source="role.noun", read_only=True)

    class Meta:
        model = PublicationAgent
        fields = ["id", "agent", "display_name", "role", "role_display", "order"]


class PublicationInWorkSerializer(serializers.ModelSerializer):
    """Publication serializer for use inside WorkSerializer - excludes manifestations to avoid redundancy."""

    language_display = serializers.CharField(source="get_language_display", read_only=True)
    publisher = AgentMinimalSerializer(read_only=True)
    source_display = serializers.CharField(source="get_source_display", read_only=True)
    media_display = serializers.CharField(source="composite_media_display", read_only=True)
    year = serializers.SerializerMethodField()
    contributions = PublicationAgentSerializer(many=True, read_only=True)

    class Meta:
        model = Publication
        fields = [
            "id",
            "title",
            "source_display",
            "media_display",
            "language_display",
            "year",
            "isbn",
            "note",
            "publisher",
            "contributions",
        ]

    def get_year(self, obj):
        return obj.pub_date.year if obj.pub_date else None


# ============================================================================
# CATALOGUE ENTRY FOR WORK SERIALIZER
# ============================================================================


class CatalogueBriefSerializer(serializers.ModelSerializer):
    catalogue_type_display = serializers.CharField(source="get_catalogue_type_display", read_only=True)
    curators = AgentMinimalSerializer(many=True, read_only=True, source="agents")

    class Meta:
        model = Catalogue
        fields = ["id", "title", "catalogue_type_display", "year", "curators"]


class WorkCatalogueSerializer(serializers.ModelSerializer):
    catalogue = CatalogueBriefSerializer(read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = WorkCatalogue
        fields = ["id", "catalogue", "category", "status", "status_display", "note"]


# ============================================================================
# MAIN WORK SERIALIZER (The Aggregator)
# ============================================================================


class WorkListSerializer(serializers.ModelSerializer):
    byline = serializers.SerializerMethodField()
    genre_display = serializers.CharField(source="get_genre_display", read_only=True)
    work_length_display = serializers.CharField(source="get_work_length_display", read_only=True)
    year = serializers.SerializerMethodField()
    work_concepts = WorkConceptListSerializer(many=True, read_only=True)

    class Meta:
        model = Work
        fields = [
            "id",
            "title",
            "year",
            "byline",
            "genre_display",
            "work_length_display",
            "work_concepts",
        ]

    def get_byline(self, obj):
        return get_byline(obj.contributions.all())

    def get_year(self, obj):
        return obj.ori_date.year if obj.ori_date else None


class WorkDetailSerializer(serializers.ModelSerializer):
    genre_display = serializers.CharField(source="get_genre_display", read_only=True)
    language_display = serializers.CharField(source="get_language_display", read_only=True)
    work_length_display = serializers.CharField(source="get_work_length_display", read_only=True)
    year = serializers.SerializerMethodField()

    def get_year(self, obj):
        return obj.ori_date.year if obj.ori_date else None

    cycle = CycleSerializer(read_only=True)
    contributions = WorkAgentSerializer(many=True, read_only=True)
    work_concepts = WorkConceptSerializer(many=True, read_only=True)
    publications = serializers.SerializerMethodField()
    work_catalogues = WorkCatalogueSerializer(many=True, read_only=True)
    byline = serializers.SerializerMethodField()
    credit = serializers.SerializerMethodField()

    class Meta:
        model = Work
        fields = [
            "id",
            "title",
            "language",
            "language_display",
            "genre",
            "genre_display",
            "work_length",
            "work_length_display",
            "year",
            "description",
            "cycle",
            "cycle_order",
            "contributions",
            "work_concepts",
            "publications",
            "work_catalogues",
            "byline",
            "credit",
            "updated_at",
        ]

    def get_byline(self, obj):
        return get_byline(obj.contributions.all())

    def get_credit(self, obj):
        return get_credits(obj.contributions.all())

    def get_publications(self, obj):
        manifestations = getattr(obj, "prefetched_manifestations", obj.manifestations.all())
        if not manifestations:
            return []

        publications = [man.publication for man in manifestations]
        pub_data_list = PublicationInWorkSerializer(publications, many=True, context=self.context).data

        # Merge manifestation-specific metadata back into the serialized publication data.
        for man, pub_data in zip(manifestations, pub_data_list, strict=True):
            pub_data["manifestation_id"] = man.id
            pub_data["manifestation_name"] = man.name
            pub_data["manifestation_display_name"] = man.name if man.name else man.publication.title

            man_credit = get_credits(man.contributions.all())
            pub_credit = get_credits(man.publication.contributions.all())
            pub_data["credit"] = man_credit + pub_credit

        return pub_data_list
