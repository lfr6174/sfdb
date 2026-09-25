from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CatalogueViewSet, RoleViewSet, WorkViewSet

app_name = "work"

router = DefaultRouter()
router.register(r"works", WorkViewSet, basename="work")
router.register(r"catalogues", CatalogueViewSet, basename="catalogue")
router.register(r"roles", RoleViewSet, basename="role")

urlpatterns = [
    path("", include(router.urls)),
]
