<template>
  <div class="admin-page">
    <!-- 页面头部说明 -->
    <section class="admin-hero">
      <div>
        <p class="hero-tag">Admin Center</p>
        <h2>管理员中心</h2>
        <p class="hero-desc">
          本页面接入后端数据库中的真实用户与业务统计数据，便于管理员查看系统运行情况并维护用户状态。
        </p>
      </div>
      <div class="hero-actions">
        <el-input
          v-model="searchKeyword"
          placeholder="按用户名或邮箱搜索用户"
          clearable
          style="width: 260px"
          @keyup.enter="handleSearchUsers"
        />
        <el-button @click="handleSearchUsers">查询用户</el-button>
        <el-button type="primary" :loading="loading" @click="loadAllData">刷新数据</el-button>
      </div>
    </section>

    <!-- 统计卡片 -->
    <section class="summary-grid">
      <article class="summary-card">
        <span class="summary-label">系统用户总数</span>
        <strong>{{ summary.total_users }}</strong>
      </article>
      <article class="summary-card">
        <span class="summary-label">活跃用户数</span>
        <strong>{{ summary.active_users }}</strong>
      </article>
      <article class="summary-card">
        <span class="summary-label">管理员人数</span>
        <strong>{{ summary.admin_users }}</strong>
      </article>
      <article class="summary-card">
        <span class="summary-label">启用国家数</span>
        <strong>{{ summary.total_countries }}</strong>
      </article>
      <article class="summary-card">
        <span class="summary-label">推荐记录数</span>
        <strong>{{ summary.total_recommendations }}</strong>
      </article>
    </section>

    <!-- 用户管理表格 -->
    <section class="table-panel">
      <div class="panel-header">
        <div>
          <h3>用户管理</h3>
          <p>管理员可查看系统用户列表，并调整用户启用状态与管理员权限。</p>
        </div>
        <el-tag type="info">共 {{ userTableData.length }} 位用户</el-tag>
      </div>

      <el-table :data="userTableData" border stripe v-loading="loading" style="width: 100%">
        <el-table-column prop="username" label="用户名" min-width="140" />
        <el-table-column prop="nickname" label="昵称" min-width="140" />
        <el-table-column prop="email" label="邮箱" min-width="180" />
        <el-table-column prop="role_name" label="角色" min-width="100" align="center">
          <template #default="scope">
            <el-tag :type="scope.row.is_staff ? 'danger' : 'success'">
              {{ scope.row.role_name }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="启用状态" min-width="110" align="center">
          <template #default="scope">
            <el-switch
              :model-value="scope.row.is_active"
              @change="(value) => handleUpdateUser(scope.row, { is_active: value })"
            />
          </template>
        </el-table-column>
        <el-table-column prop="is_staff" label="管理员" min-width="110" align="center">
          <template #default="scope">
            <el-switch
              :model-value="scope.row.is_staff"
              @change="(value) => handleUpdateUser(scope.row, { is_staff: value })"
            />
          </template>
        </el-table-column>
        <el-table-column prop="date_joined" label="注册时间" min-width="180" />
        <el-table-column prop="last_login" label="最后登录" min-width="180" />
      </el-table>
    </section>
  </div>
</template>

<script setup>
// 管理员中心页面逻辑
import { onMounted, reactive, ref } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";

import { getAdminSummaryApi, getAdminUsersApi, getCurrentUserApi, updateAdminUserApi } from "@/api";
import { useUserStore } from "@/store";

const router = useRouter();
const userStore = useUserStore();

// 加载状态
const loading = ref(false);

// 搜索关键字
const searchKeyword = ref("");

// 管理员概览数据
const summary = reactive({
  total_users: 0,
  active_users: 0,
  admin_users: 0,
  total_countries: 0,
  total_recommendations: 0,
});

// 用户表格数据
const userTableData = ref([]);

function formatDate(value) {
  if (!value) {
    return "--";
  }
  return new Date(value).toLocaleString("zh-CN", { hour12: false });
}

function redirectToLogin() {
  router.push({
    path: "/login",
    query: { redirect: "/app/admin" },
  });
}

async function ensureAdminSession() {
  try {
    const result = await getCurrentUserApi({ silentError: true });
    userStore.setUserInfo(result.data);

    if (!userStore.isAdmin) {
      ElMessage.warning("请使用管理员账号登录后查看后台数据");
      router.push("/app/recommendation");
      return false;
    }

    return true;
  } catch (error) {
    userStore.clearUserInfo();
    ElMessage.warning("管理员登录状态已失效，请重新登录");
    redirectToLogin();
    return false;
  }
}

async function loadAdminSummary() {
  const result = await getAdminSummaryApi({ silentError: true });
  Object.assign(summary, result.data || {});
}

async function loadAdminUsers() {
  const result = await getAdminUsersApi(
    { search: searchKeyword.value },
    { silentError: true },
  );
  userTableData.value = (result.data?.results || []).map((item) => ({
    ...item,
    nickname: item.profile?.nickname || "--",
    email: item.email || "--",
    date_joined: formatDate(item.date_joined),
    last_login: formatDate(item.last_login),
  }));
}

async function loadAllData() {
  loading.value = true;
  try {
    const isAdminReady = await ensureAdminSession();
    if (!isAdminReady) {
      return;
    }

    await Promise.all([loadAdminSummary(), loadAdminUsers()]);
  } catch (error) {
    const detail = error?.response?.data?.detail || "";
    if (detail.includes("身份认证信息未提供") || detail.includes("Authentication credentials")) {
      userStore.clearUserInfo();
      ElMessage.warning("管理员登录状态已失效，请重新登录");
      redirectToLogin();
      return;
    }
    ElMessage.error("管理员数据加载失败，请检查后端服务或当前账号权限");
  } finally {
    loading.value = false;
  }
}

async function handleSearchUsers() {
  loading.value = true;
  try {
    const isAdminReady = await ensureAdminSession();
    if (!isAdminReady) {
      return;
    }
    await loadAdminUsers();
  } catch (error) {
    ElMessage.error("用户列表查询失败，请检查后端服务或当前账号权限");
  } finally {
    loading.value = false;
  }
}

async function handleUpdateUser(row, payload) {
  try {
    const isAdminReady = await ensureAdminSession();
    if (!isAdminReady) {
      return;
    }

    await updateAdminUserApi(row.id, payload, { silentError: true });
    ElMessage.success("用户信息更新成功");
    await loadAllData();
  } catch (error) {
    ElMessage.error("更新失败，请检查后端服务或当前账号权限");
  }
}

onMounted(() => {
  loadAllData();
});
</script>

<style scoped>
.admin-page {
  display: grid;
  gap: 20px;
}

.admin-hero {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
  padding: 28px;
  border-radius: 24px;
  background: linear-gradient(135deg, #3b2f5d 0%, #6849a7 100%);
  color: #faf8ff;
  box-shadow: 0 18px 42px rgba(47, 35, 79, 0.16);
}

.hero-tag {
  margin: 0 0 10px;
  color: rgba(250, 248, 255, 0.72);
  text-transform: uppercase;
  letter-spacing: 0.12em;
  font-size: 12px;
}

.admin-hero h2 {
  margin: 0 0 10px;
  font-size: 30px;
}

.hero-desc {
  margin: 0;
  max-width: 760px;
  line-height: 1.7;
  color: rgba(250, 248, 255, 0.88);
}

.hero-actions {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 16px;
}

.summary-card {
  padding: 22px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.95);
  box-shadow: 0 12px 30px rgba(26, 43, 39, 0.08);
}

.summary-label {
  display: block;
  margin-bottom: 10px;
  color: #6f7b76;
  font-size: 14px;
}

.summary-card strong {
  color: #2e3f61;
  font-size: 28px;
}

.table-panel {
  padding: 24px;
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.94);
  box-shadow: 0 12px 32px rgba(24, 43, 38, 0.08);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 18px;
}

.panel-header h3 {
  margin: 0 0 8px;
  color: #28473f;
}

.panel-header p {
  margin: 0;
  color: #667570;
  line-height: 1.6;
}

@media (max-width: 1200px) {
  .summary-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 900px) {
  .admin-hero {
    flex-direction: column;
    align-items: flex-start;
  }
}

@media (max-width: 640px) {
  .summary-grid {
    grid-template-columns: 1fr;
  }

  .hero-actions {
    width: 100%;
  }
}
</style>
