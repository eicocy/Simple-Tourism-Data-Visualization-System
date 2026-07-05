"""推荐模块序列化器。"""

from rest_framework import serializers

from apps.countries.serializers import CountrySimpleSerializer
from apps.recommendation.models import RecommendationRecord, UserPreference


class UserPreferenceSerializer(serializers.ModelSerializer):
    """用户偏好记录序列化器。"""

    class Meta:
        model = UserPreference
        fields = [
            "id",
            "user",
            "preferred_continent",
            "budget_level",
            "safety_weight",
            "cost_weight",
            "climate_weight",
            "medical_weight",
            "visa_weight",
            "remark",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class UserPreferenceCreateSerializer(serializers.ModelSerializer):
    """用户偏好新增序列化器。"""

    class Meta:
        model = UserPreference
        fields = [
            "preferred_continent",
            "budget_level",
            "safety_weight",
            "cost_weight",
            "climate_weight",
            "medical_weight",
            "visa_weight",
            "remark",
        ]


class RecommendationRequestSerializer(serializers.Serializer):
    """推荐接口请求序列化器。"""

    # 用户预算等级，用于预算过滤
    budget_level = serializers.ChoiceField(
        choices=[("low", "低预算"), ("medium", "中等预算"), ("high", "高预算")],
        help_text="用户预算等级，可选 low、medium、high。",
    )
    # 用户偏好的洲别，可为空
    preferred_continent = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="用户偏好的旅游洲别，可为空。",
    )
    # 用户安全需求，用于对安全指数不满足要求的国家进行排序降权
    safety_requirement = serializers.ChoiceField(
        choices=[("normal", "一般安全需求"), ("high", "较高安全需求"), ("strict", "高安全需求")],
        required=False,
        default="high",
        help_text="用户对目的地安全水平的要求，可选 normal、high、strict。",
    )
    # 以下三个字段为兼容现有前端保留，当前推荐算法内部不再使用前端传入权重
    safety_weight = serializers.IntegerField(
        min_value=0,
        max_value=100,
        required=False,
        default=30,
        help_text="为兼容现有前端保留，当前固定权重算法中将忽略该值。",
    )
    ppp_weight = serializers.IntegerField(
        min_value=0,
        max_value=100,
        required=False,
        default=15,
        help_text="为兼容现有前端保留，当前固定权重算法中将忽略该值。",
    )
    happiness_weight = serializers.IntegerField(
        min_value=0,
        max_value=100,
        required=False,
        default=15,
        help_text="为兼容现有前端保留，当前固定权重算法中将忽略该值。",
    )


class RecommendationRecordSerializer(serializers.ModelSerializer):
    """推荐结果记录序列化器。"""

    # 输出国家简要信息，便于前端直接展示推荐卡片
    country_detail = CountrySimpleSerializer(source="country", read_only=True)

    class Meta:
        model = RecommendationRecord
        fields = [
            "id",
            "user",
            "preference",
            "country",
            "country_detail",
            "score",
            "reason",
            "rank",
            "is_viewed",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "country_detail"]


class RecommendationRecordCreateSerializer(serializers.ModelSerializer):
    """推荐结果新增序列化器。"""

    class Meta:
        model = RecommendationRecord
        fields = [
            "user",
            "preference",
            "country",
            "score",
            "reason",
            "rank",
            "is_viewed",
        ]


class RecommendationRecordDetailSerializer(serializers.ModelSerializer):
    """推荐结果详情序列化器。"""

    # 详情场景下输出完整国家信息中的简要内容
    country_detail = CountrySimpleSerializer(source="country", read_only=True)
    # 输出偏好记录中的关键字段，便于查看推荐依据
    preference_detail = UserPreferenceSerializer(source="preference", read_only=True)

    class Meta:
        model = RecommendationRecord
        fields = [
            "id",
            "user",
            "preference",
            "preference_detail",
            "country",
            "country_detail",
            "score",
            "reason",
            "rank",
            "is_viewed",
            "created_at",
        ]
