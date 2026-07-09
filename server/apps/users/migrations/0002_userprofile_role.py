from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="userprofile",
            name="role",
            field=models.CharField(
                choices=[("user", "普通用户"), ("admin", "管理员")],
                default="user",
                help_text="系统角色，普通用户为 user，管理员为 admin。",
                max_length=20,
                verbose_name="用户角色",
            ),
        ),
    ]
