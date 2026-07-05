"""推荐模块应用配置。"""

from django.apps import AppConfig


class RecommendationConfig(AppConfig):
    """推荐模块配置类。"""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.recommendation"
    verbose_name = "推荐算法"
