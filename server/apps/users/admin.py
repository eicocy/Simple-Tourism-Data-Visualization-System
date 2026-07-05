"""用户模块后台管理配置。"""

from django.contrib import admin

from apps.users.models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """用户扩展资料后台管理。"""

    list_display = ["id", "user", "nickname", "gender", "age", "phone", "updated_at"]
    search_fields = ["user__username", "nickname", "phone"]
    list_filter = ["gender", "created_at", "updated_at"]
