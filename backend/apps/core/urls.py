from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"settings", views.SiteSettingViewSet, basename="settings")

urlpatterns = [
    path("", include(router.urls)),
]
