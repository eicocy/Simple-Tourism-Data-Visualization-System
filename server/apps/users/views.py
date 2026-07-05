"""用户模块视图。"""

from django.contrib.auth import get_user_model, login, logout, update_session_auth_hash
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token

from apps.countries.models import Country
from apps.recommendation.models import RecommendationRecord
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


# 获取 Django 默认用户模型
User = get_user_model()


def ensure_user_profile(user):
    """确保用户存在扩展资料。"""
    profile, _ = UserProfile.objects.get_or_create(user=user)
    return profile


def build_auth_payload(user):
    """构建登录成功后返回给前端的用户信息与 Token。"""
    token, _ = Token.objects.get_or_create(user=user)
    return {
        "token": token.key,
        "user": UserSerializer(user).data,
    }


@method_decorator(ensure_csrf_cookie, name="dispatch")
class CSRFTokenAPIView(APIView):
    """获取 CSRF Cookie 的接口。"""

    permission_classes = [AllowAny]

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

    def post(self, request):
        """处理用户登录请求。"""
        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        ensure_user_profile(user)
        login(request, user)

        return Response(
            {
                "code": 200,
                "message": "登录成功",
                "data": build_auth_payload(user),
            },
            status=status.HTTP_200_OK,
        )


class LogoutAPIView(APIView):
    """用户退出登录接口。"""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """清理当前用户 Session。"""
        # Token 登录时同步删除 Token，前端重新登录后会生成新 Token
        Token.objects.filter(user=request.user).delete()
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

    permission_classes = [IsAuthenticated]

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

    permission_classes = [IsAuthenticated]

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

    def patch(self, request):
        """局部更新当前用户资料。"""
        return self._update(request, partial=True)

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

    permission_classes = [IsAuthenticated]

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

    permission_classes = [IsAdminUser]

    def get(self, request):
        """返回管理员首页所需统计数据。"""
        data = {
            "total_users": User.objects.count(),
            "active_users": User.objects.filter(is_active=True).count(),
            "admin_users": User.objects.filter(is_staff=True).count(),
            "total_countries": Country.objects.filter(is_active=True).count(),
            "total_recommendations": RecommendationRecord.objects.count(),
        }
        return Response(
            {
                "code": 200,
                "message": "获取管理员概览成功",
                "data": data,
            },
            status=status.HTTP_200_OK,
        )


class AdminUserListAPIView(APIView):
    """管理员用户列表接口。"""

    permission_classes = [IsAdminUser]

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

    permission_classes = [IsAdminUser]

    def get_object(self, pk):
        """获取指定用户对象。"""
        return get_object_or_404(User, pk=pk)

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
