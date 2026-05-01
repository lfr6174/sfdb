from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AgentViewSet

app_name = "agent"

router = DefaultRouter()
router.register(r"agents", AgentViewSet, basename="agent")

urlpatterns = [
    path("", include(router.urls)),
]
