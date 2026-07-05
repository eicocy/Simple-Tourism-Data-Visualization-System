"""国家模块序列化器。"""

from rest_framework import serializers

from apps.countries.models import Country, CountryIndicator


class CountrySerializer(serializers.ModelSerializer):
    """国家基础信息序列化器。"""

    class Meta:
        model = Country
        fields = [
            "id",
            "name_zh",
            "name_en",
            "code",
            "continent",
            "capital",
            "language",
            "currency",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class CountrySimpleSerializer(serializers.ModelSerializer):
    """国家简要信息序列化器。"""

    class Meta:
        model = Country
        fields = ["id", "name_zh", "name_en", "code", "continent"]


class CountryIndicatorSerializer(serializers.ModelSerializer):
    """国家指标序列化器。"""

    # 同时输出国家简要信息，便于前端展示
    country_detail = CountrySimpleSerializer(source="country", read_only=True)

    class Meta:
        model = CountryIndicator
        fields = [
            "id",
            "country",
            "country_detail",
            "year",
            "safety_index",
            "cost_index",
            "tourism_index",
            "climate_index",
            "medical_index",
            "visa_index",
            "overall_score",
            "data_source",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "country_detail"]

    def validate_year(self, value):
        """校验年份取值，避免明显异常数据。"""
        if value < 2000 or value > 2100:
            raise serializers.ValidationError("年份必须在 2000 到 2100 之间。")
        return value


class CountryDetailSerializer(serializers.ModelSerializer):
    """国家详情序列化器。"""

    # 在国家详情中嵌套该国家的全部指标信息
    indicators = CountryIndicatorSerializer(many=True, read_only=True)

    class Meta:
        model = Country
        fields = [
            "id",
            "name_zh",
            "name_en",
            "code",
            "continent",
            "capital",
            "language",
            "currency",
            "is_active",
            "created_at",
            "updated_at",
            "indicators",
        ]
