"""用户模块序列化器。"""

from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers

from apps.users.models import UserProfile


# 获取 Django 默认用户模型
User = get_user_model()


class UserProfileSerializer(serializers.ModelSerializer):
    """用户扩展信息序列化器。"""

    class Meta:
        model = UserProfile
        fields = [
            "id",
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
            "last_login",
            "date_joined",
            "role_name",
            "profile",
        ]
        read_only_fields = fields

    def get_profile(self, obj):
        """返回用户扩展资料，不存在时自动补建。"""
        profile, _ = UserProfile.objects.get_or_create(user=obj)
        return UserProfileSerializer(profile).data

    def get_role_name(self, obj):
        """返回当前用户角色名称。"""
        if obj.is_superuser or obj.is_staff:
            return "管理员"
        return "普通用户"


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

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "is_active",
            "is_staff",
            "is_superuser",
            "last_login",
            "date_joined",
            "role_name",
            "profile",
        ]
        read_only_fields = fields

    def get_profile(self, obj):
        """返回扩展资料。"""
        profile, _ = UserProfile.objects.get_or_create(user=obj)
        return UserProfileSerializer(profile).data

    def get_role_name(self, obj):
        """返回角色文本。"""
        if obj.is_superuser or obj.is_staff:
            return "管理员"
        return "普通用户"


class AdminUserUpdateSerializer(serializers.ModelSerializer):
    """管理员用户信息更新序列化器。"""

    nickname = serializers.CharField(required=False, allow_blank=True, write_only=True)

    class Meta:
        model = User
        fields = ["email", "is_active", "is_staff", "nickname"]

    def update(self, instance, validated_data):
        """更新用户基础信息与扩展昵称。"""
        nickname = validated_data.pop("nickname", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if nickname is not None:
            profile, _ = UserProfile.objects.get_or_create(user=instance)
            profile.nickname = nickname
            profile.save(update_fields=["nickname", "updated_at"])

        return instance
