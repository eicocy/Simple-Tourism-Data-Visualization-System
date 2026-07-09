"""用户模块视图。"""

from datetime import datetime, time, timedelta

from django.contrib.auth import get_user_model, login, logout, update_session_auth_hash
from django.db.models import Count, Q
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
    extend_schema,
    inline_serializer,
)
from rest_framework import status
from rest_framework import serializers as drf_serializers
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from apps.countries.models import Country, CountryIndicator
from apps.recommendation.models import RecommendationRecord, UserPreference
from apps.system.models import OperationLog, record_operation_log
from apps.users.models import UserProfile
from apps.users.serializers import (
    AdminUserListSerializer,
    AdminUserUpdateSerializer,
    ChangePasswordSerializer,
    LoginSerializer,
    RegisterSerializer,
    UserProfileUpdateSerializer,
    UserSerializer,
    UserUpdateSerializer,
)
from common.permissions import IsAdminRole, IsAuthenticatedRole, is_admin_role


# 获取 Django 默认用户模型
User = get_user_model()


def ensure_user_profile(user):
    """确保用户存在扩展资料。"""
    profile, _ = UserProfile.objects.get_or_create(user=user)
    return profile


def build_auth_payload(user):
    """构建登录成功后返回给前端的用户信息与 JWT。"""
    refresh = RefreshToken.for_user(user)
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
        # 兼容旧前端字段，后续统一使用 access。
        "token": str(refresh.access_token),
        "user": UserSerializer(user).data,
    }


def get_popular_continent():
    """返回推荐记录中出现次数最多的洲别，暂无推荐时回退到国家数量最多的洲别。"""
    recommended_continent = (
        RecommendationRecord.objects.values("country__continent")
        .annotate(total=Count("id"))
        .order_by("-total")
        .first()
    )
    if recommended_continent and recommended_continent["country__continent"]:
        return {
            "name": recommended_continent["country__continent"],
            "count": recommended_continent["total"],
            "source": "recommendation",
        }

    country_continent = (
        Country.objects.filter(is_active=True)
        .values("continent")
        .annotate(total=Count("id"))
        .order_by("-total")
        .first()
    )
    if country_continent and country_continent["continent"]:
        return {
            "name": country_continent["continent"],
            "count": country_continent["total"],
            "source": "country",
        }

    return {"name": "--", "count": 0, "source": "empty"}


def build_safety_ranking(limit=10):
    """返回最新年份安全指数排名。"""
    latest_year = CountryIndicator.objects.order_by("-year").values_list(
        "year", flat=True
    ).first()
    if latest_year is None:
        return {"year": None, "results": []}

    indicators = (
        CountryIndicator.objects.select_related("country")
        .filter(year=latest_year, country__is_active=True)
        .order_by("-safety_index", "country__name_zh")[:limit]
    )
    return {
        "year": latest_year,
        "results": [
            {
                "country_id": indicator.country_id,
                "country_name": indicator.country.name_zh,
                "continent": indicator.country.continent,
                "safety_index": round(float(indicator.safety_index), 2),
            }
            for indicator in indicators
        ],
    }


def build_continent_country_counts():
    """返回各洲国家数量统计。"""
    rows = (
        Country.objects.filter(is_active=True)
        .values("continent")
        .annotate(count=Count("id"))
        .order_by("-count", "continent")
    )
    return [
        {
            "continent": row["continent"] or "未分类",
            "count": row["count"],
        }
        for row in rows
    ]


def build_recommendation_trend(days=14):
    """返回最近若干天的推荐记录趋势。"""
    today = timezone.localdate()
    start_date = today - timedelta(days=days - 1)
    trend_map = {
        (start_date + timedelta(days=index)).isoformat(): 0
        for index in range(days)
    }

    current_timezone = timezone.get_current_timezone()
    start_datetime = timezone.make_aware(
        datetime.combine(start_date, time.min),
        current_timezone,
    )
    end_datetime = timezone.make_aware(
        datetime.combine(today + timedelta(days=1), time.min),
        current_timezone,
    )

    created_values = UserPreference.objects.filter(
        created_at__gte=start_datetime,
        created_at__lt=end_datetime,
    ).values_list("created_at", flat=True)

    for created_at in created_values:
        local_date = timezone.localtime(created_at).date().isoformat()
        if local_date in trend_map:
            trend_map[local_date] += 1

    return [
        {
            "date": date,
            "count": count,
        }
        for date, count in trend_map.items()
    ]


