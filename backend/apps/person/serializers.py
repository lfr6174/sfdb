from rest_framework import serializers

from .models import Person, PersonAlias, PersonLink


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

    class Meta:
        model = Person
        fields = ["id", "name", "bio", "aliases", "links", "works_count", "created_at", "updated_at"]
