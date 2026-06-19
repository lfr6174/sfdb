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
