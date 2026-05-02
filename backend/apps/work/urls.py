from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import WorkViewSet

app_name = "work"

router = DefaultRouter()
router.register(r"works", WorkViewSet, basename="work")

urlpatterns = [
    path("", include(router.urls)),
]
