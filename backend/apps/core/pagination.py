from rest_framework.pagination import PageNumberPagination


class TotalPagesPagination(PageNumberPagination):
    """Adds ``total_pages`` to the paginated response so clients don't
    have to derive it from a hardcoded page size."""

    def get_paginated_response(self, data):
        response = super().get_paginated_response(data)
        response.data["total_pages"] = self.page.paginator.num_pages
        return response

    def get_paginated_response_schema(self, schema):
        schema = super().get_paginated_response_schema(schema)
        schema["properties"]["total_pages"] = {"type": "integer", "example": 5}
        return schema
