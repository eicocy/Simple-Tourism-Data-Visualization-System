"""系统模块路由配置。"""

from django.urls import path

from apps.system.views import OperationLogListAPIView


urlpatterns = [
    path("operation-logs/", OperationLogListAPIView.as_view(), name="operation-log-list"),
]
