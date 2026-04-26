from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Concept, ConceptGroup, ConceptLink
from .serializers import ConceptGroupSerializer, ConceptLinkSerializer, ConceptSerializer


class ConceptGroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Concept Groups.
    """

    queryset = ConceptGroup.objects.all().order_by("category", "name")
    serializer_class = ConceptGroupSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["category"]
    search_fields = ["name"]
    ordering_fields = ["name", "category", "created_at", "updated_at"]


class ConceptViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Concepts.
    Uses `slug` as the lookup field instead of `pk` (ID).
    """

    queryset = Concept.objects.annotate(works_count=Count("works", distinct=True)).order_by("category", "name")
    serializer_class = ConceptSerializer
    lookup_field = "slug"  # Change the default /id/ URL to /slug/

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["category", "group"]
    search_fields = ["name", "slug"]
    ordering_fields = ["name", "created_at", "updated_at", "works_count"]

    @action(detail=False, methods=["get"], url_path="random-spotlight")
    def random_spotlight(self, request):
        """
        Retrieve works for a random concept that has at least one associated work.
        Useful for the homepage spotlight section.
        """
        # Filter out concepts with no works (works_count > 0) and order randomly ("?")
        concept = self.get_queryset().filter(works_count__gt=0).order_by("?").first()

        if not concept:
            return Response({"detail": "No concepts available with associated works."}, status=404)

        data = self.get_serializer(concept).data

        # Imported here to avoid circular imports with apps.work
        # TODO: support specifing extract work count
        from apps.work.serializers import WorkBriefSerializer

        works = concept.works.prefetch_related("credits__person").order_by("-year", "title")[:4]
        data["spotlight_works"] = WorkBriefSerializer(works, many=True).data

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
