from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets

from .models import Agent, AgentAlias, AgentLink
from .serializers import AgentAliasSerializer, AgentDetailSerializer, AgentLinkSerializer, AgentSerializer


class AgentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows agents to be viewed or edited.
    """

    queryset = (
        Agent.objects.annotate(works_count=Count("works", distinct=True))
        .prefetch_related(
            "work_credits",
            "publication_credits",
            "work_credits__work__concepts",
            "publication_credits__publication__publisher",
        )
        .order_by("-created_at")
    )
    serializer_class = AgentSerializer

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "aliases__name"]
    ordering_fields = ["name", "created_at", "updated_at", "works_count"]
    filterset_fields = ["name", "agent_type"]

    def get_serializer_class(self):
        # Use detailed serializer with works list for single agent retrieve actions
        if self.action == "retrieve":
            return AgentDetailSerializer
        return super().get_serializer_class()


class AgentAliasViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows agent aliases to be viewed or edited independently.
    """

    queryset = AgentAlias.objects.all()
    serializer_class = AgentAliasSerializer


class AgentLinkViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows agent links to be viewed or edited independently.
    """

    queryset = AgentLink.objects.all()
    serializer_class = AgentLinkSerializer
