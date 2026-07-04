from rest_framework import serializers

from .models import Concept, ConceptAlias, ConceptLink


class ConceptAliasSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConceptAlias
        fields = ["id", "name", "order"]


class ConceptLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConceptLink
        fields = ["id", "title", "url", "order"]


class ConceptMinimalSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source="get_category_display", read_only=True)

    class Meta:
        model = Concept
        fields = ["id", "name", "slug", "category", "category_display"]


class ConceptListSerializer(serializers.ModelSerializer):
    works_count = serializers.IntegerField(read_only=True)
    category_display = serializers.CharField(source="get_category_display", read_only=True)

    class Meta:
        model = Concept
        fields = [
            "id",
            "name",
            "slug",
            "category",
            "category_display",
            "works_count",
            "updated_at",
            "is_featured",
            "featured_order",
        ]


class ConceptDetailSerializer(serializers.ModelSerializer):
    aliases = ConceptAliasSerializer(many=True, read_only=True)
    links = ConceptLinkSerializer(many=True, read_only=True)
    related_concepts = ConceptMinimalSerializer(many=True, read_only=True)
    works_count = serializers.IntegerField(read_only=True)
    work_concepts = serializers.SerializerMethodField()
    category_display = serializers.CharField(source="get_category_display", read_only=True)

    class Meta:
        model = Concept
        fields = [
            "id",
            "name",
            "slug",
            "category",
            "category_display",
            "description",
            "aliases",
            "related_concepts",
            "work_concepts",
            "links",
            "works_count",
            "created_at",
            "updated_at",
        ]

    def get_work_concepts(self, obj):
        # NOTE: Manually construct dict to avoid circular dependency with work serializers
        return [
            {
                "id": wc.id,
                "work": wc.work_id,
                "work_title": wc.work.title,
                "year": wc.work.year,
                "provenance": wc.work.provenance,
                "description": wc.description,
            }
            for wc in getattr(obj, "prefetched_work_concepts", [])
            if wc.description and wc.description.strip()
        ]
