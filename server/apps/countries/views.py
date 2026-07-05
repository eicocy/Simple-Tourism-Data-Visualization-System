"""国家模块视图。"""

from rest_framework import filters, status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from apps.countries.models import Country, CountryIndicator
from apps.countries.serializers import (
    CountryDetailSerializer,
    CountryIndicatorSerializer,
    CountrySerializer,
)
from apps.recommendation.recommendation import TravelRecommendationEngine
from apps.recommendation.tourism_suitability import TourismSuitabilityCalculator


def build_indicator_payload(indicator):
    """将国家指标记录转换为前端分析页面需要的数据结构。"""
    raw_visa_score = (
        float(indicator.visa_index)
        if float(indicator.visa_index) != 50.0
        else float(indicator.tourism_index)
    )
    country_payload = {
        "country_id": indicator.country.id,
        "country_name": indicator.country.name_zh,
        "country_name_en": indicator.country.name_en,
        "continent": indicator.country.continent,
        "raw_visa_score": raw_visa_score,
        "visa_index": float(indicator.visa_index),
        "tourism_index": float(indicator.tourism_index),
        "safety_index": float(indicator.safety_index),
        "cost_index": float(indicator.cost_index),
        "happiness_index": float(indicator.overall_score),
    }
    tourism_detail = TourismSuitabilityCalculator.build_detail(country_payload)
    country_payload["tourism_index"] = tourism_detail["tourism_index"]
    recommendation_index = TravelRecommendationEngine.calculate_default_recommendation_index(
        country_payload
    )
    return {
        "country_id": indicator.country.id,
        "country_name": indicator.country.name_zh,
        "country_name_en": indicator.country.name_en,
        "code": indicator.country.code,
        "continent": indicator.country.continent,
        "capital": indicator.country.capital,
        "language": indicator.country.language,
        "currency": indicator.country.currency,
        "year": indicator.year,
        "recommendation_index": recommendation_index,
        "tourism_index": round(float(tourism_detail["tourism_index"]), 2),
        "tourism_detail": tourism_detail,
        "safety_index": round(float(indicator.safety_index), 2),
        "ppp_index": round(float(indicator.cost_index), 2),
        "cost_index": round(float(indicator.cost_index), 2),
        "happiness_index": round(float(indicator.overall_score), 2),
        "visa_index": round(float(raw_visa_score), 2),
        "overall_score": round(float(indicator.overall_score), 2),
        "data_source": indicator.data_source,
    }


class CountryListAPIView(ListAPIView):
    """国家列表查询接口。"""

    serializer_class = CountrySerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name_zh", "name_en", "code", "continent"]
    ordering_fields = ["created_at", "name_zh"]
    ordering = ["name_zh"]

    def get_queryset(self):
        """获取国家列表查询集，并支持按洲别筛选。"""
        queryset = Country.objects.filter(is_active=True)
        continent = self.request.query_params.get("continent")
        if continent:
            queryset = queryset.filter(continent=continent)
        return queryset


class CountryDetailAPIView(RetrieveAPIView):
    """国家详情接口。"""

    serializer_class = CountryDetailSerializer
    permission_classes = [AllowAny]
    queryset = Country.objects.filter(is_active=True)


class CountryIndicatorListAPIView(ListAPIView):
    """国家指标数据查询接口。"""

    serializer_class = CountryIndicatorSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["year", "overall_score", "safety_index", "tourism_index"]
    ordering = ["-year", "-overall_score"]

    def get_queryset(self):
        """获取国家指标查询集，并支持按国家与年份筛选。"""
        queryset = CountryIndicator.objects.select_related("country").filter(
            country__is_active=True
        )

        country_id = self.request.query_params.get("country")
        if country_id:
            queryset = queryset.filter(country_id=country_id)

        year = self.request.query_params.get("year")
        if year:
            queryset = queryset.filter(year=year)

        return queryset


