from rest_framework import serializers

from .models import Person, PersonAlias, PersonLink
from .services import (
    build_participated_publications_list,
    build_participated_works_list,
    calculate_person_concept_stats,
)


class PersonAliasSerializer(serializers.ModelSerializer):
    """Serializer for PersonAlias."""

    class Meta:
        model = PersonAlias
        fields = ["id", "name"]


class PersonLinkSerializer(serializers.ModelSerializer):
    """Serializer for PersonLink."""

    class Meta:
        model = PersonLink
        fields = ["id", "title", "url"]


class PersonSerializer(serializers.ModelSerializer):
    """
    Serializer for Person.
    Includes nested aliases and links as read-only fields.
    """

    aliases = PersonAliasSerializer(many=True, read_only=True)
    links = PersonLinkSerializer(many=True, read_only=True)
    works_count = serializers.IntegerField(read_only=True)
    roles = serializers.SerializerMethodField()
    concept_stats = serializers.SerializerMethodField()

    class Meta:
        model = Person
        fields = [
            "id",
            "name",
            "bio",
            "aliases",
            "links",
            "works_count",
            "roles",
            "concept_stats",
            "created_at",
            "updated_at",
        ]

    def get_roles(self, obj):
        # Avoid duplicate roles using set
        work_roles = {credit.get_role_display() for credit in obj.work_credits.all()}
        pub_roles = {credit.get_role_display() for credit in obj.publication_credits.all()}
        return sorted(list(work_roles | pub_roles))

    def get_concept_stats(self, obj):
        return calculate_person_concept_stats(obj)


class PersonDetailSerializer(PersonSerializer):
    """
    Serializer for Person detail view.
    Includes a comprehensive list of all participated works and publications.
    """

    participated_works = serializers.SerializerMethodField()
    participated_publications = serializers.SerializerMethodField()

    class Meta(PersonSerializer.Meta):
        fields = PersonSerializer.Meta.fields + ["participated_works", "participated_publications"]

    def get_participated_works(self, obj):
        return build_participated_works_list(obj)

    def get_participated_publications(self, obj):
        return build_participated_publications_list(obj)
