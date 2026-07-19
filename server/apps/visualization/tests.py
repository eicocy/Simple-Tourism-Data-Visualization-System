"""可视化模块测试。"""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.countries.models import Country, CountryIndicator


class MapAgentChatAPITests(APITestCase):
    """智能地图助手接口测试。"""

    def setUp(self):
        """准备国家指标测试数据。"""
        self.user = get_user_model().objects.create_user(
            username="map_agent_user",
            password="test-pass-123",
        )
        self.url = reverse("visualization-agent-chat")

        switzerland = Country.objects.create(
            name_zh="瑞士",
            name_en="Switzerland",
            code="CH",
            continent="欧洲",
        )
        ukraine = Country.objects.create(
            name_zh="乌克兰",
            name_en="Ukraine",
            code="UA",
            continent="欧洲",
        )
        nigeria = Country.objects.create(
            name_zh="尼日利亚",
            name_en="Nigeria",
            code="NG",
            continent="非洲",
        )
        CountryIndicator.objects.create(
            country=switzerland,
            year=2026,
            safety_index=Decimal("92.00"),
            cost_index=Decimal("75.00"),
            tourism_index=Decimal("95.00"),
            climate_index=Decimal("80.00"),
            medical_index=Decimal("90.00"),
            visa_index=Decimal("78.00"),
            overall_score=Decimal("88.00"),
        )
        CountryIndicator.objects.create(
            country=ukraine,
            year=2026,
            safety_index=Decimal("35.00"),
            cost_index=Decimal("45.00"),
            tourism_index=Decimal("60.00"),
            climate_index=Decimal("60.00"),
            medical_index=Decimal("55.00"),
            visa_index=Decimal("50.00"),
            overall_score=Decimal("52.00"),
        )
        CountryIndicator.objects.create(
            country=nigeria,
            year=2026,
            safety_index=Decimal("58.00"),
            cost_index=Decimal("42.00"),
            tourism_index=Decimal("62.00"),
            climate_index=Decimal("64.00"),
            medical_index=Decimal("48.00"),
            visa_index=Decimal("50.00"),
            overall_score=Decimal("58.00"),
        )

    def test_requires_login(self):
        """未登录用户不能调用智能地图助手。"""
        response = self.client.post(self.url, {"message": "I want mountain in Europe"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_recommends_europe_mountain_destinations(self):
        """山景偏好会返回欧洲推荐标注。"""
        self.client.force_authenticate(self.user)

        response = self.client.post(self.url, {"message": "I want mountain in Europe"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data["data"]
        self.assertEqual(data["intent"], "scenery_mountain")
        self.assertEqual(data["map_targets"][0]["country_name_en"], "Switzerland")
        self.assertEqual(data["map_targets"][0]["category"], "recommendation")

    def test_marks_conflict_risk_destinations(self):
        """战事查询会返回风险标注和不推荐理由。"""
        self.client.force_authenticate(self.user)

        response = self.client.post(self.url, {"message": "war conflict"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data["data"]
        target_names = {item["country_name_en"] for item in data["map_targets"]}
        self.assertEqual(data["intent"], "risk_conflict")
        self.assertIn("Ukraine", target_names)
        self.assertTrue(all(item["category"] == "risk" for item in data["map_targets"]))

    def test_marks_demo_disease_risk_destinations(self):
        """传染病查询会返回内置示例风险标注和官方核验提醒。"""
        self.client.force_authenticate(self.user)

        response = self.client.post(self.url, {"message": "disease epidemic"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data["data"]
        target_names = {item["country_name_en"] for item in data["map_targets"]}
        self.assertEqual(data["intent"], "risk_disease")
        self.assertIn("Nigeria", target_names)
        self.assertIn("不推荐", data["answer"])
        self.assertIn("官方", data["answer"])
