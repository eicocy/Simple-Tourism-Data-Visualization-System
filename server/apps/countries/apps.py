"""国家模块应用配置。"""

from django.apps import AppConfig


class CountriesConfig(AppConfig):
    """国家模块配置类。"""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.countries"
    verbose_name = "国家数据"
