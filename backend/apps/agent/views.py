from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets

from .models import Agent
from .serializers import AgentDetailSerializer, AgentSerializer


class AgentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows agents to be viewed or edited.
    """

    queryset = Agent.objects.all().order_by("name").distinct()
    serializer_class = AgentSerializer

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "aliases__name", "about"]
    ordering_fields = ["name", "created_at", "updated_at"]
    filterset_fields = ["agent_type"]

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.prefetch_related("aliases", "links")
        if self.action == "retrieve":
            qs = qs.prefetch_related(
                "work_contributions__work__concepts",
                "publication_contributions__publication__publisher",
            )
        return qs

    def get_serializer_class(self):
        # Use detailed serializer with works list for single agent retrieve actions
        if self.action == "retrieve":
            return AgentDetailSerializer
        return super().get_serializer_class()


class PersonViewSet(AgentViewSet):
    """
    API endpoint that allows persons (Agents of type PERSON) to be viewed or edited.
    """

    queryset = AgentViewSet.queryset.filter(agent_type=Agent.AgentType.PERSON)
