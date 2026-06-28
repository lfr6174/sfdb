from django.db.models import Prefetch
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets

from apps.core.filters import LimitedSearchFilter

from .filters import WorkFilter
from .models import Catalogue, Manifestation, Work, WorkCatalogue, WorkRelation
from .serializers import (
    CatalogueBriefSerializer,
    WorkDetailSerializer,
    WorkListSerializer,
)


class CatalogueViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Catalogue.objects.order_by("catalogue_type", "title")
    serializer_class = CatalogueBriefSerializer
    pagination_class = None


class WorkViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = WorkDetailSerializer
    filter_backends = [DjangoFilterBackend, LimitedSearchFilter, filters.OrderingFilter]
    filterset_class = WorkFilter
    search_fields = [
        "title",
        "publications__title",
        "contributions__agent__name",
        "contributions__agent__aliases__name",
    ]
    ordering_fields = ["ori_date", "title", "created_at", "updated_at"]

    def get_queryset(self):
        qs = Work.objects.select_related("cycle").order_by("-ori_date", "title").distinct()

        if self.action == "list":
            return qs.prefetch_related("contributions__agent", "contributions__role", "work_concepts__concept")

        return qs.prefetch_related(
            "contributions__agent",
            "contributions__role",
            "work_concepts__concept",
            Prefetch(
                "rels_as_subject",
                queryset=WorkRelation.objects.select_related("object_work"),
                to_attr="prefetched_rels_as_subject",
            ),
            Prefetch(
                "rels_as_object",
                queryset=WorkRelation.objects.select_related("subject_work"),
                to_attr="prefetched_rels_as_object",
            ),
            Prefetch(
                "manifestations",
                queryset=Manifestation.objects.select_related(
                    "publication__publisher", "publication__series"
                ).prefetch_related(
                    "publication__contributions__agent",
                    "publication__contributions__role",
                    "contributions__agent",
                    "contributions__role",
                ),
                to_attr="prefetched_manifestations",
            ),
            Prefetch(
                "work_catalogues",
                queryset=WorkCatalogue.objects.select_related("catalogue", "category"),
            ),
        )

    def get_serializer_class(self):
        if self.action == "list":
            return WorkListSerializer
        return WorkDetailSerializer
