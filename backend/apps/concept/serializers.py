from rest_framework import serializers

from .models import Concept, ConceptGroup, ConceptLink


class ConceptGroupSerializer(serializers.ModelSerializer):
    """Serializer for ConceptGroup."""

    class Meta:
        model = ConceptGroup
        fields = ["id", "name", "category", "description", "created_at", "updated_at"]


class ConceptLinkSerializer(serializers.ModelSerializer):
    """Serializer for ConceptLink."""

    class Meta:
        model = ConceptLink
        fields = ["id", "title", "url", "order"]


class ConceptMinimalSerializer(serializers.ModelSerializer):
    """
    A lightweight serializer for Concept to prevent infinite recursion
    when serializing the ManyToMany `related_concepts` field.
    """

    class Meta:
        model = Concept
        fields = ["id", "name", "slug", "category"]


class ConceptSerializer(serializers.ModelSerializer):
    """
    Main serializer for Concept.
    Includes rich read-only details for relationships.
    """

    links = ConceptLinkSerializer(many=True, read_only=True)
    group_detail = ConceptGroupSerializer(source="group", read_only=True)
    related_concepts_detail = ConceptMinimalSerializer(source="related_concepts", many=True, read_only=True)
    works_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Concept
        fields = [
            "id",
            "name",
            "slug",
            "category",
            "group",
            "group_detail",
            "description",
            "related_concepts",
            "related_concepts_detail",
            "links",
            "works_count",
            "created_at",
            "updated_at",
        ]
