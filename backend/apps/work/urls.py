from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CatalogueViewSet, WorkViewSet

app_name = "work"

router = DefaultRouter()
router.register(r"works", WorkViewSet, basename="work")
router.register(r"catalogues", CatalogueViewSet, basename="catalogue")

urlpatterns = [
    path("", include(router.urls)),
]
