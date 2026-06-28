from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

admin.site.site_header = "TSFDB管理"
admin.site.site_title = "TSFDB管理"
admin.site.index_title = "資料"

urlpatterns = [
    path(settings.ADMIN_URL, admin.site.urls),
    # Core APIs
    path("api/", include("apps.core.urls")),
    path("api/", include("apps.agent.urls")),
    path("api/", include("apps.concept.urls")),
    path("api/", include("apps.work.urls")),
    path("api/", include("apps.post.urls")),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        path("__debug__/", include(debug_toolbar.urls)),
        # OpenAPI Schema and API documentation (development only)
        path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
        path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
        path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    ]
