from import_export.resources import ModelResource

from .models import Publication, Work


class WorkResource(ModelResource):
    """force_init_instance: every row creates a new Work, never matches an existing one."""

    class Meta:
        model = Work
        fields = (
            "title",
            "genre",
            "work_length",
            "provenance",
            "language",
            "ori_date",
            "ori_date_precision",
            "description",
        )
        force_init_instance = True
        clean_model_instances = True  # runs full_clean(): rejects invalid genre/precision values


class PublicationResource(ModelResource):
    """force_init_instance: every row creates a new Publication, never matches an existing one."""

    class Meta:
        model = Publication
        fields = (
            "title",
            "subtitle",
            "language",
            "source",
            "media",
            "binding",
            "pub_date",
            "pub_date_precision",
            "isbn",
            "note",
        )
        force_init_instance = True
        clean_model_instances = True  # runs full_clean(): rejects bad ISBNs and source/media/binding combos
