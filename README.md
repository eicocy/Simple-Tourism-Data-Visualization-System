# Simple Tourism Data Visualization System

基于 Django + Vue 的安全旅游国家推荐与可视化系统。系统围绕国家安全指数、旅游适宜指数、幸福指数、消费水平、签证便利度等指标，提供国家数据管理、旅游推荐、推荐结果解释、地图与图表分析、管理员后台和操作日志等功能。

当前版本：`v1.1.0`

## 功能概览

- 首页展示：参考作品集风格重构首页，包含动态推荐仪表盘、旅行信号矩阵、世界地图预览和可交互入口。
- 国家推荐：根据预算、洲别偏好、安全要求等输入生成推荐结果，并展示推荐依据。
- 可视化分析：通过世界地图、柱状图、雷达图等方式展示国家指标与推荐表现。
- 国家分析：支持国家列表查询、洲别统计、国家详情页和多维指标图表。
- 管理员中心：提供用户管理、国家指标数据表格、Excel 上传、业务统计图表和操作日志。
- 后端接口：基于 Django REST Framework 提供用户、国家、推荐、可视化、日志等 API。

## 技术栈

- 后端：Python、Django、Django REST Framework、MySQL、Simple JWT、drf-spectacular
- 前端：Vue 3、Vite、Vue Router、Pinia、Axios、Tailwind CSS、Element Plus、ECharts
- 数据处理：Django ORM、Python 导入脚本、指标归一化、规则加权推荐
- 构建优化：Element Plus 按需引入、ECharts 动态加载、路由级懒加载、Rollup manualChunks、rollup-plugin-visualizer

## 目录结构

```text
server/                 Django 后端项目
  apps/                 用户、国家、推荐、可视化、日志等业务模块
  config/               Django 配置与路由入口
  scripts/              数据导入、洲别更新、演示数据初始化脚本
web/                    Vue 前端项目
  src/                  前端源码
    components/         通用组件与首页组件
    layout/             主布局
    plugins/            ECharts 等前端插件
    router/             前端路由
    styles/             全局样式
    views/              业务页面
  public/               静态资源目录
```

## 本地后端运行

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

后端默认地址：

```text
http://127.0.0.1:8000
```

## 本地前端运行

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

前端默认地址：

```text
http://127.0.0.1:5173
```

## 常用账号

演示环境可使用初始化脚本创建的管理员账号登录：

```text
用户名：admin
密码：lll190
```

如本地数据库未初始化，请先执行后端迁移和演示数据脚本。

## 构建与分析

前端生产构建：

```bash
cd web
npm run build
```

本地预览生产构建：

```bash
cd web
npm run preview
```

生成包体分析报告：

```bash
cd web
npm run analyze
```

分析报告输出路径：

```text
web/dist/bundle-stats.html
```

后端基础检查：

```bash
cd server
python manage.py check
```

## 前端构建优化说明

`v1.1.0` 已完成以下前端优化：

- Element Plus 使用 `unplugin-auto-import` 与 `unplugin-vue-components` 按需引入。
- ECharts 改为 `loadEcharts()` 动态加载，避免普通推荐页提前下载图表依赖。
- 首页、可视化页、国家分析/详情页、管理员图表使用可见性延迟初始化。
- `MainLayout` 和页面路由使用懒加载，降低首屏入口负载。
- Rollup `manualChunks` 拆分 Vue、网络库、Element Plus、ECharts、zrender 等依赖。
- `npm run build` 已消除 Vite `Some chunks are larger than 500 kB` 警告。
- 当前仍保留少量 ECharts circular chunk 提示；这是第三方图表库拆包后的循环引用提示，不影响构建产物运行。

## 视觉优化说明

`v1.1.0` 对首页和业务页面做了统一视觉优化：

- 首页采用深色作品集式仪表盘布局，强化安全旅游推荐系统的第一屏识别度。
- 首页动态模块包含指数仪表盘、旅行信号矩阵、地图预览和数据芯片。
- `Safety / Budget / Visa / Index / Map` 数据芯片已调整为正向水平布局，保留轻微上下浮动，不再使用斜向 3D 旋转。
- 推荐页、可视化页、国家分析页、国家详情页、管理员页和日志页统一为深色分析台风格。
- 所有动态效果遵守 `prefers-reduced-motion`，系统开启减少动态效果时会自动降低动画强度。

## 数据说明

当前仓库不直接提交真实导入数据。系统可通过 `server/scripts/seed_demo_data.py` 生成一组毕业设计演示数据，用于本地运行、接口联调和前端展示。真实指标导入脚本位于 `server/scripts/`，包括安全指数、幸福指数、人均 GDP/消费指数、签证便利度和旅游适宜指数重算等脚本。

## 未提交到仓库的内容

本仓库只保留可运行代码与必要示例配置，不包含以下导入文件或生成材料：

- `数据分析用/`：原始 Excel、CSV、PDF 数据文件
- `server/scripts/*.xlsx`：脚本使用的导入源数据副本
- `server/continent_names.txt`：独立国家名清单，不参与系统运行
- `论文截图素材/`、`docx_rendered/`、`tmp/`、`lo_out/`、`outputs/`：论文截图、答辩、渲染和临时产物
- `web/node_modules/`、`web/dist/`：前端依赖和构建产物
- `.env.*`、`*.log`、`__pycache__/`、`*.pyc`：本地环境、日志和缓存

如需导入真实数据，请自行将对应 Excel/CSV 文件放到 `server/scripts/`，或修改脚本中的默认文件路径。

## 发布记录

### v1.1.0

- 完成前端包体优化：按需引入、懒加载、图表延迟初始化和 vendor 拆包。
- 优化首页动态展示区和业务页面统一视觉风格。
- 修复首页指标数据芯片斜歪问题。
- 保持后端接口、权限、推荐算法和业务计算逻辑不变。

### v1.0.0

- 完成 Django + Vue 安全旅游国家推荐与可视化系统基础功能。
- 支持国家指标管理、推荐流程、可视化页面、管理员后台和部署配置。

## 部署说明

阿里云宝塔部署记录见 [aliyun_deploy_summary.md](aliyun_deploy_summary.md)。

生产部署建议：

- 前端执行 `npm run build`，将 `web/dist` 交给 Nginx 提供静态访问。
- 后端使用 Gunicorn 运行 Django，并由 Supervisor 守护进程。
- Nginx 将 `/api/` 和 `/admin/` 反向代理到 `127.0.0.1:8000`。
- MySQL 保存用户、国家指标、推荐记录、操作日志等业务数据。
