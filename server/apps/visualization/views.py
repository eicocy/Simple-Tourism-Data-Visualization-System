"""可视化模块视图。"""

from drf_spectacular.utils import OpenApiExample, OpenApiResponse, OpenApiTypes, extend_schema
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.visualization.agent import generate_agent_response
from common.permissions import IsAuthenticatedRole


class MapAgentChatRequestSerializer(serializers.Serializer):
    """智能地图助手请求参数。"""

    message = serializers.CharField(
        max_length=500,
        trim_whitespace=True,
        help_text="用户自然语言问题，例如：现在哪里有战事？我想去看欧洲的山。",
    )


class MapAgentChatAPIView(APIView):
    """智能地图问答助手接口。"""

    permission_classes = [IsAuthenticatedRole]

    @extend_schema(
        tags=["可视化分析"],
        summary="智能地图问答助手",
        description=(
            "根据用户自然语言问题识别风险查询或旅游偏好，返回地图国家级标注与对话回答。"
            "当前版本采用本地规则和系统国家指标稳定演示；配置大模型 Key 后可用于回答润色。"
        ),
        request=MapAgentChatRequestSerializer,
        responses={
            200: OpenApiResponse(description="智能地图问答成功", response=OpenApiTypes.OBJECT),
            400: OpenApiResponse(description="请求参数不合法"),
        },
        examples=[
            OpenApiExample(
                "战事风险查询",
                value={"message": "现在哪里有战事？"},
                request_only=True,
            ),
            OpenApiExample(
                "风景推荐查询",
                value={"message": "我想去看欧洲的山"},
                request_only=True,
            ),
        ],
    )
    def post(self, request):
        """接收用户问题并返回地图标注结果。"""
        serializer = MapAgentChatRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = generate_agent_response(serializer.validated_data["message"])
        return Response(
            {
                "code": 200,
                "message": "智能地图问答成功",
                "data": result,
            },
            status=status.HTTP_200_OK,
        )
