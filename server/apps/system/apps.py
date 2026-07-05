"""系统模块应用配置。"""

from django.apps import AppConfig


class SystemConfig(AppConfig):
    """系统模块配置类。"""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.system"
    verbose_name = "系统管理"
