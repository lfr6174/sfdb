from rest_framework import serializers

from .models import Concept, ConceptLink


class ConceptLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConceptLink
        fields = ["id", "title", "url", "order"]


class ConceptMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Concept
        fields = ["id", "name", "slug", "category"]


class ConceptListSerializer(serializers.ModelSerializer):
    works_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Concept
        fields = ["id", "name", "slug", "category", "works_count", "updated_at"]


class ConceptDetailSerializer(serializers.ModelSerializer):
    links = ConceptLinkSerializer(many=True, read_only=True)
    related_concepts = ConceptMinimalSerializer(many=True, read_only=True)
    works_count = serializers.IntegerField(read_only=True)
    work_concepts = serializers.SerializerMethodField()

    class Meta:
        model = Concept
        fields = [
            "id",
            "name",
            "slug",
            "category",
            "description",
            "related_concepts",
            "work_concepts",
            "links",
            "works_count",
            "created_at",
            "updated_at",
        ]

    def get_work_concepts(self, obj):
        # Avoid importing work serializers to keep concept app self-contained
        return [
            {
                "id": wc.id,
                "work": wc.work_id,
                "work_title": wc.work.title,
                "year": wc.work.year,
                "description": wc.description,
            }
            for wc in getattr(obj, "prefetched_work_concepts", [])
            if wc.description and wc.description.strip()
        ]
