from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets

from .models import Concept, ConceptGroup, ConceptLink
from .serializers import ConceptGroupSerializer, ConceptLinkSerializer, ConceptSerializer


class ConceptGroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Concept Groups.
    """

    queryset = ConceptGroup.objects.all().order_by("category", "name")
    serializer_class = ConceptGroupSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["category"]
    search_fields = ["name"]


class ConceptViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Concepts.
    Uses `slug` as the lookup field instead of `pk` (ID).
    """

    queryset = Concept.objects.all().order_by("category", "name")
    serializer_class = ConceptSerializer
    lookup_field = "slug"  # Change the default /id/ URL to /slug/

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["category", "group"]
    search_fields = ["name", "slug", "description"]
    ordering_fields = ["name", "created_at"]


class ConceptLinkViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Concept Links.
    """

    queryset = ConceptLink.objects.all()
    serializer_class = ConceptLinkSerializer
