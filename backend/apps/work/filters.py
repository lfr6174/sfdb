import django_filters
from django.db.models import Count

from .models import Work


class WorkFilter(django_filters.FilterSet):
    """Advanced Faceted Search Filter for Work. Supports exact matches and year ranges."""

    year_min = django_filters.NumberFilter(field_name="year", lookup_expr="gte")
    year_max = django_filters.NumberFilter(field_name="year", lookup_expr="lte")
    concepts_in = django_filters.CharFilter(method="filter_concepts_include")

    genre = django_filters.CharFilter(method="filter_genre")
    work_length = django_filters.CharFilter(method="filter_work_length")
    publication = django_filters.NumberFilter(
        field_name="manifestations__publication__id", lookup_expr="exact", distinct=True
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

        concept_ids = list(set([int(c_id) for c_id in value.split(",") if c_id.isdigit()]))
        if not concept_ids:
            return queryset

        return (
            queryset.filter(concepts__id__in=concept_ids)
            .annotate(matching_concepts=Count("concepts", distinct=True))
            .filter(matching_concepts=len(concept_ids))
        )

    def filter_genre(self, queryset, _name, value):
        if not value:
            return queryset
        types = [v.strip() for v in value.split(",") if v.strip()]
        return queryset.filter(genre__in=types)

    def filter_work_length(self, queryset, _name, value):
        if not value:
            return queryset
        lengths = [v.strip() for v in value.split(",") if v.strip()]
        return queryset.filter(work_length__in=lengths)
