"""用户模块序列化器。"""

from django.contrib.auth import authenticate, get_user_model
from drf_spectacular.utils import OpenApiTypes, extend_schema_field
from rest_framework import serializers

from common.permissions import get_user_role
from apps.users.models import UserProfile


# 获取 Django 默认用户模型
User = get_user_model()


class UserProfileSerializer(serializers.ModelSerializer):
    """用户扩展信息序列化器。"""

    class Meta:
        model = UserProfile
        fields = [
            "id",
            "role",
            "nickname",
            "gender",
            "age",
            "phone",
            "bio",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class UserSerializer(serializers.ModelSerializer):
    """用户基础信息序列化器。"""

    # 通过方法字段保证管理员用户也能正常返回扩展资料
    profile = serializers.SerializerMethodField()
    # 返回当前用户角色，便于前端区分普通用户与管理员
    role_name = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_active",
            "is_staff",
            "is_superuser",
            "role",
            "last_login",
            "date_joined",
            "role_name",
            "profile",
        ]
        read_only_fields = fields

    @extend_schema_field(UserProfileSerializer)
    def get_profile(self, obj):
        """返回用户扩展资料，不存在时自动补建。"""
        profile, _ = UserProfile.objects.get_or_create(user=obj)
        return UserProfileSerializer(profile).data

    @extend_schema_field(OpenApiTypes.STR)
    def get_role_name(self, obj):
        """返回当前用户角色名称。"""
        if get_user_role(obj) == "admin":
            return "管理员"
        return "普通用户"

    @extend_schema_field(OpenApiTypes.STR)
    def get_role(self, obj):
        """返回当前用户角色标识。"""
        return get_user_role(obj)


class RegisterSerializer(serializers.ModelSerializer):
    """用户注册序列化器。"""

    password = serializers.CharField(
        write_only=True,
        min_length=6,
        style={"input_type": "password"},
        help_text="用户登录密码，长度不少于 6 位。",
    )
    confirm_password = serializers.CharField(
        write_only=True,
        min_length=6,
        style={"input_type": "password"},
        help_text="确认密码，必须与密码保持一致。",
    )
    nickname = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
        help_text="用户昵称，可选。",
    )
    email = serializers.EmailField(
        required=False,
        allow_blank=True,
        help_text="用户邮箱，可选。",
    )

    class Meta:
        model = User
        fields = [
            "username",
            "password",
            "confirm_password",
            "email",
            "nickname",
        ]

    def validate_username(self, value):
        """校验用户名是否重复。"""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("该用户名已存在，请更换用户名。")
        return value

    def validate(self, attrs):
        """校验两次密码输入是否一致。"""
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({"confirm_password": "两次输入的密码不一致。"})
        return attrs

    def create(self, validated_data):
        """创建用户及扩展信息。"""
        nickname = validated_data.pop("nickname", "")
        validated_data.pop("confirm_password", None)

        user = User.objects.create_user(**validated_data)
        UserProfile.objects.get_or_create(user=user, defaults={"nickname": nickname})
        return user


class LoginSerializer(serializers.Serializer):
    """用户登录序列化器。"""

    username = serializers.CharField(help_text="登录用户名。")
    password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
        help_text="登录密码。",
    )

    def validate(self, attrs):
        """校验用户名和密码是否正确。"""
        request = self.context.get("request")
        username = attrs.get("username")
        password = attrs.get("password")
        user = authenticate(request=request, username=username, password=password)

        if not user:
            raise serializers.ValidationError("用户名或密码错误。")
        if not user.is_active:
            raise serializers.ValidationError("当前用户已被禁用，无法登录。")

        attrs["user"] = user
        return attrs


class UserUpdateSerializer(serializers.ModelSerializer):
    """用户基础信息更新序列化器。"""

    class Meta:
        model = User
        fields = ["email", "first_name", "last_name"]


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """用户扩展信息更新序列化器。"""

    class Meta:
        model = UserProfile
        fields = ["nickname", "gender", "age", "phone", "bio"]


class ChangePasswordSerializer(serializers.Serializer):
    """密码修改序列化器。"""

    old_password = serializers.CharField(write_only=True, style={"input_type": "password"})
    new_password = serializers.CharField(write_only=True, min_length=6, style={"input_type": "password"})
    confirm_password = serializers.CharField(write_only=True, min_length=6, style={"input_type": "password"})

    def validate_old_password(self, value):
        """校验旧密码是否正确。"""
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("原密码输入错误。")
        return value

    def validate(self, attrs):
        """校验新密码与确认密码是否一致。"""
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({"confirm_password": "两次输入的新密码不一致。"})
        return attrs


class AdminUserListSerializer(serializers.ModelSerializer):
    """管理员用户列表序列化器。"""

    profile = serializers.SerializerMethodField()
    role_name = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "is_active",
            "is_staff",
            "is_superuser",
            "role",
            "last_login",
            "date_joined",
            "role_name",
            "profile",
        ]
        read_only_fields = fields

    @extend_schema_field(UserProfileSerializer)
    def get_profile(self, obj):
        """返回扩展资料。"""
        profile, _ = UserProfile.objects.get_or_create(user=obj)
        return UserProfileSerializer(profile).data

    @extend_schema_field(OpenApiTypes.STR)
    def get_role_name(self, obj):
        """返回角色文本。"""
        if get_user_role(obj) == "admin":
            return "管理员"
        return "普通用户"

    @extend_schema_field(OpenApiTypes.STR)
    def get_role(self, obj):
        """返回角色标识。"""
        return get_user_role(obj)


class AdminUserUpdateSerializer(serializers.ModelSerializer):
    """管理员用户信息更新序列化器。"""

    nickname = serializers.CharField(required=False, allow_blank=True, write_only=True)
    role = serializers.ChoiceField(
        choices=UserProfile.ROLE_CHOICES,
        required=False,
        write_only=True,
    )

    class Meta:
        model = User
        fields = ["email", "is_active", "is_staff", "role", "nickname"]

    def update(self, instance, validated_data):
        """更新用户基础信息与扩展昵称。"""
        nickname = validated_data.pop("nickname", None)
        role = validated_data.pop("role", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if role == "admin":
            instance.is_staff = True
        elif role == "user":
            instance.is_staff = False
        instance.save()

        if nickname is not None or role is not None:
            profile, _ = UserProfile.objects.get_or_create(user=instance)
            update_fields = ["updated_at"]
            if nickname is not None:
                profile.nickname = nickname
                update_fields.append("nickname")
            if role is not None:
                profile.role = role
                update_fields.append("role")
            profile.save(update_fields=update_fields)

        return instance
