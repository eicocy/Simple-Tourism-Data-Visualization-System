"""毕业设计演示数据初始化脚本。"""

import os
import sys
from decimal import Decimal

import django


# 将 server 目录加入 Python 路径，便于脚本独立执行
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SERVER_DIR = os.path.dirname(CURRENT_DIR)
if SERVER_DIR not in sys.path:
    sys.path.insert(0, SERVER_DIR)

# 指定 Django 配置文件
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.countries.models import Country, CountryIndicator  # noqa: E402


# 演示数据说明：
# 1. 以下数据主要用于本科毕业设计的系统演示与接口联调
# 2. 数据风格尽量接近真实情况，但不作为正式统计结论使用
# 3. 当前模型中没有单独的 ppp_index 和 happiness_index 字段，因此这里做如下映射：
#    - ppp_index -> cost_index
#    - happiness_index -> overall_score
# 4. estimated_cost_level 为演示字段，不直接入库，用于帮助理解消费水平
DEMO_COUNTRY_DATA = [
    {
        "name_zh": "日本",
        "name_en": "Japan",
        "code": "JP",
        "continent": "亚洲",
        "capital": "东京",
        "language": "日语",
        "currency": "日元",
        "safety_index": 88.0,
        "ppp_index": 72.0,
        "happiness_index": 70.0,
        "estimated_cost_level": "较高",
    },
    {
        "name_zh": "韩国",
        "name_en": "South Korea",
        "code": "KR",
        "continent": "亚洲",
        "capital": "首尔",
        "language": "韩语",
        "currency": "韩元",
        "safety_index": 82.0,
        "ppp_index": 68.0,
        "happiness_index": 64.0,
        "estimated_cost_level": "中高",
    },
    {
        "name_zh": "新加坡",
        "name_en": "Singapore",
        "code": "SG",
        "continent": "亚洲",
        "capital": "新加坡",
        "language": "英语",
        "currency": "新加坡元",
        "safety_index": 92.0,
        "ppp_index": 85.0,
        "happiness_index": 78.0,
        "estimated_cost_level": "高",
    },
    {
        "name_zh": "泰国",
        "name_en": "Thailand",
        "code": "TH",
        "continent": "亚洲",
        "capital": "曼谷",
        "language": "泰语",
        "currency": "泰铢",
        "safety_index": 72.0,
        "ppp_index": 45.0,
        "happiness_index": 68.0,
        "estimated_cost_level": "较低",
    },
    {
        "name_zh": "马来西亚",
        "name_en": "Malaysia",
        "code": "MY",
        "continent": "亚洲",
        "capital": "吉隆坡",
        "language": "马来语",
        "currency": "林吉特",
        "safety_index": 76.0,
        "ppp_index": 50.0,
        "happiness_index": 72.0,
        "estimated_cost_level": "较低",
    },
    {
        "name_zh": "阿联酋",
        "name_en": "United Arab Emirates",
        "code": "AE",
        "continent": "亚洲",
        "capital": "阿布扎比",
        "language": "阿拉伯语",
        "currency": "迪拉姆",
        "safety_index": 86.0,
        "ppp_index": 78.0,
        "happiness_index": 71.0,
        "estimated_cost_level": "中高",
    },
    {
        "name_zh": "瑞士",
        "name_en": "Switzerland",
        "code": "CH",
        "continent": "欧洲",
        "capital": "伯尔尼",
        "language": "德语",
        "currency": "瑞士法郎",
        "safety_index": 90.0,
        "ppp_index": 95.0,
        "happiness_index": 84.0,
        "estimated_cost_level": "很高",
    },
    {
        "name_zh": "挪威",
        "name_en": "Norway",
        "code": "NO",
        "continent": "欧洲",
        "capital": "奥斯陆",
        "language": "挪威语",
        "currency": "挪威克朗",
        "safety_index": 91.0,
        "ppp_index": 90.0,
        "happiness_index": 82.0,
        "estimated_cost_level": "很高",
    },
    {
        "name_zh": "德国",
        "name_en": "Germany",
        "code": "DE",
        "continent": "欧洲",
        "capital": "柏林",
        "language": "德语",
        "currency": "欧元",
        "safety_index": 84.0,
        "ppp_index": 73.0,
        "happiness_index": 74.0,
        "estimated_cost_level": "中高",
    },
    {
        "name_zh": "法国",
        "name_en": "France",
        "code": "FR",
        "continent": "欧洲",
        "capital": "巴黎",
        "language": "法语",
        "currency": "欧元",
        "safety_index": 79.0,
        "ppp_index": 76.0,
        "happiness_index": 73.0,
        "estimated_cost_level": "中高",
    },
    {
        "name_zh": "意大利",
        "name_en": "Italy",
        "code": "IT",
        "continent": "欧洲",
        "capital": "罗马",
        "language": "意大利语",
        "currency": "欧元",
        "safety_index": 77.0,
        "ppp_index": 70.0,
        "happiness_index": 69.0,
        "estimated_cost_level": "中等",
    },
    {
        "name_zh": "西班牙",
        "name_en": "Spain",
        "code": "ES",
        "continent": "欧洲",
        "capital": "马德里",
        "language": "西班牙语",
        "currency": "欧元",
        "safety_index": 81.0,
        "ppp_index": 67.0,
        "happiness_index": 72.0,
        "estimated_cost_level": "中等",
    },
    {
        "name_zh": "加拿大",
        "name_en": "Canada",
        "code": "CA",
        "continent": "北美洲",
        "capital": "渥太华",
        "language": "英语",
        "currency": "加元",
        "safety_index": 87.0,
        "ppp_index": 80.0,
        "happiness_index": 79.0,
        "estimated_cost_level": "中高",
    },
    {
        "name_zh": "美国",
        "name_en": "United States",
        "code": "US",
        "continent": "北美洲",
        "capital": "华盛顿",
        "language": "英语",
        "currency": "美元",
        "safety_index": 69.0,
        "ppp_index": 88.0,
        "happiness_index": 71.0,
        "estimated_cost_level": "高",
    },
    {
        "name_zh": "澳大利亚",
        "name_en": "Australia",
        "code": "AU",
        "continent": "大洋洲",
        "capital": "堪培拉",
        "language": "英语",
        "currency": "澳元",
        "safety_index": 86.0,
        "ppp_index": 82.0,
        "happiness_index": 78.0,
        "estimated_cost_level": "中高",
    },
    {
        "name_zh": "新西兰",
        "name_en": "New Zealand",
        "code": "NZ",
        "continent": "大洋洲",
        "capital": "惠灵顿",
        "language": "英语",
        "currency": "新西兰元",
        "safety_index": 89.0,
        "ppp_index": 79.0,
        "happiness_index": 80.0,
        "estimated_cost_level": "中高",
    },
    {
        "name_zh": "土耳其",
        "name_en": "Turkey",
        "code": "TR",
        "continent": "亚洲",
        "capital": "安卡拉",
        "language": "土耳其语",
        "currency": "里拉",
        "safety_index": 65.0,
        "ppp_index": 40.0,
        "happiness_index": 58.0,
        "estimated_cost_level": "较低",
    },
    {
        "name_zh": "越南",
        "name_en": "Vietnam",
        "code": "VN",
        "continent": "亚洲",
        "capital": "河内",
        "language": "越南语",
        "currency": "越南盾",
        "safety_index": 74.0,
        "ppp_index": 35.0,
        "happiness_index": 66.0,
        "estimated_cost_level": "低",
    },
    {
        "name_zh": "印度尼西亚",
        "name_en": "Indonesia",
        "code": "ID",
        "continent": "亚洲",
        "capital": "雅加达",
        "language": "印尼语",
        "currency": "印尼盾",
        "safety_index": 70.0,
        "ppp_index": 42.0,
        "happiness_index": 64.0,
        "estimated_cost_level": "较低",
    },
    {
        "name_zh": "葡萄牙",
        "name_en": "Portugal",
        "code": "PT",
        "continent": "欧洲",
        "capital": "里斯本",
        "language": "葡萄牙语",
        "currency": "欧元",
        "safety_index": 88.0,
        "ppp_index": 62.0,
        "happiness_index": 76.0,
        "estimated_cost_level": "中等",
    },
]


