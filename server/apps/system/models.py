"""系统模块数据模型。"""

from django.conf import settings
from django.db import models


class OperationLog(models.Model):
    """后台操作日志。"""

    OPERATION_ADMIN_LOGIN = "admin_login"
    OPERATION_COUNTRY_CREATE = "country_create"
    OPERATION_COUNTRY_UPDATE = "country_update"
    OPERATION_COUNTRY_DELETE = "country_delete"
    OPERATION_EXCEL_IMPORT = "excel_import"
    OPERATION_EXCEL_EXPORT = "excel_export"

    OPERATION_TYPE_CHOICES = [
        (OPERATION_ADMIN_LOGIN, "管理员登录"),
        (OPERATION_COUNTRY_CREATE, "添加国家数据"),
        (OPERATION_COUNTRY_UPDATE, "修改国家数据"),
        (OPERATION_COUNTRY_DELETE, "删除国家数据"),
        (OPERATION_EXCEL_IMPORT, "导入 Excel"),
        (OPERATION_EXCEL_EXPORT, "导出 Excel"),
    ]

    RESULT_SUCCESS = "success"
    RESULT_FAILED = "failed"

    OPERATION_RESULT_CHOICES = [
        (RESULT_SUCCESS, "成功"),
        (RESULT_FAILED, "失败"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="operation_logs",
        verbose_name="操作用户",
    )
    username = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="用户名快照",
        help_text="保存操作发生时的用户名，避免用户删除后日志失去可读性。",
    )
    operation_type = models.CharField(
        max_length=50,
        choices=OPERATION_TYPE_CHOICES,
        verbose_name="操作类型",
    )
    operation_object = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="操作对象",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="操作时间",
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="IP 地址",
    )
    operation_result = models.CharField(
        max_length=20,
        choices=OPERATION_RESULT_CHOICES,
        default=RESULT_SUCCESS,
        verbose_name="操作结果",
    )
    detail = models.TextField(
        blank=True,
        verbose_name="操作详情",
    )

    class Meta:
        db_table = "operation_log"
        verbose_name = "操作日志"
        verbose_name_plural = "操作日志"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["username", "operation_type"], name="oplog_user_type_idx"),
            models.Index(fields=["created_at"], name="oplog_created_idx"),
        ]

    def __str__(self):
        """返回日志简要描述。"""
        return f"{self.username or '未知用户'} - {self.get_operation_type_display()}"


def get_client_ip(request):
    """从请求头中提取客户端 IP。"""
    if not request:
        return None

    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def record_operation_log(
    request,
    operation_type,
    operation_object="",
    operation_result=OperationLog.RESULT_SUCCESS,
    detail="",
):
    """记录操作日志，日志写入失败不影响主业务流程。"""
    try:
        user = getattr(request, "user", None)
        is_authenticated = bool(user and user.is_authenticated)
        OperationLog.objects.create(
            user=user if is_authenticated else None,
            username=getattr(user, "username", "") if is_authenticated else "匿名用户",
            operation_type=operation_type,
            operation_object=str(operation_object or "")[:255],
            ip_address=get_client_ip(request),
            operation_result=operation_result,
            detail=detail or "",
        )
    except Exception:
        pass
