<template>
  <div class="main-layout">
    <!-- 顶部区域，用于展示系统标题与用户操作入口 -->
    <header class="main-header">
      <div class="header-left">
        <h1 class="system-title">安全旅游国家推荐与可视化系统</h1>
        <p class="system-subtitle">基于 Django + Vue 的毕业设计项目</p>
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
      <!-- 侧边导航：根据用户角色展示功能入口 -->
      <aside class="sidebar">
        <el-menu :default-active="activeMenu" class="menu-panel" router>
          <el-menu-item index="/app/recommendation">旅游推荐</el-menu-item>
          <el-menu-item index="/app/visualization">可视化分析</el-menu-item>
          <el-menu-item v-if="userStore.isAdmin" index="/app/countries">国家指标分析</el-menu-item>
          <el-menu-item v-if="userStore.isAdmin" index="/app/algorithm">算法说明</el-menu-item>
          <el-menu-item v-if="userStore.isAdmin" index="/app/admin">管理员中心</el-menu-item>
          <el-menu-item v-if="userStore.isAdmin" index="/app/admin/logs">操作日志</el-menu-item>
        </el-menu>
      </aside>

      <!-- 主内容区域：后续业务页面将在这里渲染 -->
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
import { ElMessage } from "element-plus";

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
    radial-gradient(circle at top left, rgba(48, 140, 122, 0.18), transparent 28%),
    radial-gradient(circle at bottom right, rgba(217, 175, 107, 0.18), transparent 24%),
    linear-gradient(180deg, #f6f7f2 0%, #edf1ea 100%);
}

.main-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 32px;
  border-bottom: 1px solid rgba(37, 61, 54, 0.08);
  background: rgba(255, 255, 255, 0.72);
  backdrop-filter: blur(10px);
}

.system-title {
  margin: 0;
  color: #1f4037;
  font-size: 28px;
  font-weight: 700;
}

.system-subtitle {
  margin: 6px 0 0;
  color: #5a6b66;
  font-size: 14px;
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
  color: #29463f;
  font-weight: 600;
}

.main-body {
  display: grid;
  grid-template-columns: 240px 1fr;
  min-height: calc(100vh - 93px);
}

.sidebar {
  padding: 24px 16px;
}

.menu-panel {
  border: none;
  border-radius: 18px;
  padding: 12px 0;
  background: rgba(255, 255, 255, 0.82);
  box-shadow: 0 16px 40px rgba(31, 64, 55, 0.08);
}

.content-panel {
  padding: 24px 24px 32px 8px;
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
  }

  .content-panel {
    padding: 16px 24px 24px;
  }
}
</style>
