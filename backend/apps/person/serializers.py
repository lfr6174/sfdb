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
        from collections import Counter

        concept_counter = Counter()
        counted_work_ids = set()

        # 1. Summarize from works directly
        for credit in obj.work_credits.all():
            work = credit.work
            if work.id not in counted_work_ids:
                counted_work_ids.add(work.id)
                for concept in work.concepts.all():
                    concept_counter[(concept.name, concept.slug)] += 1

        # Return all associated concepts sorted by frequency (descending)
        return [{"name": name, "slug": slug, "count": count} for (name, slug), count in concept_counter.most_common()]


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
        works_dict = {}

        def add_work_to_dict(work, role_display):
            if work.id not in works_dict:
                works_dict[work.id] = {
                    "id": work.id,
                    "title": work.title,
                    "title_en": getattr(work, "title_en", ""),
                    "year": work.year,
                    "media_type": work.get_media_type_display() if hasattr(work, "get_media_type_display") else "",
                    "work_length": work.get_work_length_display() if hasattr(work, "get_work_length_display") else "",
                    "roles": set(),
                    "concepts": [{"name": c.name, "slug": c.slug} for c in work.concepts.all()[:3]],  # limit to 3 tags
                }
            works_dict[work.id]["roles"].add(role_display)

        # 1. Process works directly from work credits
        for credit in obj.work_credits.all():
            add_work_to_dict(credit.work, credit.get_role_display())

        # Convert dictionary to list
        result = list(works_dict.values())

        # Convert roles set to a sorted list for consistent output
        for w in result:
            w["roles"] = sorted(list(w["roles"]))

        # Sort works by year (descending), fallback to 0 if year is None
        result.sort(key=lambda x: x["year"] if x["year"] is not None else 0, reverse=True)
        return result

    def get_participated_publications(self, obj):
        pubs_dict = {}

        def add_pub_to_dict(publication, role_display):
            if publication.id not in pubs_dict:
                pubs_dict[publication.id] = {
                    "id": publication.id,
                    "title": publication.title,
                    "year": publication.year,
                    "media": publication.get_media_display() if hasattr(publication, "get_media_display") else "",
                    "publisher": publication.publisher.name if publication.publisher else "",
                    "isbn": publication.isbn,
                    "note": publication.note,
                    "roles": set(),
                }
            pubs_dict[publication.id]["roles"].add(role_display)

        for credit in obj.publication_credits.all():
            if credit.publication:
                add_pub_to_dict(credit.publication, credit.get_role_display())

        result = list(pubs_dict.values())
        for p in result:
            p["roles"] = sorted(list(p["roles"]))

        result.sort(key=lambda x: x["year"] if x["year"] is not None else 0, reverse=True)
        return result
