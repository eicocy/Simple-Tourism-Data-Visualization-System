// 路由配置文件
import { createRouter, createWebHistory } from "vue-router";

import { fetchCsrfTokenApi, getCurrentUserApi } from "@/api";
import MainLayout from "@/layout/MainLayout.vue";
import { useUserStore } from "@/store";

// 路由表设计说明：
// 1. 首页与登录页允许匿名访问
// 2. /app 下的业务页面要求登录后访问
// 3. 管理员页面要求当前用户具备管理员权限
const routes = [
  {
    path: "/",
    name: "home",
    component: () => import("@/views/dashboard/DashboardView.vue"),
    meta: {
      title: "系统首页",
      requiresAuth: false,
    },
  },
  {
    path: "/dashboard",
    redirect: "/",
  },
  {
    path: "/login",
    name: "login",
    component: () => import("@/views/login/LoginView.vue"),
    meta: {
      title: "用户登录",
      requiresAuth: false,
    },
  },
  {
    path: "/app",
    component: MainLayout,
    redirect: "/app/recommendation",
    meta: {
      requiresAuth: true,
    },
    children: [
      {
        path: "recommendation",
        name: "recommendation",
        component: () => import("@/views/recommendation/RecommendationView.vue"),
        meta: {
          title: "旅游推荐",
          requiresAuth: true,
          roles: ["user", "admin"],
        },
      },
      {
        path: "recommendation/result",
        name: "recommendation-result",
        component: () => import("@/views/recommendation/RecommendationResultView.vue"),
        meta: {
          title: "推荐结果",
          requiresAuth: true,
          roles: ["user", "admin"],
        },
      },
      {
        path: "visualization",
        name: "visualization",
        component: () => import("@/views/visualization/VisualizationView.vue"),
        meta: {
          title: "可视化分析",
          requiresAuth: true,
          roles: ["user", "admin"],
        },
      },
      {
        path: "countries",
        name: "country-analysis",
        component: () => import("@/views/countries/CountryAnalysisView.vue"),
        meta: {
          title: "国家指标分析",
          requiresAuth: true,
          roles: ["admin"],
        },
      },
      {
        path: "countries/:id",
        name: "country-detail",
        component: () => import("@/views/countries/CountryDetailView.vue"),
        meta: {
          title: "国家详情",
          requiresAuth: true,
          roles: ["admin"],
        },
      },
      {
        path: "algorithm",
        name: "algorithm-info",
        component: () => import("@/views/algorithm/AlgorithmInfoView.vue"),
        meta: {
          title: "算法说明",
          requiresAuth: true,
          roles: ["admin"],
        },
      },
      {
        path: "admin",
        name: "admin-dashboard",
        component: () => import("@/views/admin/AdminDashboardView.vue"),
        meta: {
          title: "管理员中心",
          requiresAuth: true,
          requiresAdmin: true,
          roles: ["admin"],
        },
      },
      {
        path: "admin/logs",
        name: "operation-logs",
        component: () => import("@/views/admin/OperationLogView.vue"),
        meta: {
          title: "操作日志",
          requiresAuth: true,
          requiresAdmin: true,
          roles: ["admin"],
        },
      },
    ],
  },
];

// 创建路由实例
const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 };
  },
});

let authBootstrapPromise = null;

// 启动时同步 Session 与前端状态
async function bootstrapAuthState() {
  const userStore = useUserStore();

  if (userStore.initialized) {
    return;
  }

  if (authBootstrapPromise) {
    await authBootstrapPromise;
    return;
  }

  authBootstrapPromise = (async () => {
    userStore.hydrateUserInfo();

    try {
      await fetchCsrfTokenApi({ silentError: true });
      const result = await getCurrentUserApi({ silentError: true });
      userStore.setUserInfo(result.data);
    } catch (error) {
      userStore.clearUserInfo();
    } finally {
      userStore.markInitialized();
      authBootstrapPromise = null;
    }
  })();

  await authBootstrapPromise;
}

// 基础路由守卫
router.beforeEach(async (to, from, next) => {
  document.title = `${to.meta?.title || "系统页面"} - 安全旅游国家推荐系统`;

  const userStore = useUserStore();
  await bootstrapAuthState();

  if (to.meta?.requiresAuth && !userStore.isAuthenticated) {
    next({
      path: "/login",
      query: { redirect: to.fullPath },
    });
    return;
  }

  if (to.meta?.requiresAdmin && !userStore.isAdmin) {
    next("/app/recommendation");
    return;
  }

  const allowedRoles = to.meta?.roles || [];
  const currentRole = userStore.isAdmin ? "admin" : "user";
  if (allowedRoles.length && !allowedRoles.includes(currentRole)) {
    next(userStore.isAdmin ? "/app/admin" : "/app/recommendation");
    return;
  }

  if (to.path === "/login" && userStore.isAuthenticated) {
    next(userStore.isAdmin ? "/app/admin" : "/app/recommendation");
    return;
  }

  next();
});

export default router;
