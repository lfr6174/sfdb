from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets

from .models import Person, PersonAlias, PersonLink
from .serializers import PersonAliasSerializer, PersonLinkSerializer, PersonSerializer


class PersonViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows persons to be viewed or edited.

    Supported query parameters:
    - `search`: Performs a case-insensitive partial match on `name` and `aliases__name`.
    - `name`: Performs an exact match filter on the `name` field.
    - `ordering`: Sorts the results. Allowed fields are `name`, `created_at`, `updated_at`.
      Prefix with a minus sign (-) for descending order.
    """

    queryset = Person.objects.all().order_by("-created_at")
    serializer_class = PersonSerializer

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "aliases__name"]
    ordering_fields = ["name", "created_at", "updated_at"]
    filterset_fields = ["name"]


class PersonAliasViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows person aliases to be viewed or edited independently.
    """

    queryset = PersonAlias.objects.all()
    serializer_class = PersonAliasSerializer


class PersonLinkViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows person links to be viewed or edited independently.
    """

    queryset = PersonLink.objects.all()
    serializer_class = PersonLinkSerializer
