from django.db.models import F
from rest_framework import filters


class LimitedSearchFilter(filters.SearchFilter):
    """SearchFilter that truncates terms to 200 chars before they reach the DB.

    A search term longer than ~200 chars gives no useful results but generates
    a wide LIKE '%...%' scan across joined tables. Truncating is cheaper than
    rejecting: the client gets a valid (empty) response instead of a 400.
    """

    MAX_TERM_LENGTH = 200

    def get_search_terms(self, request):
        terms = super().get_search_terms(request)
        if terms:
            return [term[: self.MAX_TERM_LENGTH] for term in terms]
        return terms


class NullsLastOrderingFilter(filters.OrderingFilter):
    """OrderingFilter that sorts NULLs last in both directions.

    PostgreSQL and SQLite default NULLs to opposite ends, so a nullable sort
    field leads with blank rows in one direction on each backend.
    """

    def filter_queryset(self, request, queryset, view):
        ordering = self.get_ordering(request, queryset, view)
        if not ordering:
            return queryset
        return queryset.order_by(
            *[
                F(field[1:]).desc(nulls_last=True) if field.startswith("-") else F(field).asc(nulls_last=True)
                for field in ordering
            ]
        )
