"""用户模块测试。"""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.countries.models import Country, CountryIndicator
from apps.recommendation.models import RecommendationRecord, UserPreference
from apps.users.views import build_recommendation_trend


class AdminReportTrendTests(TestCase):
    """后台推荐趋势统计测试。"""

    def test_recommendation_trend_counts_each_generate_once(self):
        """一次推荐生成多条国家结果时，趋势只统计一次推荐。"""
        user = get_user_model().objects.create_user(
            username="trend_user",
            password="test-pass-123",
        )
        preference = UserPreference.objects.create(
            user=user,
            preferred_continent="亚洲",
            budget_level="medium",
        )

        for index in range(10):
            country = Country.objects.create(
                name_zh=f"测试国家{index}",
                name_en=f"TrendCountry{index}",
                code=f"TC{index}",
                continent="亚洲",
            )
            CountryIndicator.objects.create(
                country=country,
                year=2026,
                safety_index=Decimal("80.00"),
                cost_index=Decimal("50.00"),
                tourism_index=Decimal("75.00"),
                climate_index=Decimal("60.00"),
                medical_index=Decimal("70.00"),
                visa_index=Decimal("65.00"),
                overall_score=Decimal("78.00"),
            )
            RecommendationRecord.objects.create(
                user=user,
                preference=preference,
                country=country,
                score=Decimal("88.00"),
                reason="测试推荐",
                rank=index + 1,
            )

        trend = build_recommendation_trend(days=1)

        self.assertEqual(trend[0]["count"], 1)
