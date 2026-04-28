from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets

from .filters import WorkFilter
from .models import Catalogue, Publication, Publisher, Series, Work
from .serializers import (
    CatalogueSerializer,
    PublicationSerializer,
    PublisherSerializer,
    SeriesSerializer,
    WorkSerializer,
)


class SeriesViewSet(viewsets.ModelViewSet):
    queryset = Series.objects.annotate(works_count=Count("works", distinct=True)).order_by("title")
    serializer_class = SeriesSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title"]
    ordering_fields = ["title", "created_at", "updated_at", "works_count"]


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
            "catalogue_entries__catalogue__curator",
        )
        .order_by("-year", "title")
    )

    serializer_class = WorkSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = WorkFilter
    search_fields = [
        "title",
        "publications__title",
        "credits__person__name",
        "credits__person__aliases__name",
        "publications__credits__person__name",
        "publications__credits__person__aliases__name",
    ]
    ordering_fields = ["year", "title", "created_at", "updated_at"]


class PublisherViewSet(viewsets.ModelViewSet):
    queryset = Publisher.objects.annotate(works_count=Count("publications__work", distinct=True)).order_by("name")
    serializer_class = PublisherSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name"]
    ordering_fields = ["name", "created_at", "updated_at", "works_count"]


class PublicationViewSet(viewsets.ModelViewSet):
    queryset = (
        Publication.objects.select_related("work", "publisher")
        .prefetch_related("credits__person")
        .order_by("year", "title")
    )
    serializer_class = PublicationSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["year", "publisher", "work"]
    search_fields = [
        "title",
        "isbn",
        "credits__person__name",
        "credits__person__aliases__name",
    ]
    ordering_fields = ["year", "title", "created_at", "updated_at"]


class CatalogueViewSet(viewsets.ModelViewSet):
    queryset = (
        Catalogue.objects.select_related("curator")
        .prefetch_related("entries__work", "entries__work__credits__person")
        .annotate(works_count=Count("entries", distinct=True))
        .order_by("-year", "title")
    )
    serializer_class = CatalogueSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["catalogue_type", "year"]
    search_fields = ["title"]
    ordering_fields = ["year", "title", "created_at", "updated_at", "works_count"]
