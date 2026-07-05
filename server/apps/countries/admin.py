"""国家模块后台管理配置。"""

from django.contrib import admin

from apps.countries.models import Country, CountryIndicator


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    """国家基础信息后台管理。"""

    list_display = [
        "id",
        "name_zh",
        "name_en",
        "code",
        "continent",
        "is_active",
        "updated_at",
    ]
    search_fields = ["name_zh", "name_en", "code", "continent"]
    list_filter = ["continent", "is_active", "created_at", "updated_at"]
    ordering = ["name_zh"]


@admin.register(CountryIndicator)
class CountryIndicatorAdmin(admin.ModelAdmin):
    """国家年度指标后台管理。"""

    list_display = [
        "id",
        "country",
        "year",
        "safety_index",
        "cost_index",
        "tourism_index",
        "visa_index",
        "overall_score",
        "updated_at",
    ]
    search_fields = ["country__name_zh", "country__name_en", "country__code"]
    list_filter = ["year", "country__continent", "created_at", "updated_at"]
    ordering = ["-year", "country__name_zh"]
