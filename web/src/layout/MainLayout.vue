<template>
  <div class="main-layout">
    <!-- 顶部区域展示系统名称与用户操作入口 -->
    <header class="main-header">
      <div class="header-left">
        <span class="system-mark">旅</span>
        <div>
          <h1 class="system-title">安全旅游分析可视化系统</h1>
          <p class="system-subtitle">国家指标 · 推荐模型 · 风险地图</p>
        </div>
      </div>
      <div class="header-right">
        <div class="user-info">
          <span class="user-name">{{ userStore.displayName }}</span>
          <el-tag :type="userStore.isAdmin ? 'danger' : 'success'">
            {{ userStore.isAdmin ? "管理员" : "普通用户" }}
          </el-tag>
        </div>
        <el-button type="primary" plain @click="goHome">返回首页</el-button>
        <el-button @click="handleLogout">退出登录</el-button>
      </div>
    </header>

    <div class="main-body">
      <!-- 左侧导航根据用户角色展示管理入口 -->
      <aside class="sidebar">
        <div class="sidebar-summary">
          <span>Analysis desk</span>
          <strong>旅游安全指数</strong>
          <b>0-100</b>
        </div>
        <el-menu :default-active="activeMenu" class="menu-panel" router>
          <el-menu-item index="/app/recommendation">国家推荐</el-menu-item>
          <el-menu-item index="/app/visualization">可视化分析</el-menu-item>
          <el-menu-item v-if="userStore.isAdmin" index="/app/countries">国家指标分析</el-menu-item>
          <el-menu-item v-if="userStore.isAdmin" index="/app/algorithm">算法说明</el-menu-item>
          <el-menu-item v-if="userStore.isAdmin" index="/app/admin">管理员后台</el-menu-item>
          <el-menu-item v-if="userStore.isAdmin" index="/app/admin/logs">操作日志</el-menu-item>
        </el-menu>
      </aside>

      <!-- 内容区域：核心业务页面将在这里渲染 -->
      <main class="content-panel">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
// 使用计算属性获取当前激活菜单
import { computed } from "vue";
import { useRoute, useRouter } from "vue-router";

import { fetchCsrfTokenApi, logoutApi } from "@/api";
import { useUserStore } from "@/store";

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();

const activeMenu = computed(() => route.path);

function goHome() {
  router.push("/");
}

async function handleLogout() {
  try {
    await fetchCsrfTokenApi({ silentError: true });
    await logoutApi();
    ElMessage.success("退出登录成功");
  } catch (error) {
    if (!error?.response) {
      ElMessage.error("退出登录失败，请检查后端服务是否正常");
    }
  } finally {
    userStore.clearUserInfo();
    router.push("/");
  }
}
</script>

<style scoped>
.main-layout {
  min-height: 100vh;
  background:
    linear-gradient(90deg, rgba(255, 255, 255, 0.035) 1px, transparent 1px),
    linear-gradient(180deg, rgba(255, 255, 255, 0.035) 1px, transparent 1px),
    #050605;
  background-size: 44px 44px;
}

.main-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  min-height: 78px;
  margin: 8px 8px 0;
  padding: 14px 20px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 8px 8px 0 0;
  background: #f0f0ee;
  color: #171717;
  backdrop-filter: blur(12px);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 14px;
}

.system-mark {
  display: grid;
  width: 46px;
  height: 46px;
  place-items: center;
  border-radius: 8px;
  background: #171717;
  color: #ffffff;
  font-size: 22px;
  font-weight: 900;
}

.system-title {
  margin: 0;
  color: #171717;
  font-size: 25px;
  font-weight: 800;
}

.system-subtitle {
  margin: 6px 0 0;
  color: #63635f;
  font-size: 13px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-right: 8px;
}

.user-name {
  color: #171717;
  font-weight: 700;
}

.main-body {
  display: grid;
  grid-template-columns: 252px 1fr;
  min-height: calc(100vh - 86px);
  margin: 0 8px 8px;
}

.sidebar {
  padding: 18px 14px;
  border-right: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 0 0 0 8px;
  background: #f0f0ee;
}

.sidebar-summary {
  display: grid;
  gap: 6px;
  margin-bottom: 14px;
  padding: 16px;
  border: 1px solid rgba(23, 23, 23, 0.1);
  border-radius: 8px;
  background:
    linear-gradient(135deg, rgba(199, 255, 100, 0.2), transparent 58%),
    #ffffff;
}

.sidebar-summary span {
  color: #6f6f69;
  font-size: 12px;
  text-transform: uppercase;
}

.sidebar-summary strong {
  color: #171717;
}

.sidebar-summary b {
  color: #286a73;
  font-size: 30px;
  line-height: 1;
}

.menu-panel {
  border: none;
  border-radius: 8px;
  padding: 12px 0;
  background: transparent;
}

.menu-panel :deep(.el-menu-item) {
  height: 46px;
  margin: 4px 8px;
  border-radius: 8px;
  color: #373a38;
  font-weight: 700;
}

.menu-panel :deep(.el-menu-item:hover) {
  background: #ffffff;
  color: #171717;
}

.menu-panel :deep(.el-menu-item.is-active) {
  background: #171717;
  color: #ffffff;
}

.content-panel {
  padding: 22px 24px 34px;
  overflow: hidden;
  border-radius: 0 0 8px 0;
}

@media (max-width: 900px) {
  .main-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .header-right {
    flex-wrap: wrap;
  }

  .main-body {
    grid-template-columns: 1fr;
  }

  .sidebar {
    padding: 16px 24px 0;
    border-radius: 0;
  }

  .content-panel {
    padding: 16px 24px 24px;
    border-radius: 0 0 8px 8px;
  }
}
</style>