@method_decorator(ensure_csrf_cookie, name="dispatch")
class CSRFTokenAPIView(APIView):
    """获取 CSRF Cookie 的接口。"""

    permission_classes = [AllowAny]

    @extend_schema(
        tags=["认证与用户"],
        summary="获取 CSRF Cookie",
        description="为浏览器端写操作下发 csrftoken Cookie。",
        auth=[],
        responses={200: OpenApiTypes.OBJECT},
    )
    def get(self, request):
        """向前端下发 CSRF Cookie。"""
        return Response(
            {
                "code": 200,
                "message": "CSRF Cookie 获取成功",
                "data": None,
            },
            status=status.HTTP_200_OK,
        )


class RegisterAPIView(APIView):
    """用户注册接口。"""

    permission_classes = [AllowAny]

    @extend_schema(
        tags=["认证与用户"],
        summary="用户注册",
        request=RegisterSerializer,
        responses={201: OpenApiTypes.OBJECT, 400: OpenApiResponse(description="注册参数校验失败")},
        auth=[],
    )
    def post(self, request):
        """处理用户注册请求。"""
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        ensure_user_profile(user)

        return Response(
            {
                "code": 201,
                "message": "用户注册成功",
                "data": build_auth_payload(user),
            },
            status=status.HTTP_201_CREATED,
        )


class LoginAPIView(APIView):
    """用户登录接口。"""

    permission_classes = [AllowAny]

    @extend_schema(
        tags=["认证与用户"],
        summary="用户登录并获取 JWT",
        description=(
            "使用用户名和密码登录。登录成功后返回 access、refresh、用户资料和角色信息；"
            "管理员登录会同步写入后台操作日志。"
        ),
        request=LoginSerializer,
        responses={
            200: inline_serializer(
                name="LoginSuccessResponse",
                fields={
                    "code": drf_serializers.IntegerField(default=200),
                    "message": drf_serializers.CharField(default="登录成功"),
                    "data": inline_serializer(
                        name="LoginPayload",
                        fields={
                            "access": drf_serializers.CharField(),
                            "refresh": drf_serializers.CharField(),
                            "token": drf_serializers.CharField(),
                            "user": UserSerializer(),
                        },
                    ),
                },
            ),
            400: OpenApiResponse(description="用户名或密码错误"),
        },
        examples=[
            OpenApiExample(
                "管理员登录示例",
                value={"username": "admin", "password": "lll190"},
                request_only=True,
            )
        ],
    )
    def post(self, request):
        """处理用户登录请求。"""
        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        ensure_user_profile(user)
        login(request, user)
        if is_admin_role(user):
            record_operation_log(
                request,
                OperationLog.OPERATION_ADMIN_LOGIN,
                operation_object=user.username,
                detail="管理员登录系统",
            )

        return Response(
            {
                "code": 200,
                "message": "登录成功",
                "data": build_auth_payload(user),
            },
            status=status.HTTP_200_OK,
        )


class JWTRefreshAPIView(APIView):
    """刷新 JWT Access Token 接口。"""

    permission_classes = [AllowAny]

    @extend_schema(
        tags=["认证与用户"],
        summary="刷新 JWT Access Token",
        request=inline_serializer(
            name="JWTRefreshRequest",
            fields={"refresh": drf_serializers.CharField()},
        ),
        responses={200: OpenApiTypes.OBJECT, 401: OpenApiResponse(description="Refresh Token 无效")},
        auth=[],
    )
    def post(self, request):
        """使用 refresh token 换取新的 access token。"""
        serializer = TokenRefreshSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(
            {
                "code": 200,
                "message": "Token 刷新成功",
                "data": serializer.validated_data,
            },
            status=status.HTTP_200_OK,
        )


class LogoutAPIView(APIView):
    """用户退出登录接口。"""

    permission_classes = [IsAuthenticatedRole]

    @extend_schema(
        tags=["认证与用户"],
        summary="退出登录",
        description="清理当前用户 Session，JWT Token 由前端删除。",
        request=None,
        responses={200: OpenApiTypes.OBJECT},
    )
    def post(self, request):
        """清理当前用户 Session，JWT 由前端移除。"""
        logout(request)
        return Response(
            {
                "code": 200,
                "message": "退出登录成功",
                "data": None,
            },
            status=status.HTTP_200_OK,
        )