class LatestCountryMapDataAPIView(APIView):
    """首页世界地图所需的国家指标数据接口。"""

    permission_classes = [AllowAny]

    def get(self, request):
        """返回最新年份的国家指标数据，供前端地图可视化使用。"""
        latest_year = CountryIndicator.objects.order_by("-year").values_list(
            "year", flat=True
        ).first()
        if latest_year is None:
            return Response(
                {
                    "code": 200,
                    "message": "暂无国家指标数据",
                    "data": {
                        "year": None,
                        "results": [],
                    },
                },
                status=status.HTTP_200_OK,
            )

        indicators = CountryIndicator.objects.select_related("country").filter(
            year=latest_year,
            country__is_active=True,
        ).order_by("-tourism_index", "-safety_index", "country__name_en")

        results = []
        for indicator in indicators:
            results.append(build_indicator_payload(indicator))

        return Response(
            {
                "code": 200,
                "message": "获取地图数据成功",
                "data": {
                    "year": latest_year,
                    "results": results,
                },
            },
            status=status.HTTP_200_OK,
        )


class CountryContinentStatsAPIView(APIView):
    """按洲别统计国家指标数据接口。"""

    permission_classes = [AllowAny]

    def get(self, request):
        """返回最新年份下各洲国家数量与平均指标。"""
        latest_year = CountryIndicator.objects.order_by("-year").values_list(
            "year", flat=True
        ).first()
        if latest_year is None:
            return Response(
                {
                    "code": 200,
                    "message": "暂无国家指标数据",
                    "data": {"year": None, "results": []},
                },
                status=status.HTTP_200_OK,
            )

        indicators = CountryIndicator.objects.select_related("country").filter(
            year=latest_year,
            country__is_active=True,
        )
        stats_map = {}
        for indicator in indicators:
            payload = build_indicator_payload(indicator)
            continent = payload["continent"] or "未分类"
            if continent not in stats_map:
                stats_map[continent] = {
                    "continent": continent,
                    "country_count": 0,
                    "recommendation_sum": 0,
                    "tourism_sum": 0,
                    "safety_sum": 0,
                    "cost_sum": 0,
                    "happiness_sum": 0,
                }

            item = stats_map[continent]
            item["country_count"] += 1
            item["recommendation_sum"] += payload["recommendation_index"]
            item["tourism_sum"] += payload["tourism_index"]
            item["safety_sum"] += payload["safety_index"]
            item["cost_sum"] += payload["cost_index"]
            item["happiness_sum"] += payload["happiness_index"]

        results = []
        for item in stats_map.values():
            count = item["country_count"] or 1
            results.append(
                {
                    "continent": item["continent"],
                    "country_count": item["country_count"],
                    "avg_recommendation_index": round(item["recommendation_sum"] / count, 2),
                    "avg_tourism_index": round(item["tourism_sum"] / count, 2),
                    "avg_safety_index": round(item["safety_sum"] / count, 2),
                    "avg_cost_index": round(item["cost_sum"] / count, 2),
                    "avg_happiness_index": round(item["happiness_sum"] / count, 2),
                }
            )

        results.sort(key=lambda item: item["avg_recommendation_index"], reverse=True)
        return Response(
            {
                "code": 200,
                "message": "获取洲别统计成功",
                "data": {"year": latest_year, "results": results},
            },
            status=status.HTTP_200_OK,
        )


class CountryInsightDetailAPIView(APIView):
    """国家洞察详情接口。"""

    permission_classes = [AllowAny]

    def get(self, request, pk):
        """返回指定国家的基础资料、最新指标和历史指标。"""
        country = get_object_or_404(Country.objects.filter(is_active=True), pk=pk)
        latest_indicator = (
            CountryIndicator.objects.select_related("country")
            .filter(country=country)
            .order_by("-year")
            .first()
        )
        if latest_indicator is None:
            return Response(
                {
                    "code": 404,
                    "message": "该国家暂无指标数据",
                    "data": None,
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        history = [
            build_indicator_payload(indicator)
            for indicator in CountryIndicator.objects.select_related("country")
            .filter(country=country)
            .order_by("year")
        ]
        return Response(
            {
                "code": 200,
                "message": "获取国家洞察详情成功",
                "data": {
                    "country": {
                        "id": country.id,
                        "name_zh": country.name_zh,
                        "name_en": country.name_en,
                        "code": country.code,
                        "continent": country.continent,
                        "capital": country.capital,
                        "language": country.language,
                        "currency": country.currency,
                    },
                    "latest_indicator": build_indicator_payload(latest_indicator),
                    "history": history,
                },
            },
            status=status.HTTP_200_OK,
        )


class CountryAdminViewSet(ModelViewSet):
    """管理端国家数据增删改查接口。"""

    serializer_class = CountrySerializer
    permission_classes = [IsAdminUser]
    queryset = Country.objects.all().order_by("name_zh")
