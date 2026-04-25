from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import PersonAliasViewSet, PersonLinkViewSet, PersonViewSet

app_name = "person"

router = DefaultRouter()
router.register(r"persons", PersonViewSet, basename="person")
router.register(r"person-aliases", PersonAliasViewSet, basename="personalias")
router.register(r"person-links", PersonLinkViewSet, basename="personlink")

urlpatterns = [
    path("", include(router.urls)),
]
