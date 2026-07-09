"""Django 项目主路由配置。"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)


def health_check(_request):
    """提供基础健康检查接口，便于确认后端服务是否正常启动。"""
    return JsonResponse(
        {
            "code": 200,
            "message": "后端服务运行正常",
        }
    )


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", health_check, name="health_check"),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
    path("api/users/", include("apps.users.urls")),
    path("api/countries/", include("apps.countries.urls")),
    path("api/recommendation/", include("apps.recommendation.urls")),
    path("api/visualization/", include("apps.visualization.urls")),
    path("api/system/", include("apps.system.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
