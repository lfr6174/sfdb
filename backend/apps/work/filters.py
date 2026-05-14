import django_filters

from .models import Work


class WorkFilter(django_filters.FilterSet):
    """
    Advanced Faceted Search Filter for Work.
    Supports exact matches, year ranges, and 3-state concept tag filtering (Include/Exclude).
    """

    # 1. Year Range
    year_min = django_filters.NumberFilter(field_name="year", lookup_expr="gte")
    year_max = django_filters.NumberFilter(field_name="year", lookup_expr="lte")

    # 2. 3-state concept tag: Include (AND)
    # Format: ?concepts_in=1,2,3
    concepts_in = django_filters.CharFilter(method="filter_concepts_include")

    # 3. 3-state concept tag: Exclude (NOT)
    # Format: ?concepts_ex=4,5
    concepts_ex = django_filters.CharFilter(method="filter_concepts_exclude")

    media_type = django_filters.CharFilter(method="filter_media_type")
    work_length = django_filters.CharFilter(method="filter_work_length")

    class Meta:
        model = Work
        fields = ["cycle"]

    def filter_concepts_include(self, queryset, _name, value):
        """
        Ensure the work contains ALL the specified concept IDs (AND logic).
        """
        if not value:
            return queryset

        concept_ids = [int(c_id) for c_id in value.split(",") if c_id.isdigit()]
        for c_id in concept_ids:
            queryset = queryset.filter(concepts__id=c_id)
        return queryset.distinct()

    def filter_concepts_exclude(self, queryset, _name, value):
        """
        Ensure the work contains NONE of the specified concept IDs (NOT logic).
        """
        if not value:
            return queryset

        concept_ids = [int(c_id) for c_id in value.split(",") if c_id.isdigit()]
        return queryset.exclude(concepts__id__in=concept_ids)

    def filter_media_type(self, queryset, _name, value):
        if not value:
            return queryset
        types = [v.strip() for v in value.split(",") if v.strip()]
        return queryset.filter(media_type__in=types)

    def filter_work_length(self, queryset, _name, value):
        if not value:
            return queryset
        lengths = [v.strip() for v in value.split(",") if v.strip()]
        return queryset.filter(work_length__in=lengths)
