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
    WorkBriefSerializer,
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

    def get_queryset(self):
        qs = Work.objects.select_related("series").order_by("-year", "title")

        if self.action == "list":
            # 列表頁只需要參與人員來組成 byline，避免抓取過多無用資料
            return qs.prefetch_related("credits__person")

        # Detail 頁面才抓取所有的深層巢狀關聯
        return qs.prefetch_related(
            "credits__person",
            "work_concepts__concept",
            "publications",
            "publications__works",
            "publications__publisher",
            "publications__credits__person",
            "catalogue_entries__catalogue__curator",
        )

    def get_serializer_class(self):
        if self.action == "list":
            return WorkBriefSerializer
        return super().get_serializer_class()


class PublisherViewSet(viewsets.ModelViewSet):
    queryset = Publisher.objects.annotate(works_count=Count("publications__works", distinct=True)).order_by("name")
    serializer_class = PublisherSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name"]
    ordering_fields = ["name", "created_at", "updated_at", "works_count"]


class PublicationViewSet(viewsets.ModelViewSet):
    queryset = (
        Publication.objects.select_related("publisher")
        .prefetch_related("credits__person", "works")
        .order_by("year", "title")
    )
    serializer_class = PublicationSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["year", "publisher", "works"]
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
