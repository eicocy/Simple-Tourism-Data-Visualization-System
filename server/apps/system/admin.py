"""系统模块后台管理。"""

from django.contrib import admin

from apps.system.models import OperationLog


@admin.register(OperationLog)
class OperationLogAdmin(admin.ModelAdmin):
    """操作日志后台配置。"""

    list_display = [
        "username",
        "operation_type",
        "operation_object",
        "operation_result",
        "ip_address",
        "created_at",
    ]
    list_filter = ["operation_type", "operation_result", "created_at"]
    search_fields = ["username", "operation_object", "detail"]
    readonly_fields = [
        "user",
        "username",
        "operation_type",
        "operation_object",
        "operation_result",
        "ip_address",
        "detail",
        "created_at",
    ]
