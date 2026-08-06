"""可视化模块路由配置。"""

from django.urls import path

from apps.visualization.views import MapAgentChatAPIView

urlpatterns = [
    path("agent/chat/", MapAgentChatAPIView.as_view(), name="visualization-agent-chat"),
]
