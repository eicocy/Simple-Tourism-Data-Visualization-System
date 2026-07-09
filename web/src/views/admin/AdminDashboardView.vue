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
        <span class="summary-label">国家总数</span>
        <strong>{{ reportCards.total_countries }}</strong>
      </article>
      <article class="summary-card">
        <span class="summary-label">用户总数</span>
        <strong>{{ reportCards.total_users }}</strong>
      </article>
      <article class="summary-card">
        <span class="summary-label">推荐记录数</span>
        <strong>{{ reportCards.total_recommendations }}</strong>
      </article>
      <article class="summary-card">
        <span class="summary-label">热门洲别</span>
        <strong>{{ reportCards.popular_continent }}</strong>
        <small>{{ popularContinentTip }}</small>
      </article>
    </section>

    <!-- 后台统计报表 -->
    <section class="report-grid">
      <article class="report-panel wide">
        <div class="panel-header">
          <div>
            <h3>安全指数排名</h3>
            <p>基于最新年份国家指标数据，展示安全指数排名前十的国家。</p>
          </div>
          <el-tag type="info">{{ safetyRankingYear }}</el-tag>
        </div>
        <div ref="safetyRankingChartRef" class="chart-box"></div>
      </article>

      <article class="report-panel">
        <div class="panel-header">
          <div>
            <h3>洲别国家数量</h3>
            <p>按洲别统计当前启用国家数量。</p>
          </div>
        </div>
        <div ref="continentPieChartRef" class="chart-box"></div>
      </article>

      <article class="report-panel">
        <div class="panel-header">
          <div>
            <h3>推荐次数趋势</h3>
            <p>统计最近 14 天系统推荐记录生成次数。</p>
          </div>
        </div>
        <div ref="recommendationTrendChartRef" class="chart-box"></div>
      </article>
    </section>

    <!-- 国家指标 Excel 导入 -->
    <section class="import-panel">
      <div class="panel-header">
        <div>
          <h3>国家指标 Excel 导入</h3>
          <p>管理员可批量维护国家安全、幸福、消费与旅游适宜指数。</p>
        </div>
        <el-tag type="success">.xlsx</el-tag>
      </div>

      <div class="import-toolbar">
        <el-input-number
          v-model="importYear"
          :min="2000"
          :max="2100"
          :step="1"
          controls-position="right"
        />
        <el-upload
          accept=".xlsx"
          :show-file-list="false"
          :before-upload="beforeImportUpload"
          :http-request="handleImportRequest"
        >
          <el-button type="primary" :icon="Upload" :loading="importLoading">
            上传 Excel
          </el-button>
        </el-upload>
      </div>

      <el-alert
        v-if="importResult && !importErrors.length"
        class="import-result"
        type="success"
        show-icon
        :closable="false"
        title="导入成功"
        :description="`共处理 ${importResult.total_rows || 0} 行，新增国家 ${importResult.created_countries || 0} 个，新增指标 ${importResult.created_indicators || 0} 条，更新指标 ${importResult.updated_indicators || 0} 条。`"
      />

      <div v-if="importErrors.length" class="import-error-box">
        <el-alert
          type="error"
          show-icon
          :closable="false"
          title="导入校验失败"
          description="请根据下方错误位置修正 Excel 后重新上传。"
        />
        <el-table :data="importErrors" border size="small" style="width: 100%">
          <el-table-column prop="row" label="行号" width="90" align="center" />
          <el-table-column prop="field" label="字段" min-width="140" />
          <el-table-column prop="message" label="错误原因" min-width="260" />
        </el-table>
      </div>
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
import { computed, nextTick, onBeforeUnmount, onMounted, reactive, ref } from "vue";
import { useRouter } from "vue-router";
import { Upload } from "@element-plus/icons-vue";
import { ElMessage } from "element-plus";