def calculate_climate_index(continent):
    """根据洲别生成演示用气候指数。"""
    climate_map = {
        "亚洲": Decimal("78.00"),
        "欧洲": Decimal("74.00"),
        "北美洲": Decimal("72.00"),
        "大洋洲": Decimal("81.00"),
    }
    return climate_map.get(continent, Decimal("70.00"))


def calculate_medical_index(safety_index, happiness_index):
    """根据安全指数和幸福指数估算演示用医疗指数。"""
    return round((Decimal(str(safety_index)) * Decimal("0.6") + Decimal(str(happiness_index)) * Decimal("0.4")), 2)


def calculate_visa_index(ppp_index):
    """根据 PPP 指数估算演示用签证便利指数。"""
    base_score = Decimal("90.00") - Decimal(str(ppp_index)) * Decimal("0.2")
    if base_score < Decimal("55.00"):
        return Decimal("55.00")
    return round(base_score, 2)


def seed_demo_data():
    """写入毕业设计演示数据。"""
    current_year = 2026

    for item in DEMO_COUNTRY_DATA:
        # 创建或更新国家基础信息
        country, _ = Country.objects.update_or_create(
            code=item["code"],
            defaults={
                "name_zh": item["name_zh"],
                "name_en": item["name_en"],
                "continent": item["continent"],
                "capital": item["capital"],
                "language": item["language"],
                "currency": item["currency"],
                "is_active": True,
            },
        )

        # 根据演示数据推导补充其他指标
        climate_index = calculate_climate_index(item["continent"])
        medical_index = calculate_medical_index(
            item["safety_index"],
            item["happiness_index"],
        )
        visa_index = calculate_visa_index(item["ppp_index"])

        # 创建或更新国家指标数据
        CountryIndicator.objects.update_or_create(
            country=country,
            year=current_year,
            defaults={
                # 安全指数直接使用演示数据
                "safety_index": Decimal(str(item["safety_index"])),
                # 当前模型中使用 cost_index 暂存 PPP 指数
                "cost_index": Decimal(str(item["ppp_index"])),
                # 气候指数采用简化生成方式
                "climate_index": climate_index,
                # 医疗指数采用估算方式
                "medical_index": Decimal(str(medical_index)),
                # 签证便利指数采用估算方式
                "visa_index": visa_index,
                # 当前模型中使用 overall_score 暂存幸福指数
                "overall_score": Decimal(str(item["happiness_index"])),
                # 数据来源字段中保留演示说明与预计消费水平
                "data_source": (
                    f"毕业设计演示数据；预计消费水平={item['estimated_cost_level']}；"
                    f"PPP指数={item['ppp_index']}；幸福指数={item['happiness_index']}"
                ),
            },
        )

        print(f"已写入国家数据：{item['name_zh']}")

    print("毕业设计演示数据初始化完成。")


if __name__ == "__main__":
    seed_demo_data()
