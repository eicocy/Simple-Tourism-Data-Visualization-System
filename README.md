# Simple Tourism Data Visualization System

基于 Django + Vue 的安全旅游国家推荐与可视化系统。项目围绕国家安全指数、旅游适宜指数、幸福指数、消费指数和签证便利度等指标，提供国家查询、旅游推荐、推荐结果展示、图表分析和管理员用户管理功能。

## 技术栈

- 后端：Python、Django、Django REST Framework、MySQL
- 前端：Vue 3、Vite、Vue Router、Pinia、Axios、Element Plus、ECharts
- 数据处理：Python 导入脚本、Django ORM、指标归一化与规则加权推荐

## 目录结构

```text
server/                 Django 后端项目
  apps/                 用户、国家、推荐、可视化等业务模块
  config/               Django 配置与路由入口
  scripts/              数据导入、洲别更新、演示数据初始化脚本
web/                    Vue 前端项目
  src/                  前端源码
  public/               静态资源目录
```

## 未提交到仓库的内容

本仓库只保留可运行代码与必要示例配置，不包含以下导入文件或生成材料：

- `数据分析用/`：原始 Excel、CSV、PDF 数据文件
- `server/scripts/*.xlsx`：脚本使用的导入源数据副本
- `server/continent_names.txt`：独立国家名清单，不参与系统运行
- `论文截图素材/`、`docx_rendered/`、`tmp/`、`lo_out/`：论文截图、答辩、渲染和临时产物
- `web/node_modules/`、`web/dist/`：前端依赖和构建产物
- `.env.*`、`*.log`、`__pycache__/`、`*.pyc`：本地环境、日志和缓存

如需导入真实数据，请自行将对应 Excel/CSV 文件放到 `server/scripts/`，或修改脚本中的默认文件路径。

## 后端运行

进入后端目录：

```bash
cd server
```

创建并激活虚拟环境：

```bash
python -m venv .venv
.venv\Scripts\activate
```

安装依赖：

```bash
pip install -r requirements.txt
```

创建环境变量文件：

```bash
copy .env.example .env
```

根据本机 MySQL 修改 `.env` 中的数据库配置，然后执行迁移：

```bash
python manage.py migrate
```

写入演示数据：

```bash
python scripts/seed_demo_data.py
python scripts/recalculate_tourism_index.py
```

启动后端：

```bash
python manage.py runserver 127.0.0.1:8000
```

## 前端运行

进入前端目录：

```bash
cd web
```

安装依赖：

```bash
npm install
```

创建前端环境变量文件：

```bash
copy .env.example .env.development
```

启动开发服务器：

```bash
npm run dev
```

默认访问地址为：

```text
http://127.0.0.1:5173
```

## 常用验证命令

后端基础检查：

```bash
cd server
python manage.py check
```

前端构建检查：

```bash
cd web
npm run build
```

## 数据说明

当前仓库不直接提交真实导入数据。系统可通过 `server/scripts/seed_demo_data.py` 生成一组毕业设计演示数据，用于本地运行、接口联调和前端展示。真实指标导入脚本位于 `server/scripts/`，包括安全指数、幸福指数、人均 GDP/消费指数、签证便利度和旅游适宜指数重算等脚本。
