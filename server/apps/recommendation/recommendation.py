"""旅游国家推荐算法模块。"""

from decimal import Decimal

from apps.recommendation.tourism_suitability import TourismSuitabilityCalculator


class TravelRecommendationEngine:
    """旅游国家推荐引擎。"""

    # 固定推荐权重，用于推荐接口和首页地图等场景
    # tourism_index 占 40%，安全指数占 30%，幸福指数占 15%，消费指数占 15%
    FIXED_WEIGHT_PROFILE = {
        "tourism_weight": Decimal("40.00"),
        "safety_weight": Decimal("30.00"),
        "happiness_weight": Decimal("15.00"),
        "cost_weight": Decimal("15.00"),
    }

    # 系统默认推荐配置，用于首页地图等无需用户输入的场景
    DEFAULT_WEIGHT_PROFILE = {
        "budget_level": "high",
        "preferred_continent": "",
        "safety_requirement": "normal",
    }

    # 不同预算等级可接受的消费指数上限
    BUDGET_LIMIT_MAP = {
        "low": Decimal("60.00"),
        "medium": Decimal("80.00"),
        "high": Decimal("100.00"),
    }

    # 不同安全需求对应的最低安全指数要求
    SAFETY_REQUIREMENT_MAP = {
        "normal": Decimal("0.00"),
        "high": Decimal("75.00"),
        "strict": Decimal("85.00"),
    }

    def __init__(self, countries, user_preference):
        """初始化推荐引擎。"""
        self.countries = countries
        self.user_preference = user_preference

    def filter_by_budget(self, countries):
        """根据预算等级标记国家是否匹配。"""
        budget_level = self.user_preference.get("budget_level", "medium")
        max_cost_index = self.BUDGET_LIMIT_MAP.get(budget_level, Decimal("80.00"))

        filtered_countries = []
        for country in countries:
            current_cost_index = Decimal(str(country.get("cost_index", 0)))
            country_copy = country.copy()
            country_copy["budget_matched"] = current_cost_index <= max_cost_index
            filtered_countries.append(country_copy)

        return filtered_countries

    def apply_safety_requirement(self, countries):
        """根据用户安全需求标记国家是否满足安全要求。"""
        safety_requirement = self.user_preference.get("safety_requirement", "high")
        min_safety_index = self.SAFETY_REQUIREMENT_MAP.get(
            safety_requirement,
            Decimal("75.00"),
        )

        prepared_countries = []
        for country in countries:
            current_safety_index = Decimal(str(country.get("safety_index", 0)))
            country_copy = country.copy()
            country_copy["safety_requirement"] = safety_requirement
            country_copy["safety_matched"] = current_safety_index >= min_safety_index
            prepared_countries.append(country_copy)

        return prepared_countries

    def filter_by_continent(self, countries):
        """根据偏好洲别筛选国家。"""
        preferred_continent = self.user_preference.get("preferred_continent")
        if not preferred_continent:
            return countries

        matched_countries = [
            country
            for country in countries
            if country.get("continent") == preferred_continent
        ]
        return matched_countries if matched_countries else countries

    @staticmethod
    def normalize_cost_score(cost_index):
        """将消费指数转换为正向分值。"""
        cost_score = Decimal("100.00") - Decimal(str(cost_index))
        if cost_score < 0:
            return Decimal("0.00")
        if cost_score > 100:
            return Decimal("100.00")
        return cost_score

    @staticmethod
    def estimate_cost_level(cost_index):
        """根据消费指数估算消费水平。"""
        numeric_value = Decimal(str(cost_index))
        if numeric_value <= Decimal("45.00"):
            return "较低"
        if numeric_value <= Decimal("65.00"):
            return "中等"
        if numeric_value <= Decimal("80.00"):
            return "中高"
        return "较高"

    @classmethod
    def calculate_default_recommendation_index(cls, country):
        """按固定权重计算首页地图等场景使用的推荐指数。"""
        country = country.copy()
        country["tourism_index"] = TourismSuitabilityCalculator.build_detail(country)[
            "tourism_index"
        ]
        engine = cls(
            countries=[country],
            user_preference=cls.DEFAULT_WEIGHT_PROFILE,
        )
        prepared_country = engine.filter_by_budget([country])[0]
        return engine.calculate_score(prepared_country)

    def calculate_score(self, country):
        """计算单个国家的综合推荐得分。"""
        tourism_index = Decimal(str(country.get("tourism_index", 0)))
        safety_index = Decimal(str(country.get("safety_index", 0)))
        happiness_index = Decimal(str(country.get("happiness_index", 0)))
        cost_index = Decimal(str(country.get("cost_index", 0)))

        tourism_weight = self.FIXED_WEIGHT_PROFILE["tourism_weight"]
        safety_weight = self.FIXED_WEIGHT_PROFILE["safety_weight"]
        happiness_weight = self.FIXED_WEIGHT_PROFILE["happiness_weight"]
        cost_weight = self.FIXED_WEIGHT_PROFILE["cost_weight"]

        # 消费指数越高表示旅游成本越高，因此转换成消费友好度得分
        cost_score = self.normalize_cost_score(cost_index)

        score = (
            tourism_weight * tourism_index
            + safety_weight * safety_index
            + happiness_weight * happiness_index
            + cost_weight * cost_score
        ) / Decimal("100.00")

        if not country.get("budget_matched", True):
            score *= Decimal("0.80")
        if not country.get("safety_matched", True):
            score *= Decimal("0.85")

        return round(float(score), 2)

    @staticmethod
    def get_safety_requirement_text(safety_requirement):
        """返回安全需求文本。"""
        return {
            "normal": "一般安全需求",
            "high": "较高安全需求",
            "strict": "高安全需求",
        }.get(safety_requirement, "较高安全需求")

    @staticmethod
    def build_reason(country):
        """生成推荐原因。"""
        reasons = []

        if Decimal(str(country.get("tourism_index", 0))) >= Decimal("75.00"):
            reasons.append("旅游适宜性较高")
        if Decimal(str(country.get("safety_index", 0))) >= Decimal("80.00"):
            reasons.append("公共安全水平较高")
        if Decimal(str(country.get("happiness_index", 0))) >= Decimal("75.00"):
            reasons.append("居民幸福指数较高")
        if Decimal(str(country.get("cost_index", 0))) <= Decimal("60.00"):
            reasons.append("旅游消费相对友好")
        if country.get("safety_requirement") != "normal":
            if country.get("safety_matched", True):
                reasons.append("符合当前安全需求")
            else:
                reasons.append("安全指数低于当前需求，已降低排序权重")

        if not reasons:
            reasons.append("综合指标表现较均衡")

        return "，".join(reasons)

    def recommend(self, top_n=10):
        """执行推荐计算并返回排序结果。"""
        continent_filtered = self.filter_by_continent(self.countries)
        budget_filtered = self.filter_by_budget(continent_filtered)
        safety_prepared = self.apply_safety_requirement(budget_filtered)

        recommendation_results = []
        for country in safety_prepared:
            tourism_detail = TourismSuitabilityCalculator.build_detail(country)
            country["tourism_index"] = tourism_detail["tourism_index"]
            score = self.calculate_score(country)
            recommendation_results.append(
                {
                    "country_id": country.get("country_id"),
                    "country_name": country.get("country_name"),
                    "country_name_en": country.get("country_name_en"),
                    "continent": country.get("continent"),
                    "score": score,
                    "tourism_index": round(float(country.get("tourism_index", 0)), 2),
                    "tourism_detail": tourism_detail,
                    "safety_index": round(float(country.get("safety_index", 0)), 2),
                    "ppp_index": round(float(country.get("cost_index", 0)), 2),
                    "cost_index": round(float(country.get("cost_index", 0)), 2),
                    "happiness_index": round(
                        float(country.get("happiness_index", 0)), 2
                    ),
                    "estimated_cost": self.estimate_cost_level(
                        country.get("cost_index", 0)
                    ),
                    "budget_matched": country.get("budget_matched", True),
                    "safety_requirement": self.get_safety_requirement_text(
                        country.get("safety_requirement")
                    ),
                    "safety_matched": country.get("safety_matched", True),
                    "reason": self.build_reason(country),
                }
            )

        recommendation_results.sort(key=lambda item: item["score"], reverse=True)

        for index, item in enumerate(recommendation_results, start=1):
            item["rank"] = index

        return recommendation_results[:top_n]
