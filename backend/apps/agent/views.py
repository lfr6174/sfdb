from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets

from apps.core.filters import LimitedSearchFilter

from .models import Agent
from .serializers import AgentDetailSerializer, AgentListSerializer
from .services import agents_with_role


class AgentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Agent.objects.all().order_by("name").distinct()
    serializer_class = AgentListSerializer

    filter_backends = [DjangoFilterBackend, LimitedSearchFilter, filters.OrderingFilter]
    search_fields = ["name", "aliases__name", "about"]
    ordering_fields = ["name", "created_at", "updated_at"]
    filterset_fields = ["agent_type"]

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.prefetch_related("aliases", "links")
        role = self.request.query_params.get("role")
        if role:
            qs = qs.filter(agents_with_role(role))
        return qs

    def get_serializer_class(self):
        if self.action == "retrieve":
            return AgentDetailSerializer
        return AgentListSerializer


class PersonViewSet(AgentViewSet):
    queryset = AgentViewSet.queryset.filter(agent_type=Agent.AgentType.PERSON)