import {
  getAdminReportApi,
  getAdminSummaryApi,
  getAdminUsersApi,
  getCurrentUserApi,
  updateAdminUserApi,
  uploadCountryIndicatorExcelApi,
} from "@/api";
import echarts from "@/plugins/echarts";
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
  popular_continent: "--",
});

const reportCards = reactive({
  total_countries: 0,
  total_users: 0,
  total_recommendations: 0,
  popular_continent: "--",
  popular_continent_count: 0,
  popular_continent_source: "empty",
});

const reportCharts = reactive({
  safety_ranking: {
    year: null,
    results: [],
  },
  continent_country_counts: [],
  recommendation_trend: [],
});

const safetyRankingChartRef = ref(null);
const continentPieChartRef = ref(null);
const recommendationTrendChartRef = ref(null);

let safetyRankingChart = null;
let continentPieChart = null;
let recommendationTrendChart = null;

// 用户表格数据
const userTableData = ref([]);

// Excel 导入状态
const importYear = ref(new Date().getFullYear());
const importLoading = ref(false);
const importResult = ref(null);
const importErrors = computed(() => importResult.value?.errors || []);

const safetyRankingYear = computed(() => {
  return reportCharts.safety_ranking.year
    ? `${reportCharts.safety_ranking.year} 年`
    : "暂无数据";
});

const popularContinentTip = computed(() => {
  if (!reportCards.popular_continent_count) {
    return "暂无统计";
  }
  return reportCards.popular_continent_source === "recommendation"
    ? `推荐 ${reportCards.popular_continent_count} 次`
    : `${reportCards.popular_continent_count} 个国家`;
});

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
  Object.assign(reportCards, {
    total_countries: result.data?.total_countries || reportCards.total_countries,
    total_users: result.data?.total_users || reportCards.total_users,
    total_recommendations:
      result.data?.total_recommendations || reportCards.total_recommendations,
    popular_continent: result.data?.popular_continent || reportCards.popular_continent,
  });
}

async function loadAdminReport() {
  const result = await getAdminReportApi({ silentError: true });
  Object.assign(reportCards, result.data?.cards || {});
  Object.assign(reportCharts.safety_ranking, result.data?.charts?.safety_ranking || {});
  reportCharts.continent_country_counts =
    result.data?.charts?.continent_country_counts || [];
  reportCharts.recommendation_trend =
    result.data?.charts?.recommendation_trend || [];
  renderReportCharts();
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

    await Promise.all([loadAdminSummary(), loadAdminReport(), loadAdminUsers()]);
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

function renderReportCharts() {
  nextTick(() => {
    renderSafetyRankingChart();
    renderContinentPieChart();
    renderRecommendationTrendChart();
  });
}

function renderSafetyRankingChart() {
  if (!safetyRankingChartRef.value) {
    return;
  }

  safetyRankingChart?.dispose();
  safetyRankingChart = echarts.init(safetyRankingChartRef.value);
  const rows = reportCharts.safety_ranking.results || [];
  safetyRankingChart.setOption({
    tooltip: { trigger: "axis" },
    grid: { left: "4%", right: "4%", bottom: "12%", containLabel: true },
    xAxis: {
      type: "category",
      data: rows.map((item) => item.country_name),
      axisLabel: {
        color: "#5f6f7a",
        interval: 0,
        rotate: rows.length > 6 ? 28 : 0,
      },
    },
    yAxis: {
      type: "value",
      max: 100,
      axisLabel: { color: "#5f6f7a" },
    },
    series: [
      {
        name: "安全指数",
        type: "bar",
        barWidth: 28,
        data: rows.map((item) => item.safety_index),
        itemStyle: {
          borderRadius: [8, 8, 0, 0],
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: "#2f6b5a" },
            { offset: 1, color: "#9ad8c5" },
          ]),
        },
      },
    ],
  });
}

