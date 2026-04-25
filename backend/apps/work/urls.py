from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CatalogueViewSet, PublicationViewSet, PublisherViewSet, SeriesViewSet, WorkViewSet

app_name = "work"

router = DefaultRouter()
router.register(r"series", SeriesViewSet, basename="series")
router.register(r"works", WorkViewSet, basename="work")
router.register(r"publishers", PublisherViewSet, basename="publisher")
router.register(r"publications", PublicationViewSet, basename="publication")
router.register(r"catalogues", CatalogueViewSet, basename="catalogue")

urlpatterns = [
    path("", include(router.urls)),
]
