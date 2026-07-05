"""重新计算数据库中的旅游适宜指数。"""

import os
import sys
from decimal import Decimal
from pathlib import Path


# 将 server 目录加入 Python 路径，便于脚本独立执行
BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django  # noqa: E402

django.setup()

from apps.countries.models import CountryIndicator  # noqa: E402
from apps.recommendation.tourism_suitability import TourismSuitabilityCalculator  # noqa: E402


def decimal_from_float(value):
    """将浮点分值转换为数据库 Decimal。"""
    return Decimal(str(value)).quantize(Decimal("0.01"))


def get_raw_visa_score(indicator):
    """获取原始签证便利分。"""
    # 旧版本曾将签证便利分直接写入 tourism_index，因此第一次重算时需要先保存到 visa_index。
    if indicator.visa_index == Decimal("50.00") and indicator.tourism_index != Decimal("50.00"):
        return indicator.tourism_index
    return indicator.visa_index


def main():
    """批量重算全部国家指标的旅游适宜指数。"""
    updated_count = 0

    queryset = CountryIndicator.objects.select_related("country").all()
    for indicator in queryset:
        raw_visa_score = get_raw_visa_score(indicator)
        country_payload = {
            "country_id": indicator.country.id,
            "country_name": indicator.country.name_zh,
            "country_name_en": indicator.country.name_en,
            "continent": indicator.country.continent,
            "raw_visa_score": float(raw_visa_score),
            "visa_index": float(raw_visa_score),
            "tourism_index": float(indicator.tourism_index),
            "safety_index": float(indicator.safety_index),
            "cost_index": float(indicator.cost_index),
            "happiness_index": float(indicator.overall_score),
        }
        tourism_detail = TourismSuitabilityCalculator.build_detail(country_payload)
        new_tourism_index = decimal_from_float(tourism_detail["tourism_index"])

        indicator.visa_index = raw_visa_score
        indicator.tourism_index = new_tourism_index
        if indicator.data_source:
            if "旅游适宜指数算法重算" not in indicator.data_source:
                indicator.data_source = f"{indicator.data_source}；旅游适宜指数算法重算"
        else:
            indicator.data_source = "旅游适宜指数算法重算"

        indicator.save(
            update_fields=["visa_index", "tourism_index", "data_source", "updated_at"]
        )
        updated_count += 1

    print(f"旅游适宜指数重算完成，更新记录数：{updated_count}")


if __name__ == "__main__":
    main()
