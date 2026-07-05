"""推荐模块路由配置。"""

from django.urls import path

from apps.recommendation.views import RecommendationAPIView


urlpatterns = [
    # 旅游国家推荐接口
    path("generate/", RecommendationAPIView.as_view(), name="recommendation-generate"),
]
