from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AgentAliasViewSet, AgentLinkViewSet, AgentViewSet

app_name = "agent"

router = DefaultRouter()
router.register(r"agents", AgentViewSet, basename="agent")
router.register(r"agent-aliases", AgentAliasViewSet, basename="agentalias")
router.register(r"agent-links", AgentLinkViewSet, basename="agentlink")

urlpatterns = [
    path("", include(router.urls)),
]
