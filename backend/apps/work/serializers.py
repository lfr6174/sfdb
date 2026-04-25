from rest_framework import serializers

from apps.concept.serializers import ConceptMinimalSerializer
from apps.person.models import Person

from .models import (
    Catalogue,
    CatalogueEntry,
    Publication,
    PublicationCredit,
    Publisher,
    Series,
    Work,
    WorkConcept,
    WorkCredit,
)

# ============================================================================
# MINIMAL / UTILITY SERIALIZERS
# ============================================================================


class PersonMinimalSerializer(serializers.ModelSerializer):
    """
    A lightweight serializer for Person to prevent circular imports
    and overly bloated JSON payloads when serializing nested relationships.
    """

    class Meta:
        model = Person
        fields = ["id", "name"]


class WorkMinimalSerializer(serializers.ModelSerializer):
    """Lightweight Work serializer for Catalogue entries or related list views."""

    class Meta:
        model = Work
        fields = ["id", "title", "year"]


# ============================================================================
# WORK ECOSYSTEM SERIALIZERS
# ============================================================================


class SeriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Series
        fields = ["id", "title", "note", "created_at", "updated_at"]


class WorkCreditSerializer(serializers.ModelSerializer):
    person_detail = PersonMinimalSerializer(source="person", read_only=True)
    role_display = serializers.CharField(source="get_role_display", read_only=True)

    class Meta:
        model = WorkCredit
        fields = ["id", "person", "person_detail", "role", "role_display", "order"]


class WorkConceptSerializer(serializers.ModelSerializer):
    concept_detail = ConceptMinimalSerializer(source="concept", read_only=True)

    class Meta:
        model = WorkConcept
        fields = ["id", "concept", "concept_detail", "description"]


# ============================================================================
# PUBLICATION ECOSYSTEM SERIALIZERS
# ============================================================================


class PublisherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publisher
        fields = ["id", "name", "description", "created_at", "updated_at"]


class PublicationCreditSerializer(serializers.ModelSerializer):
    person_detail = PersonMinimalSerializer(source="person", read_only=True)
    role_display = serializers.CharField(source="get_role_display", read_only=True)

    class Meta:
        model = PublicationCredit
        fields = ["id", "person", "person_detail", "role", "role_display", "order"]


class PublicationSerializer(serializers.ModelSerializer):
    publisher_detail = PublisherSerializer(source="publisher", read_only=True)
    credits = PublicationCreditSerializer(many=True, read_only=True)

    class Meta:
        model = Publication
        fields = [
            "id",
            "work",
            "publisher",
            "publisher_detail",
            "title",
            "year",
            "isbn",
            "note",
            "credits",
            "created_at",
            "updated_at",
        ]


# ============================================================================
# MAIN WORK SERIALIZER (The Aggregator)
# ============================================================================


class WorkSerializer(serializers.ModelSerializer):
    """
    The ultimate aggregator serializer that pulls together the Work,
    its credits, its concepts, and its physical publications.
    """

    media_type_display = serializers.CharField(source="get_media_type_display", read_only=True)
    work_length_display = serializers.CharField(source="get_work_length_display", read_only=True)

    series_detail = SeriesSerializer(source="series", read_only=True)
    credits = WorkCreditSerializer(many=True, read_only=True)
    work_concepts = WorkConceptSerializer(many=True, read_only=True)
    publications = PublicationSerializer(many=True, read_only=True)

    class Meta:
        model = Work
        fields = [
            "id",
            "title",
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
            "created_at",
            "updated_at",
        ]


# ============================================================================
# CATALOGUE SERIALIZERS
# ============================================================================


class CatalogueEntrySerializer(serializers.ModelSerializer):
    work_detail = WorkMinimalSerializer(source="work", read_only=True)

    class Meta:
        model = CatalogueEntry
        fields = ["id", "catalogue", "work", "work_detail", "order", "note"]


class CatalogueSerializer(serializers.ModelSerializer):
    catalogue_type_display = serializers.CharField(source="get_catalogue_type_display", read_only=True)
    curator_detail = PersonMinimalSerializer(source="curator", read_only=True)

    class Meta:
        model = Catalogue
        fields = [
            "id",
            "title",
            "catalogue_type",
            "catalogue_type_display",
            "curator",
            "curator_detail",
            "year",
            "note",
            "created_at",
            "updated_at",
        ]
