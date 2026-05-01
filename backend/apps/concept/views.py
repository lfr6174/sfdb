from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.work.serializers import WorkBriefSerializer

from .models import Concept, ConceptLink
from .serializers import ConceptLinkSerializer, ConceptMinimalSerializer, ConceptSerializer
from .services import get_random_concept_with_works


class ConceptViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Concepts.
    Uses `slug` as the lookup field instead of `pk` (ID).
    """

    queryset = Concept.objects.annotate(works_count=Count("works", distinct=True)).order_by("category", "name")
    serializer_class = ConceptSerializer
    lookup_field = "slug"  # Change the default /id/ URL to /slug/

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["category"]
    search_fields = ["name", "slug"]
    ordering_fields = ["name", "created_at", "updated_at", "works_count"]

    @action(detail=False, methods=["get"], url_path="random")
    def random(self, request):
        """Return a random concept with associated works."""
        concept = get_random_concept_with_works()

        if not concept:
            return Response({"detail": "No concepts found."}, status=404)

        data = ConceptMinimalSerializer(concept).data
        data["random_works"] = WorkBriefSerializer(concept.random_works, many=True).data

        return Response(data)

    @action(detail=False, methods=["get"], url_path="all")
    def all(self, request):
        """
        Retrieve all concepts without pagination.
        Useful for the frontend Concept Hub.
        """
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ConceptLinkViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Concept Links.
    """

    queryset = ConceptLink.objects.all()
    serializer_class = ConceptLinkSerializer
