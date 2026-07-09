"""通用权限类。"""

from rest_framework.permissions import BasePermission, SAFE_METHODS


def get_user_role(user):
    """返回用户角色，兼容 Django staff/superuser 与扩展资料 role 字段。"""
    if not user or not user.is_authenticated:
        return "anonymous"
    if user.is_superuser or user.is_staff:
        return "admin"

    profile = getattr(user, "profile", None)
    if profile and getattr(profile, "role", "") == "admin":
        return "admin"
    return "user"


def is_admin_role(user):
    """判断用户是否为管理员。"""
    return get_user_role(user) == "admin"


def is_normal_role(user):
    """判断用户是否为普通用户。"""
    return get_user_role(user) == "user"


class IsAdminRole(BasePermission):
    """仅管理员可访问。"""

    message = "当前接口仅管理员可访问。"

    def has_permission(self, request, view):
        return is_admin_role(request.user)


class IsNormalUserRole(BasePermission):
    """仅普通用户可访问。"""

    message = "当前接口仅普通用户可访问。"

    def has_permission(self, request, view):
        return is_normal_role(request.user)


class IsAuthenticatedRole(BasePermission):
    """普通用户和管理员登录后均可访问。"""

    message = "请先登录后再访问。"

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)


class IsAdminRoleOrReadOnly(BasePermission):
    """读操作允许登录用户访问，写操作仅管理员访问。"""

    message = "当前操作仅管理员可执行。"

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return bool(request.user and request.user.is_authenticated)
        return is_admin_role(request.user)
