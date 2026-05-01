from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ConceptViewSet

app_name = "concept"

router = DefaultRouter()
router.register(r"concepts", ConceptViewSet, basename="concept")

urlpatterns = [
    path("", include(router.urls)),
]