function renderContinentPieChart() {
  if (!continentPieChartRef.value) {
    return;
  }

  continentPieChart?.dispose();
  continentPieChart = echarts.init(continentPieChartRef.value);
  continentPieChart.setOption({
    tooltip: { trigger: "item" },
    legend: {
      bottom: 0,
      textStyle: { color: "#5f6f7a" },
    },
    series: [
      {
        name: "国家数量",
        type: "pie",
        radius: ["42%", "68%"],
        center: ["50%", "45%"],
        data: reportCharts.continent_country_counts.map((item) => ({
          name: item.continent,
          value: item.count,
        })),
        itemStyle: {
          borderColor: "#ffffff",
          borderWidth: 2,
        },
      },
    ],
  });
}

function renderRecommendationTrendChart() {
  if (!recommendationTrendChartRef.value) {
    return;
  }

  recommendationTrendChart?.dispose();
  recommendationTrendChart = echarts.init(recommendationTrendChartRef.value);
  const rows = reportCharts.recommendation_trend || [];
  recommendationTrendChart.setOption({
    tooltip: { trigger: "axis" },
    grid: { left: "4%", right: "4%", bottom: "8%", containLabel: true },
    xAxis: {
      type: "category",
      boundaryGap: false,
      data: rows.map((item) => item.date.slice(5)),
      axisLabel: { color: "#5f6f7a" },
    },
    yAxis: {
      type: "value",
      minInterval: 1,
      axisLabel: { color: "#5f6f7a" },
    },
    series: [
      {
        name: "推荐次数",
        type: "line",
        smooth: true,
        symbolSize: 8,
        areaStyle: {
          color: "rgba(47, 107, 90, 0.16)",
        },
        lineStyle: {
          width: 3,
          color: "#2f6b5a",
        },
        itemStyle: {
          color: "#2f6b5a",
        },
        data: rows.map((item) => item.count),
      },
    ],
  });
}

function handleResize() {
  safetyRankingChart?.resize();
  continentPieChart?.resize();
  recommendationTrendChart?.resize();
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

function beforeImportUpload(file) {
  const isXlsx = file.name.toLowerCase().endsWith(".xlsx");
  if (!isXlsx) {
    ElMessage.error("请上传 .xlsx 格式的 Excel 文件");
  }
  return isXlsx;
}

async function handleImportRequest(options) {
  importLoading.value = true;
  importResult.value = null;

  try {
    const isAdminReady = await ensureAdminSession();
    if (!isAdminReady) {
      options.onError?.(new Error("当前账号没有管理员权限"));
      return;
    }

    const result = await uploadCountryIndicatorExcelApi(
      options.file,
      { year: importYear.value },
      { silentError: true },
    );

    importResult.value = result.data || {};
    ElMessage.success("国家指标导入成功");
    options.onSuccess?.(result);
    await Promise.all([loadAdminSummary(), loadAdminReport()]);
  } catch (error) {
    importResult.value = error?.response?.data?.data || null;
    ElMessage.error(error?.response?.data?.message || "Excel 导入失败，请检查文件内容");
    options.onError?.(error);
  } finally {
    importLoading.value = false;
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
  window.addEventListener("resize", handleResize);
});

onBeforeUnmount(() => {
  window.removeEventListener("resize", handleResize);
  safetyRankingChart?.dispose();
  continentPieChart?.dispose();
  recommendationTrendChart?.dispose();
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
  grid-template-columns: repeat(4, minmax(0, 1fr));
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
  display: block;
  color: #2e3f61;
  font-size: 28px;
}

.summary-card small {
  display: block;
  margin-top: 8px;
  color: #7b8783;
  font-size: 13px;
}

.report-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18px;
}

.report-panel {
  padding: 24px;
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.94);
  box-shadow: 0 12px 32px rgba(24, 43, 38, 0.08);
}

.report-panel.wide {
  grid-column: 1 / -1;
}

.chart-box {
  height: 340px;
}

.import-panel,
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

.import-toolbar {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.import-result {
  margin-top: 16px;
}

.import-error-box {
  display: grid;
  gap: 14px;
  margin-top: 16px;
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

  .report-grid {
    grid-template-columns: 1fr;
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
