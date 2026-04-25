from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ConceptGroupViewSet, ConceptLinkViewSet, ConceptViewSet

app_name = "concept"

router = DefaultRouter()
router.register(r"concept-groups", ConceptGroupViewSet, basename="conceptgroup")
router.register(r"concepts", ConceptViewSet, basename="concept")
router.register(r"concept-links", ConceptLinkViewSet, basename="conceptlink")

urlpatterns = [
    path("", include(router.urls)),
]
