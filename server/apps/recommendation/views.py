"""推荐模块视图。"""

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.countries.models import CountryIndicator
from apps.recommendation.models import RecommendationRecord, UserPreference
from apps.recommendation.recommendation import TravelRecommendationEngine
from apps.recommendation.serializers import RecommendationRequestSerializer
from apps.recommendation.tourism_suitability import TourismSuitabilityCalculator


class RecommendationAPIView(APIView):
    """旅游国家推荐接口。"""

    # 推荐接口允许匿名访问
    permission_classes = [AllowAny]

    def post(self, request):
        """接收预算和偏好条件，返回排序后的推荐国家列表。"""
        serializer = RecommendationRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        # 获取最新年份的国家指标数据作为推荐基础
        latest_indicator_year = CountryIndicator.objects.order_by("-year").values_list(
            "year", flat=True
        ).first()
        if latest_indicator_year is None:
            return Response(
                {
                    "code": 400,
                    "message": "当前暂无国家指标数据，无法生成推荐结果",
                    "data": [],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        indicators = CountryIndicator.objects.select_related("country").filter(
            year=latest_indicator_year,
            country__is_active=True,
        )
        if not indicators.exists():
            return Response(
                {
                    "code": 404,
                    "message": "未查询到符合条件的国家数据",
                    "data": [],
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # 将数据库记录转换为独立推荐算法模块需要的输入格式
        countries_data = []
        for indicator in indicators:
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
                "ppp_index": float(indicator.cost_index),
                "happiness_index": float(indicator.overall_score),
            }
            tourism_detail = TourismSuitabilityCalculator.build_detail(country_payload)
            country_payload["tourism_index"] = tourism_detail["tourism_index"]
            country_payload["tourism_detail"] = tourism_detail
            countries_data.append(
                country_payload
            )

        # 调用独立推荐算法模块完成综合评分与排序
        engine = TravelRecommendationEngine(
            countries=countries_data,
            user_preference=validated_data,
        )
        top_recommendations = engine.recommend(top_n=10)

        # 补充年份信息，方便前端展示和论文说明
        for item in top_recommendations:
            item["year"] = latest_indicator_year

        # 如果用户已登录，则保存本次偏好与推荐记录
        if request.user.is_authenticated:
            safety_requirement = validated_data.get("safety_requirement", "high")
            safety_requirement_text = {
                "normal": "一般安全需求",
                "high": "较高安全需求",
                "strict": "高安全需求",
            }.get(safety_requirement, "较高安全需求")
            preference = UserPreference.objects.create(
                user=request.user,
                preferred_continent=validated_data.get("preferred_continent", ""),
                budget_level=validated_data["budget_level"],
                # 以下字段仅为兼容当前数据表结构保留
                safety_weight=30,
                cost_weight=15,
                climate_weight=15,
                medical_weight=40,
                visa_weight=0,
                remark=(
                    "该记录由固定权重旅游推荐算法生成：旅游适宜性40%，安全30%，"
                    f"幸福15%，消费15%；安全需求为{safety_requirement_text}。"
                ),
            )
            for index, item in enumerate(top_recommendations, start=1):
                RecommendationRecord.objects.create(
                    user=request.user,
                    preference=preference,
                    country_id=item["country_id"],
                    score=item["score"],
                    reason=item["reason"],
                    rank=index,
                )

        return Response(
            {
                "code": 200,
                "message": "推荐成功",
                "data": {
                    "year": latest_indicator_year,
                    "count": len(top_recommendations),
                    "results": top_recommendations,
                },
            },
            status=status.HTTP_200_OK,
        )
