from rest_framework import viewsets

from .models import SiteSetting
from .serializers import SiteSettingSerializer


class SiteSettingViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SiteSetting.objects.filter(is_active=True)
    serializer_class = SiteSettingSerializer
    lookup_field = "key"
