from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets

from .models import Agent, AgentAlias, AgentLink
from .serializers import AgentAliasSerializer, AgentDetailSerializer, AgentLinkSerializer, AgentSerializer


class AgentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows agents to be viewed or edited.
    """

    queryset = Agent.objects.annotate(works_count=Count("works", distinct=True)).order_by("-created_at")
    serializer_class = AgentSerializer

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "aliases__name"]
    ordering_fields = ["name", "created_at", "updated_at", "works_count"]
    filterset_fields = ["name", "agent_type"]

    def get_queryset(self):
        qs = super().get_queryset()
        # 動態決定 Prefetch 範圍，避免 List API 提取用不到的龐大資料
        if self.action == "retrieve":
            qs = qs.prefetch_related(
                "work_contributions__work__concepts",
                "publication_contributions__publication__publisher",
            )
        elif self.action == "list":
            qs = qs.prefetch_related(
                "work_contributions__work__concepts",
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


class AgentAliasViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows agent aliases to be viewed or edited independently.
    """

    queryset = AgentAlias.objects.all()
    serializer_class = AgentAliasSerializer


class AgentLinkViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows agent links to be viewed or edited independently.
    """

    queryset = AgentLink.objects.all()
    serializer_class = AgentLinkSerializer
