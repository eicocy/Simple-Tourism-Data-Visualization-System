# 阿里云宝塔部署总结

本项目已部署到阿里云服务器，使用宝塔 Linux 面板管理基础服务。整体部署方式为前后端分离：前端 Vue 项目构建为静态文件，由 Nginx 对外提供访问；后端 Django 项目通过 Gunicorn 运行在本机 `127.0.0.1:8000`，再由 Nginx 将 `/api/` 和 `/admin/` 请求反向代理到后端；数据库使用 MySQL 8.0。

## 当前部署结构

- 项目目录：`/www/wwwroot/wdzz`
- 后端目录：`/www/wwwroot/wdzz/server`
- 前端目录：`/www/wwwroot/wdzz/web`
- 前端构建目录：`/www/wwwroot/wdzz/web/dist`
- 后端虚拟环境：`/www/wwwroot/wdzz/server/.venv`
- 后端启动端口：`127.0.0.1:8000`
- 对外访问地址：`http://47.108.204.236/`
- 健康检查地址：`http://47.108.204.236/api/health/`

## 服务分工

- Nginx：负责前端页面访问、静态资源、`/api/` 反向代理。
- Gunicorn：负责运行 Django 后端服务。
- Supervisor：负责守护 Gunicorn，保证后端进程异常退出后自动重启。
- MySQL：保存用户、国家指标、推荐记录等业务数据。

## 已完成事项

- 安装并使用 Python 3.11 创建后端虚拟环境。
- 安装后端依赖并完成 Django 数据库迁移。
- 安装前端依赖并完成 `npm run build`。
- 配置 Nginx 指向 `/www/wwwroot/wdzz/web/dist`。
- 配置 Nginx 将 `/api/` 代理到 `127.0.0.1:8000`。
- 将本地 MySQL 数据通过 `mysqldump --result-file` 重新导出并导入服务器。
- 配置 Supervisor 守护 `wdzz-backend` 后端进程。
- 增加 `/root/wdzz_boot.sh` 和 `wdzz-boot.service` 作为开机兜底启动脚本，用于启动 MySQL、Nginx、Supervisor 后端。

## 常用命令

检查后端健康状态：

```bash
curl http://127.0.0.1:8000/api/health/
curl http://47.108.204.236/api/health/
```

查看后端进程：

```bash
ps -ef | grep gunicorn
```

查看 Supervisor 状态：

```bash
supervisorctl -c /etc/supervisor/supervisord.conf status
```

重启后端：

```bash
supervisorctl -c /etc/supervisor/supervisord.conf restart wdzz-backend
```

重启 Nginx：

```bash
/etc/init.d/nginx restart
```

查看 MySQL 状态：

```bash
/etc/init.d/mysqld status
```

手动执行开机兜底脚本：

```bash
/root/wdzz_boot.sh
```

查看开机兜底脚本日志：

```bash
tail -n 100 /var/log/wdzz_boot.log
```

## 注意事项

- 不需要开放服务器 `8000` 端口，后端只监听本机，由 Nginx 代理即可。
- 阿里云安全组通常只需要开放 `80`，后续配置 HTTPS 时再开放 `443`。
- 不建议用 `nohup` 长期运行后端，后端应交给 Supervisor 管理。
- 如果服务器重启后网站页面能打开但接口失败，优先检查 MySQL 是否启动，再检查 Supervisor 中的 `wdzz-backend`。
- 如果要重新迁移数据库，Windows PowerShell 中不要使用 `>` 重定向 `mysqldump` 输出，应使用 `--result-file`，避免 SQL 文件被转成 UTF-16 编码。
