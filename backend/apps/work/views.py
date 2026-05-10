from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets

from .filters import WorkFilter
from .models import Work
from .serializers import (
    WorkBriefSerializer,
    WorkSerializer,
)


class WorkViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for Works.
    Uses select_related and prefetch_related to heavily optimize SQL queries,
    preventing the N+1 problem when fetching nested relationships.
    """

    serializer_class = WorkSerializer
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
        qs = Work.objects.select_related("series").order_by("-year", "title")

        if self.action == "list":
            return qs.prefetch_related("contributions__agent", "contributions__role", "work_concepts__concept")

        return qs.prefetch_related(
            "contributions__agent",
            "contributions__role",
            "work_concepts__concept",
            "publications",
            "publications__works",
            "publications__publisher",
            "publications__contributions__agent",
            "publications__contributions__role",
            "publications__manifestations__work",
            "publications__manifestations__contributions__agent",
            "publications__manifestations__contributions__role",
            "work_catalogues__catalogue",
        )

    def get_serializer_class(self):
        if self.action == "list":
            return WorkBriefSerializer
        return super().get_serializer_class()
