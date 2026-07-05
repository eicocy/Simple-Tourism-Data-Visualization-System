"""旅游适宜指数计算模块。"""

from decimal import Decimal, ROUND_HALF_UP


class TourismSuitabilityCalculator:
    """旅游适宜指数计算器。"""

    # 旅游适宜指数内部权重。
    # 旅游吸引力用于区分典型旅游目的地，签证便利度体现中国护照出行便利性。
    WEIGHTS = {
        "destination_attraction": Decimal("40.00"),
        "visa_convenience": Decimal("30.00"),
        "tourism_infrastructure": Decimal("20.00"),
        "travel_environment": Decimal("10.00"),
    }

    # 典型国际旅游目的地，基础旅游吸引力较高。
    CORE_DESTINATIONS = {
        "Australia",
        "Austria",
        "Belgium",
        "Brazil",
        "Canada",
        "China",
        "Croatia",
        "Czechia",
        "Denmark",
        "Egypt",
        "Finland",
        "France",
        "Germany",
        "Greece",
        "Iceland",
        "Indonesia",
        "Ireland",
        "Italy",
        "Japan",
        "Malaysia",
        "Maldives",
        "Mexico",
        "Morocco",
        "Netherlands",
        "New Zealand",
        "Norway",
        "Portugal",
        "Singapore",
        "South Africa",
        "South Korea",
        "Spain",
        "Sweden",
        "Switzerland",
        "Thailand",
        "Turkey",
        "United Arab Emirates",
        "United Kingdom",
        "United States",
    }

    # 区域型旅游目的地，具备一定旅游资源和接待能力。
    REGIONAL_DESTINATIONS = {
        "Albania",
        "Argentina",
        "Bulgaria",
        "Cambodia",
        "Chile",
        "Colombia",
        "Costa Rica",
        "Cuba",
        "Dominican Republic",
        "Estonia",
        "Fiji",
        "Hungary",
        "India",
        "Israel",
        "Jordan",
        "Kenya",
        "Laos",
        "Latvia",
        "Lithuania",
        "Mauritius",
        "Montenegro",
        "Nepal",
        "Oman",
        "Panama",
        "Peru",
        "Philippines",
        "Poland",
        "Qatar",
        "Romania",
        "Saudi Arabia",
        "Serbia",
        "Seychelles",
        "Slovakia",
        "Slovenia",
        "Sri Lanka",
        "Tanzania",
        "Tunisia",
        "Uruguay",
        "Vietnam",
    }

    # 当前不适合作为普通旅游推荐的目的地，基础旅游吸引力降权。
    LIMITED_DESTINATIONS = {
        "Afghanistan",
        "Central African Republic",
        "Eritrea",
        "Haiti",
        "Iraq",
        "Libya",
        "North Korea",
        "Somalia",
        "South Sudan",
        "Sudan",
        "Syria",
        "Yemen",
    }

    COUNTRY_ALIAS_MAP = {
        "USA": "United States",
        "United States of America": "United States",
        "UK": "United Kingdom",
        "UAE": "United Arab Emirates",
        "Republic of Korea": "South Korea",
        "Korea": "South Korea",
        "Viet Nam": "Vietnam",
        "Russian Federation": "Russia",
        "Czech Republic": "Czechia",
    }

    CONTINENT_BASE_SCORE = {
        "欧洲": Decimal("72.00"),
        "亚洲": Decimal("68.00"),
        "北美洲": Decimal("70.00"),
        "大洋洲": Decimal("70.00"),
        "南美洲": Decimal("62.00"),
        "非洲": Decimal("58.00"),
    }

    @classmethod
    def normalize_country_name(cls, country_name):
        """统一国家英文名，降低不同数据源命名差异。"""
        normalized_name = str(country_name or "").strip()
        return cls.COUNTRY_ALIAS_MAP.get(normalized_name, normalized_name)

    @staticmethod
    def clamp_score(value):
        """将分值限制在 0 到 100 之间。"""
        score = Decimal(str(value or 0))
        if score < 0:
            return Decimal("0.00")
        if score > 100:
            return Decimal("100.00")
        return score

    @staticmethod
    def round_score(value):
        """统一保留两位小数。"""
        return Decimal(value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @classmethod
    def get_destination_attraction_score(cls, country):
        """计算旅游目的地吸引力分。"""
        country_name = cls.normalize_country_name(country.get("country_name_en"))
        continent = country.get("continent", "")

        if country_name in cls.CORE_DESTINATIONS:
            return Decimal("90.00")
        if country_name in cls.REGIONAL_DESTINATIONS:
            return Decimal("76.00")
        if country_name in cls.LIMITED_DESTINATIONS:
            return Decimal("35.00")

        return cls.CONTINENT_BASE_SCORE.get(continent, Decimal("55.00"))

    @classmethod
    def get_visa_convenience_score(cls, country):
        """计算签证便利分。"""
        visa_score = country.get("visa_index")
        if visa_score is None:
            visa_score = country.get("raw_visa_score")
        if visa_score is None:
            visa_score = country.get("tourism_index")
        return cls.clamp_score(visa_score if visa_score is not None else 50)

    @classmethod
    def get_infrastructure_score(cls, country):
        """计算旅游基础设施代理分。"""
        # 当前项目中 cost_index 来自人均 GDP 标准化。这里正向使用它作为基础设施与服务成熟度代理指标。
        return cls.clamp_score(country.get("cost_index", 50))

    @classmethod
    def get_environment_score(cls, country):
        """计算旅游环境分。"""
        return cls.clamp_score(country.get("happiness_index", 50))

    @classmethod
    def build_detail(cls, country):
        """返回旅游适宜指数及其明细。"""
        attraction_score = cls.get_destination_attraction_score(country)
        visa_score = cls.get_visa_convenience_score(country)
        infrastructure_score = cls.get_infrastructure_score(country)
        environment_score = cls.get_environment_score(country)

        tourism_index = (
            attraction_score * cls.WEIGHTS["destination_attraction"]
            + visa_score * cls.WEIGHTS["visa_convenience"]
            + infrastructure_score * cls.WEIGHTS["tourism_infrastructure"]
            + environment_score * cls.WEIGHTS["travel_environment"]
        ) / Decimal("100.00")

        tourism_index = cls.round_score(tourism_index)

        return {
            "tourism_index": float(tourism_index),
            "destination_attraction_score": float(cls.round_score(attraction_score)),
            "visa_convenience_score": float(cls.round_score(visa_score)),
            "tourism_infrastructure_score": float(cls.round_score(infrastructure_score)),
            "travel_environment_score": float(cls.round_score(environment_score)),
            "tourism_level": cls.get_tourism_level(tourism_index),
        }

    @staticmethod
    def get_tourism_level(tourism_index):
        """根据旅游适宜指数返回等级文本。"""
        score = Decimal(str(tourism_index))
        if score >= Decimal("80.00"):
            return "高"
        if score >= Decimal("65.00"):
            return "较高"
        if score >= Decimal("50.00"):
            return "中等"
        return "较低"
