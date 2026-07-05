"""ASGI 部署入口文件。"""

import os

from django.core.asgi import get_asgi_application


# 指定 Django 配置模块
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# 暴露 ASGI 应用对象
application = get_asgi_application()
