"""可视化模块应用配置。"""

from django.apps import AppConfig


class VisualizationConfig(AppConfig):
    """可视化模块配置类。"""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.visualization"
    verbose_name = "数据可视化"
