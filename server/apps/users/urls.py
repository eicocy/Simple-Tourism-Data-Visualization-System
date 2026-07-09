"""用户模块路由配置。"""

from django.urls import path

from apps.users.views import (
    AdminDashboardReportAPIView,
    AdminDashboardSummaryAPIView,
    AdminUserDetailAPIView,
    AdminUserListAPIView,
    CSRFTokenAPIView,
    ChangePasswordAPIView,
    CurrentUserAPIView,
    JWTRefreshAPIView,
    LoginAPIView,
    LogoutAPIView,
    RegisterAPIView,
    UserProfileAPIView,
)


urlpatterns = [
    # 获取 CSRF Cookie 接口
    path("csrf/", CSRFTokenAPIView.as_view(), name="user-csrf"),
    # 用户注册接口
    path("register/", RegisterAPIView.as_view(), name="user-register"),
    # 用户登录接口
    path("login/", LoginAPIView.as_view(), name="user-login"),
    # JWT 刷新接口
    path("token/refresh/", JWTRefreshAPIView.as_view(), name="user-token-refresh"),
    # 用户退出接口
    path("logout/", LogoutAPIView.as_view(), name="user-logout"),
    # 获取当前登录用户信息接口
    path("me/", CurrentUserAPIView.as_view(), name="user-me"),
    # 当前用户资料查看与更新接口
    path("profile/", UserProfileAPIView.as_view(), name="user-profile"),
    # 当前用户修改密码接口
    path("change-password/", ChangePasswordAPIView.as_view(), name="user-change-password"),
    # 管理员概览接口
    path("admin/summary/", AdminDashboardSummaryAPIView.as_view(), name="admin-summary"),
    # 管理员统计报表接口
    path("admin/report/", AdminDashboardReportAPIView.as_view(), name="admin-report"),
    # 管理员用户列表接口
    path("admin/users/", AdminUserListAPIView.as_view(), name="admin-user-list"),
    # 管理员用户详情与更新接口
    path("admin/users/<int:pk>/", AdminUserDetailAPIView.as_view(), name="admin-user-detail"),
]
