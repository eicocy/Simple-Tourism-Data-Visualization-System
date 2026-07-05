"""用户模块数据模型。"""

from django.contrib.auth import get_user_model
from django.db import models


# 获取 Django 默认用户模型，便于后续扩展或替换
User = get_user_model()


class UserProfile(models.Model):
    """用户扩展信息表。"""

    GENDER_CHOICES = (
        ("male", "男"),
        ("female", "女"),
        ("unknown", "未知"),
    )

    # 关联 Django 内置用户表，形成一对一扩展关系
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name="关联用户",
        help_text="关联 Django 内置用户表中的用户记录",
    )
    # 用户昵称，用于页面展示
    nickname = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="用户昵称",
        help_text="用户在系统中的显示名称",
    )
    # 性别字段，便于做基础用户画像展示
    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        default="unknown",
        verbose_name="性别",
        help_text="用户性别信息，默认未知",
    )
    # 年龄字段，用于推荐分析时做简单分层
    age = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="年龄",
        help_text="用户年龄，可为空",
    )
    # 手机号字段，方便后续扩展个人信息管理
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="手机号",
        help_text="用户联系电话，可为空",
    )
    # 用户个人简介，用于展示
    bio = models.TextField(
        blank=True,
        verbose_name="个人简介",
        help_text="用户自我描述信息",
    )
    # 创建时间，记录数据新增时间
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="创建时间",
        help_text="当前记录的创建时间",
    )
    # 更新时间，记录数据最后修改时间
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="更新时间",
        help_text="当前记录的最后更新时间",
    )

    class Meta:
        db_table = "user_profile"
        verbose_name = "用户扩展信息"
        verbose_name_plural = "用户扩展信息"

    def __str__(self):
        """返回用户扩展信息的简要说明。"""
        return self.nickname or self.user.username
