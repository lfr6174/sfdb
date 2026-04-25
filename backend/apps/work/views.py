from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets

from .models import Catalogue, Publication, Publisher, Series, Work
from .serializers import (
    CatalogueSerializer,
    PublicationSerializer,
    PublisherSerializer,
    SeriesSerializer,
    WorkSerializer,
)


class SeriesViewSet(viewsets.ModelViewSet):
    queryset = Series.objects.all().order_by("title")
    serializer_class = SeriesSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["title"]


class WorkViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Works.
    Uses select_related and prefetch_related to heavily optimize SQL queries,
    preventing the N+1 problem when fetching nested relationships.
    """

    queryset = (
        Work.objects.select_related("series")
        .prefetch_related(
            "credits__person",
            "work_concepts__concept",
            "publications__publisher",
            "publications__credits__person",
        )
        .order_by("-year", "title")
    )

    serializer_class = WorkSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["media_type", "work_length", "year", "series"]
    search_fields = ["title", "publications__title", "credits__person__name", "credits__person__aliases__name"]
    ordering_fields = ["year", "title", "created_at"]


class PublisherViewSet(viewsets.ModelViewSet):
    queryset = Publisher.objects.all().order_by("name")
    serializer_class = PublisherSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]


class PublicationViewSet(viewsets.ModelViewSet):
    queryset = (
        Publication.objects.select_related("work", "publisher")
        .prefetch_related("credits__person")
        .order_by("year", "title")
    )
    serializer_class = PublicationSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["year", "publisher", "work"]
    search_fields = ["title", "isbn"]
    ordering_fields = ["year", "title", "created_at"]


class CatalogueViewSet(viewsets.ModelViewSet):
    queryset = Catalogue.objects.select_related("curator").prefetch_related("entries__work").order_by("-year", "title")
    serializer_class = CatalogueSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["catalogue_type", "year"]
    search_fields = ["title"]
    ordering_fields = ["year", "title"]
