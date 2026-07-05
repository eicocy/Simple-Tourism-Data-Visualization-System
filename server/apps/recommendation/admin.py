"""推荐模块后台管理配置。"""

from django.contrib import admin

from apps.recommendation.models import RecommendationRecord, UserPreference


@admin.register(UserPreference)
class UserPreferenceAdmin(admin.ModelAdmin):
    """用户偏好记录后台管理。"""

    list_display = [
        "id",
        "user",
        "preferred_continent",
        "budget_level",
        "created_at",
    ]
    search_fields = ["user__username", "preferred_continent", "remark"]
    list_filter = ["budget_level", "preferred_continent", "created_at"]
    ordering = ["-created_at"]


@admin.register(RecommendationRecord)
class RecommendationRecordAdmin(admin.ModelAdmin):
    """推荐结果记录后台管理。"""

    list_display = [
        "id",
        "user",
        "country",
        "score",
        "rank",
        "is_viewed",
        "created_at",
    ]
    search_fields = ["user__username", "country__name_zh", "country__name_en", "reason"]
    list_filter = ["is_viewed", "created_at", "country__continent"]
    ordering = ["-created_at", "rank"]
