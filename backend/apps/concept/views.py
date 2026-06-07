from django.db.models import Count, Prefetch
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.work.models import WorkConcept
from apps.work.services import get_byline

from .models import Concept
from .serializers import ConceptDetailSerializer, ConceptListSerializer, ConceptMinimalSerializer
from .services import get_random_concept_with_works


class ConceptViewSet(viewsets.ReadOnlyModelViewSet):
    """Concept API. Uses slug as the lookup field."""

    lookup_field = "slug"

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["category"]
    search_fields = ["name"]
    ordering_fields = ["name", "created_at", "updated_at", "works_count"]

    def get_queryset(self):
        qs = Concept.objects.annotate(works_count=Count("works", distinct=True)).order_by("category", "name")

        if self.action == "retrieve":
            qs = qs.prefetch_related(
                "links",
                "related_concepts",
                Prefetch(
                    "work_concepts",
                    queryset=WorkConcept.objects.select_related("work").order_by("-work__ori_date"),
                    to_attr="prefetched_work_concepts",
                ),
            )
        return qs

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ConceptDetailSerializer
        return ConceptListSerializer

    @action(detail=False, methods=["get"], url_path="random")
    def random(self, request):
        """Return a random concept with associated works."""
        concept = get_random_concept_with_works()

        if not concept:
            return Response({"detail": "No concepts found."}, status=404)

        data = ConceptMinimalSerializer(concept).data

        data["random_works"] = [
            {
                "id": w.id,
                "title": w.title,
                "year": w.year,
                "genre_display": w.get_genre_display(),
                "work_length_display": w.get_work_length_display(),
                "byline": get_byline(w.contributions.all()),
            }
            for w in getattr(concept, "random_works", [])
        ]

        return Response(data)

    @action(detail=False, methods=["get"], url_path="all")
    def all(self, request):
        """Return all concepts without pagination."""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = ConceptListSerializer(queryset, many=True)
        return Response(serializer.data)
