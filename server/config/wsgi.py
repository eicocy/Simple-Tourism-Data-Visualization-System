"""WSGI 部署入口文件。"""

import os

from django.core.wsgi import get_wsgi_application


# 指定 Django 配置模块
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# 暴露 WSGI 应用对象
application = get_wsgi_application()