@method_decorator(ensure_csrf_cookie, name="dispatch")
class CurrentUserAPIView(APIView):
    """获取当前登录用户信息接口。"""

    permission_classes = [IsAuthenticatedRole]

    @extend_schema(
        tags=["认证与用户"],
        summary="获取当前登录用户",
        responses={200: OpenApiTypes.OBJECT},
    )
    def get(self, request):
        """返回当前登录用户资料。"""
        ensure_user_profile(request.user)
        return Response(
            {
                "code": 200,
                "message": "获取当前用户成功",
                "data": UserSerializer(request.user).data,
            },
            status=status.HTTP_200_OK,
        )


class UserProfileAPIView(APIView):
    """当前用户资料查看与更新接口。"""

    permission_classes = [IsAuthenticatedRole]

    @extend_schema(
        tags=["认证与用户"],
        summary="获取当前用户资料",
        responses={200: OpenApiTypes.OBJECT},
    )
    def get(self, request):
        """返回当前用户资料。"""
        ensure_user_profile(request.user)
        return Response(
            {
                "code": 200,
                "message": "获取个人资料成功",
                "data": UserSerializer(request.user).data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        tags=["认证与用户"],
        summary="局部更新当前用户资料",
        request=inline_serializer(
            name="UserProfilePartialUpdateRequest",
            fields={
                "email": drf_serializers.EmailField(required=False),
                "first_name": drf_serializers.CharField(required=False),
                "last_name": drf_serializers.CharField(required=False),
                "nickname": drf_serializers.CharField(required=False),
                "gender": drf_serializers.CharField(required=False),
                "age": drf_serializers.IntegerField(required=False),
                "phone": drf_serializers.CharField(required=False),
                "bio": drf_serializers.CharField(required=False),
            },
        ),
        responses={200: OpenApiTypes.OBJECT},
    )
    def patch(self, request):
        """局部更新当前用户资料。"""
        return self._update(request, partial=True)

    @extend_schema(
        tags=["认证与用户"],
        summary="全量更新当前用户资料",
        request=inline_serializer(
            name="UserProfileUpdateRequest",
            fields={
                "email": drf_serializers.EmailField(required=False),
                "first_name": drf_serializers.CharField(required=False),
                "last_name": drf_serializers.CharField(required=False),
                "nickname": drf_serializers.CharField(required=False),
                "gender": drf_serializers.CharField(required=False),
                "age": drf_serializers.IntegerField(required=False),
                "phone": drf_serializers.CharField(required=False),
                "bio": drf_serializers.CharField(required=False),
            },
        ),
        responses={200: OpenApiTypes.OBJECT},
    )
    def put(self, request):
        """整体更新当前用户资料。"""
        return self._update(request, partial=False)

    def _update(self, request, partial):
        """统一处理当前用户资料更新。"""
        profile = ensure_user_profile(request.user)
        user_serializer = UserUpdateSerializer(request.user, data=request.data, partial=partial)
        profile_serializer = UserProfileUpdateSerializer(profile, data=request.data, partial=partial)

        user_serializer.is_valid(raise_exception=True)
        profile_serializer.is_valid(raise_exception=True)
        user_serializer.save()
        profile_serializer.save()

        return Response(
            {
                "code": 200,
                "message": "个人资料更新成功",
                "data": UserSerializer(request.user).data,
            },
            status=status.HTTP_200_OK,
        )


class ChangePasswordAPIView(APIView):
    """当前用户修改密码接口。"""

    permission_classes = [IsAuthenticatedRole]

    @extend_schema(
        tags=["认证与用户"],
        summary="修改当前用户密码",
        request=ChangePasswordSerializer,
        responses={200: OpenApiTypes.OBJECT, 400: OpenApiResponse(description="密码校验失败")},
    )
    def post(self, request):
        """处理密码修改请求。"""
        serializer = ChangePasswordSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        request.user.set_password(serializer.validated_data["new_password"])
        request.user.save()
        update_session_auth_hash(request, request.user)

        return Response(
            {
                "code": 200,
                "message": "密码修改成功",
                "data": None,
            },
            status=status.HTTP_200_OK,
        )


class AdminDashboardSummaryAPIView(APIView):
    """管理员数据概览接口。"""

    permission_classes = [IsAdminRole]

    @extend_schema(
        tags=["后台统计"],
        summary="获取管理员首页统计概览",
        description="返回国家总数、用户总数、管理员数量、推荐次数和热门洲别等后台首页卡片数据。",
        responses={200: OpenApiTypes.OBJECT},
    )
    def get(self, request):
        """返回管理员首页所需统计数据。"""
        data = {
            "total_users": User.objects.count(),
            "active_users": User.objects.filter(is_active=True).count(),
            "admin_users": User.objects.filter(is_staff=True).count(),
            "total_countries": Country.objects.filter(is_active=True).count(),
            "total_recommendations": UserPreference.objects.count(),
            "popular_continent": get_popular_continent()["name"],
        }
        return Response(
            {
                "code": 200,
                "message": "获取管理员概览成功",
                "data": data,
            },
            status=status.HTTP_200_OK,
        )


class AdminDashboardReportAPIView(APIView):
    """管理员后台统计报表接口。"""

    permission_classes = [IsAdminRole]

    @extend_schema(
        tags=["后台统计"],
        summary="获取后台统计报表",
        description=(
            "返回管理员首页的统计卡片和 ECharts 图表数据，包含安全指数排名、"
            "洲别国家数量饼图和最近 14 天推荐次数趋势。推荐次数按一次推荐请求统计。"
        ),
        responses={
            200: OpenApiResponse(description="后台统计报表数据"),
            401: OpenApiResponse(description="未登录或 JWT 失效"),
            403: OpenApiResponse(description="当前用户不是管理员"),
        },
    )
    def get(self, request):
        """返回后台首页统计卡片与图表数据。"""
        popular_continent = get_popular_continent()
        data = {
            "cards": {
                "total_countries": Country.objects.filter(is_active=True).count(),
                "total_users": User.objects.count(),
                "total_recommendations": UserPreference.objects.count(),
                "popular_continent": popular_continent["name"],
                "popular_continent_count": popular_continent["count"],
                "popular_continent_source": popular_continent["source"],
            },
            "charts": {
                "safety_ranking": build_safety_ranking(),
                "continent_country_counts": build_continent_country_counts(),
                "recommendation_trend": build_recommendation_trend(days=14),
            },
        }
        return Response(
            {
                "code": 200,
                "message": "获取后台统计报表成功",
                "data": data,
            },
            status=status.HTTP_200_OK,
        )


class AdminUserListAPIView(APIView):
    """管理员用户列表接口。"""

    permission_classes = [IsAdminRole]

    @extend_schema(
        tags=["后台统计"],
        operation_id="admin_user_list",
        summary="查询后台用户列表",
        parameters=[
            OpenApiParameter(
                name="search",
                description="按用户名或邮箱模糊搜索",
                required=False,
                type=str,
            )
        ],
        responses={200: OpenApiTypes.OBJECT},
    )
    def get(self, request):
        """返回用户列表，支持按用户名和邮箱搜索。"""
        search = request.query_params.get("search", "").strip()
        queryset = User.objects.all().order_by("-date_joined")

        if search:
            queryset = queryset.filter(Q(username__icontains=search) | Q(email__icontains=search))

        serializer = AdminUserListSerializer(queryset, many=True)
        return Response(
            {
                "code": 200,
                "message": "获取用户列表成功",
                "data": {
                    "count": queryset.count(),
                    "results": serializer.data,
                },
            },
            status=status.HTTP_200_OK,
        )


class AdminUserDetailAPIView(APIView):
    """管理员用户详情与更新接口。"""

    permission_classes = [IsAdminRole]

    def get_object(self, pk):
        """获取指定用户对象。"""
        return get_object_or_404(User, pk=pk)

    @extend_schema(
        tags=["后台统计"],
        operation_id="admin_user_retrieve",
        summary="查询单个后台用户",
        responses={200: OpenApiTypes.OBJECT, 404: OpenApiResponse(description="用户不存在")},
    )
    def get(self, request, pk):
        """返回指定用户详情。"""
        user = self.get_object(pk)
        ensure_user_profile(user)
        return Response(
            {
                "code": 200,
                "message": "获取用户详情成功",
                "data": AdminUserListSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        tags=["后台统计"],
        operation_id="admin_user_partial_update",
        summary="管理员更新用户状态或角色",
        request=AdminUserUpdateSerializer,
        responses={200: OpenApiTypes.OBJECT, 400: OpenApiResponse(description="参数校验失败")},
    )
    def patch(self, request, pk):
        """管理员更新用户启用状态、管理员身份与邮箱。"""
        user = self.get_object(pk)
        serializer = AdminUserUpdateSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        ensure_user_profile(user)
        return Response(
            {
                "code": 200,
                "message": "用户信息更新成功",
                "data": AdminUserListSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )
