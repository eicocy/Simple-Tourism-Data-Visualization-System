"""推荐模块数据模型。"""

from django.contrib.auth import get_user_model
from django.db import models

from apps.countries.models import Country


# 获取 Django 默认用户模型
User = get_user_model()


class UserPreference(models.Model):
    """用户偏好记录表。"""

    TRAVEL_BUDGET_CHOICES = (
        ("low", "低预算"),
        ("medium", "中等预算"),
        ("high", "高预算"),
    )

    # 关联用户，表示该偏好属于哪个用户
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="preferences",
        verbose_name="所属用户",
        help_text="该条偏好记录所属的用户",
    )
    # 偏好的洲别，用于缩小推荐范围
    preferred_continent = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="偏好洲别",
        help_text="用户更希望前往的大洲，可为空",
    )
    # 可接受预算等级，便于与消费指数匹配
    budget_level = models.CharField(
        max_length=20,
        choices=TRAVEL_BUDGET_CHOICES,
        default="medium",
        verbose_name="预算等级",
        help_text="用户可接受的旅游预算等级",
    )
    # 用户对安全性的重视程度
    safety_weight = models.PositiveIntegerField(
        default=40,
        verbose_name="安全权重",
        help_text="用户对安全因素的重视程度，建议 0 到 100",
    )
    # 用户对消费成本的重视程度
    cost_weight = models.PositiveIntegerField(
        default=20,
        verbose_name="消费权重",
        help_text="用户对消费成本的重视程度，建议 0 到 100",
    )
    # 用户对气候舒适度的重视程度
    climate_weight = models.PositiveIntegerField(
        default=20,
        verbose_name="气候权重",
        help_text="用户对气候舒适度的重视程度，建议 0 到 100",
    )
    # 用户对医疗保障的重视程度
    medical_weight = models.PositiveIntegerField(
        default=10,
        verbose_name="医疗权重",
        help_text="用户对医疗保障的重视程度，建议 0 到 100",
    )
    # 用户对签证便利性的重视程度
    visa_weight = models.PositiveIntegerField(
        default=10,
        verbose_name="签证权重",
        help_text="用户对签证便利性的重视程度，建议 0 到 100",
    )
    # 备注信息，便于记录个性化需求
    remark = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="偏好备注",
        help_text="用户补充说明，例如偏好海岛、避开寒冷地区",
    )
    # 创建时间
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="创建时间",
        help_text="当前记录的创建时间",
    )

    class Meta:
        db_table = "user_preference"
        verbose_name = "用户偏好记录"
        verbose_name_plural = "用户偏好记录"
        ordering = ["-created_at"]

    def __str__(self):
        """返回用户偏好记录的简要说明。"""
        return f"{self.user.username}-偏好记录-{self.id}"


class RecommendationRecord(models.Model):
    """推荐结果记录表。"""

    # 关联用户，表示是哪位用户触发的推荐
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recommendation_records",
        verbose_name="所属用户",
        help_text="该条推荐记录所属的用户",
    )
    # 关联用户偏好，便于回溯推荐时使用的条件
    preference = models.ForeignKey(
        UserPreference,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="recommendation_records",
        verbose_name="关联偏好",
        help_text="生成该推荐结果时参考的用户偏好记录",
    )
    # 被推荐的国家
    country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        related_name="recommendation_records",
        verbose_name="推荐国家",
        help_text="系统最终推荐的国家",
    )
    # 推荐得分，便于排序和可视化展示
    score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="推荐得分",
        help_text="系统根据偏好和国家指标计算出的推荐得分",
    )
    # 推荐原因简述，便于前端直接展示
    reason = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="推荐原因",
        help_text="推荐该国家的简要原因说明",
    )
    # 排名信息，例如第 1 名、第 2 名
    rank = models.PositiveIntegerField(
        default=1,
        verbose_name="推荐排名",
        help_text="该国家在当前推荐结果中的排名",
    )
    # 是否被用户查看，可用于后续行为分析
    is_viewed = models.BooleanField(
        default=False,
        verbose_name="是否已查看",
        help_text="用户是否查看过该条推荐记录",
    )
    # 生成时间，记录推荐结果产生的时刻
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="创建时间",
        help_text="当前记录的创建时间",
    )

    class Meta:
        db_table = "recommendation_record"
        verbose_name = "推荐结果记录"
        verbose_name_plural = "推荐结果记录"
        ordering = ["rank", "-created_at"]

    def __str__(self):
        """返回推荐结果的简要说明。"""
        return f"{self.user.username}-{self.country.name_zh}-第{self.rank}名"
