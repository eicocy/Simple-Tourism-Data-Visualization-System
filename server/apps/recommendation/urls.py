"""推荐模块路由配置。"""

from django.urls import path

from apps.recommendation.views import (
    RecommendationAPIView,
    RecommendationExplanationAPIView,
    RecommendationExportExcelAPIView,
)


urlpatterns = [
    # 旅游国家推荐接口
    path("generate/", RecommendationAPIView.as_view(), name="recommendation-generate"),
    path("export/", RecommendationExportExcelAPIView.as_view(), name="recommendation-export"),
    path(
        "explanation/<int:country_id>/",
        RecommendationExplanationAPIView.as_view(),
        name="recommendation-explanation",
    ),
]
