"""Django 项目主路由配置。"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path


def health_check(_request):
    """提供基础健康检查接口，便于确认后端服务是否正常启动。"""
    return JsonResponse(
        {
            "code": 200,
            "message": "后端服务运行正常",
        }
    )


urlpatterns = [
    # Django 后台管理路由
    path("admin/", admin.site.urls),
    # 基础健康检查路由
    path("api/health/", health_check, name="health_check"),
    # 各业务模块总入口，当前仅挂载占位路由
    path("api/users/", include("apps.users.urls")),
    path("api/countries/", include("apps.countries.urls")),
    path("api/recommendation/", include("apps.recommendation.urls")),
    path("api/visualization/", include("apps.visualization.urls")),
    path("api/system/", include("apps.system.urls")),
]

# 开发环境下提供媒体文件访问
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
