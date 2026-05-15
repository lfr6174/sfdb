from django.db.models import Prefetch
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets

from .filters import WorkFilter
from .models import Manifestation, Work
from .serializers import (
    WorkDetailSerializer,
    WorkListSerializer,
)


class WorkViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for Works.
    Uses select_related and prefetch_related to heavily optimize SQL queries,
    preventing the N+1 problem when fetching nested relationships.
    """

    serializer_class = WorkDetailSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = WorkFilter
    search_fields = [
        "title",
        "publications__title",
        "contributions__agent__name",
        "contributions__agent__aliases__name",
    ]
    ordering_fields = ["year", "title", "created_at", "updated_at"]

    def get_queryset(self):
        qs = Work.objects.select_related("cycle").order_by("-year", "title").distinct()

        if self.action == "list":
            return qs.prefetch_related("contributions__agent", "contributions__role", "work_concepts__concept")

        return qs.prefetch_related(
            "contributions__agent",
            "contributions__role",
            "work_concepts__concept",
            Prefetch(
                "manifestations",
                queryset=Manifestation.objects.select_related("publication__publisher").prefetch_related(
                    "publication__contributions__agent",
                    "publication__contributions__role",
                    "contributions__agent",
                    "contributions__role",
                ),
                to_attr="prefetched_manifestations",
            ),
            "work_catalogues__catalogue__agents",
        )

    def get_serializer_class(self):
        if self.action == "list":
            return WorkListSerializer
        return WorkDetailSerializer
