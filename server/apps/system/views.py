"""系统模块视图。"""

from django.utils.dateparse import parse_date
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import filters
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from apps.system.models import OperationLog
from apps.system.serializers import OperationLogSerializer
from common.permissions import IsAdminRole


class OperationLogListAPIView(ListAPIView):
    """后台操作日志列表接口。"""

    serializer_class = OperationLogSerializer
    permission_classes = [IsAdminRole]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]

    @extend_schema(
        tags=["系统管理"],
        summary="查询后台操作日志",
        description="管理员查询登录、国家数据管理、Excel 导入导出等后台操作日志。",
        parameters=[
            OpenApiParameter("username", str, OpenApiParameter.QUERY, description="按用户名模糊筛选"),
            OpenApiParameter("operation_type", str, OpenApiParameter.QUERY, description="操作类型，如 admin_login、excel_import"),
            OpenApiParameter("start_date", str, OpenApiParameter.QUERY, description="开始日期，格式 YYYY-MM-DD"),
            OpenApiParameter("end_date", str, OpenApiParameter.QUERY, description="结束日期，格式 YYYY-MM-DD"),
        ],
        responses={200: OpenApiResponse(description="操作日志分页列表")},
    )
    def list(self, request, *args, **kwargs):
        """返回统一结构的分页日志数据。"""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return Response(
                {
                    "code": 200,
                    "message": "获取操作日志成功",
                    "data": {
                        "count": self.paginator.page.paginator.count,
                        "next": self.paginator.get_next_link(),
                        "previous": self.paginator.get_previous_link(),
                        "results": serializer.data,
                    },
                }
            )

        serializer = self.get_serializer(queryset, many=True)
        return Response(
            {
                "code": 200,
                "message": "获取操作日志成功",
                "data": {
                    "count": len(serializer.data),
                    "next": None,
                    "previous": None,
                    "results": serializer.data,
                },
            }
        )

    def get_queryset(self):
        """按用户名、操作类型和操作时间筛选日志。"""
        queryset = OperationLog.objects.select_related("user").all()

        username = self.request.query_params.get("username")
        if username:
            queryset = queryset.filter(username__icontains=username.strip())

        operation_type = self.request.query_params.get("operation_type")
        if operation_type:
            queryset = queryset.filter(operation_type=operation_type)

        start_date = parse_date(self.request.query_params.get("start_date") or "")
        if start_date:
            queryset = queryset.filter(created_at__date__gte=start_date)

        end_date = parse_date(self.request.query_params.get("end_date") or "")
        if end_date:
            queryset = queryset.filter(created_at__date__lte=end_date)

        return queryset
