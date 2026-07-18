import django_filters
from django.db.models import Count

from .models import Work


class CharInFilter(django_filters.BaseInFilter, django_filters.CharFilter):
    pass


class NumberInFilter(django_filters.BaseInFilter, django_filters.NumberFilter):
    pass


class WorkFilter(django_filters.FilterSet):
    """Advanced Faceted Search Filter for Work. Supports exact matches and year ranges."""

    year_min = django_filters.NumberFilter(field_name="ori_date__year", lookup_expr="gte")
    year_max = django_filters.NumberFilter(field_name="ori_date__year", lookup_expr="lte")
    concepts_in = django_filters.CharFilter(method="filter_concepts_include")

    genre = CharInFilter(lookup_expr="in")
    work_length = CharInFilter(lookup_expr="in")
    provenance = CharInFilter(lookup_expr="in")
    language = CharInFilter(lookup_expr="in")
    encoding_level = CharInFilter(lookup_expr="in")
    publication = NumberInFilter(field_name="manifestations__publication__id", lookup_expr="in", distinct=True)
    publication_name = django_filters.CharFilter(
        field_name="manifestations__publication__title", lookup_expr="icontains", distinct=True
    )
    publication_series = django_filters.NumberFilter(
        field_name="manifestations__publication__series__id", lookup_expr="exact", distinct=True
    )
    publisher = django_filters.NumberFilter(
        field_name="manifestations__publication__publisher__id", lookup_expr="exact", distinct=True
    )
    catalogue = django_filters.CharFilter(
        field_name="work_catalogues__catalogue__title", lookup_expr="exact", distinct=True
    )

    class Meta:
        model = Work
        fields = ["cycle"]

    def filter_concepts_include(self, queryset, _name, value):
        """
        Ensure the work contains ALL the specified concept IDs (AND logic).
        """
        if not value:
            return queryset

        concept_ids = list(set(int(c_id) for c_id in value.split(",") if c_id.isdigit()))[:20]
        if not concept_ids:
            return queryset

        return (
            queryset.filter(concepts__id__in=concept_ids)
            .annotate(matching_concepts=Count("concepts", distinct=True))
            .filter(matching_concepts=len(concept_ids))
        )
