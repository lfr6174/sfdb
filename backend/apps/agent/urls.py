from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import PersonViewSet

app_name = "agent"

router = DefaultRouter()
router.register(r"persons", PersonViewSet, basename="person")

urlpatterns = [
    path("", include(router.urls)),
]
