"""系统模块序列化器。"""

from rest_framework import serializers

from apps.system.models import OperationLog


class OperationLogSerializer(serializers.ModelSerializer):
    """操作日志列表序列化器。"""

    operation_type_display = serializers.CharField(
        source="get_operation_type_display",
        read_only=True,
    )
    operation_result_display = serializers.CharField(
        source="get_operation_result_display",
        read_only=True,
    )

    class Meta:
        model = OperationLog
        fields = [
            "id",
            "user",
            "username",
            "operation_type",
            "operation_type_display",
            "operation_object",
            "created_at",
            "ip_address",
            "operation_result",
            "operation_result_display",
            "detail",
        ]
        read_only_fields = fields
