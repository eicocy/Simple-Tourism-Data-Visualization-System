"""国家模块路由配置。"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.countries.views import (
    CountryAdminViewSet,
    CountryContinentStatsAPIView,
    CountryDetailAPIView,
    CountryInsightDetailAPIView,
    CountryIndicatorImportExcelAPIView,
    CountryIndicatorListAPIView,
    CountryListAPIView,
    LatestCountryMapDataAPIView,
)


# 管理端国家数据接口路由
router = DefaultRouter()
router.register("admin", CountryAdminViewSet, basename="country-admin")


urlpatterns = [
    # 国家列表查询接口
    path("", CountryListAPIView.as_view(), name="country-list"),
    # 国家指标数据查询接口
    path("indicators/", CountryIndicatorListAPIView.as_view(), name="country-indicator-list"),
    # 国家指标 Excel 批量导入接口
    path(
        "indicators/import-excel/",
        CountryIndicatorImportExcelAPIView.as_view(),
        name="country-indicator-import-excel",
    ),
    # 首页世界地图所需数据接口
    path("map-data/", LatestCountryMapDataAPIView.as_view(), name="country-map-data"),
    # 按洲别统计分析接口
    path("continent-stats/", CountryContinentStatsAPIView.as_view(), name="country-continent-stats"),
    # 国家洞察详情接口
    path("<int:pk>/insight/", CountryInsightDetailAPIView.as_view(), name="country-insight-detail"),
    # 国家详情接口
    path("<int:pk>/", CountryDetailAPIView.as_view(), name="country-detail"),
    # 管理端国家增删改查接口
    path("", include(router.urls)),
]
