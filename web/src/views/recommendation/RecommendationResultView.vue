<template>
  <div class="result-page">
    <!-- 页面头部说明 -->
    <section class="result-hero">
      <div>
        <p class="hero-tag">Result Center</p>
        <h2>安全旅游推荐结果</h2>
        <p class="hero-desc">
          用数据表展示推荐国家排序，并保留旅游适宜、安全、幸福、消费等指标，
          便于解释每个目的地为什么值得选择。
        </p>
      </div>
      <div class="hero-actions">
        <el-button plain @click="goBack">重新生成推荐</el-button>
        <el-button plain @click="goVisualization">查看可视化</el-button>
        <el-button type="primary" @click="sortByScoreDesc">按得分排序</el-button>
        <el-button
          type="success"
          :icon="Download"
          :loading="exportLoading"
          @click="handleExport"
        >
          导出 Excel
        </el-button>
      </div>
    </section>

    <!-- 结果摘要卡片 -->
    <section class="summary-grid">
      <article class="summary-card">
        <span class="summary-label">推荐结果数</span>
        <strong>{{ tableData.length }}</strong>
      </article>
      <article class="summary-card">
        <span class="summary-label">最高得分</span>
        <strong>{{ maxScore }}</strong>
      </article>
      <article class="summary-card">
        <span class="summary-label">查询年份</span>
        <strong>{{ resultYear }}</strong>
      </article>
    </section>

    <!-- 结果展示表格 -->
    <section class="table-panel">
      <div class="panel-header">
        <div>
          <h3>推荐结果列表</h3>
          <p>表格默认按综合得分从高到低排序，点击旅游指数可查看更细的维度拆分。</p>
        </div>
      </div>

      <el-empty
        v-if="!tableData.length"
        description="暂无推荐结果数据，请先前往推荐输入页提交推荐请求"
      >
        <el-button type="primary" @click="goBack">前往推荐输入页</el-button>
      </el-empty>

      <el-table
        v-else
        :data="tableData"
        border
        stripe
        style="width: 100%"
        :default-sort="{ prop: 'score', order: 'descending' }"
      >
        <el-table-column prop="rank" label="排名" width="80" align="center" />
        <el-table-column prop="country_name" label="国家名称" min-width="140">
          <template #default="scope">
            <el-button link type="primary" @click="goCountryDetail(scope.row.country_id)">
              {{ scope.row.country_name }}
            </el-button>
          </template>
        </el-table-column>
        <el-table-column prop="score" label="综合得分" min-width="120" align="center" sortable />
        <el-table-column prop="tourism_index" label="旅游适宜指数" min-width="150" align="center" sortable>
          <template #default="scope">
            <el-popover placement="top" width="260" trigger="hover">
              <template #reference>
                <el-button link type="primary">{{ scope.row.tourism_index }}</el-button>
              </template>
              <div class="tourism-detail-popover">
                <p>旅游吸引力：{{ scope.row.tourism_detail.destination_attraction_score }}</p>
                <p>签证便利度：{{ scope.row.tourism_detail.visa_convenience_score }}</p>
                <p>基础设施代理分：{{ scope.row.tourism_detail.tourism_infrastructure_score }}</p>
                <p>旅游环境分：{{ scope.row.tourism_detail.travel_environment_score }}</p>
                <p>适宜等级：{{ scope.row.tourism_detail.tourism_level }}</p>
              </div>
            </el-popover>
          </template>
        </el-table-column>
        <el-table-column prop="safety_index" label="安全指数" min-width="110" align="center" sortable />
        <el-table-column prop="safety_requirement" label="安全需求" min-width="130" align="center" />
        <el-table-column prop="safety_matched_text" label="安全匹配" min-width="120" align="center" />
        <el-table-column prop="ppp_index" label="消费指数" min-width="110" align="center" sortable />
        <el-table-column prop="happiness_index" label="幸福指数" min-width="110" align="center" sortable />
        <el-table-column prop="estimated_cost" label="预计消费" min-width="120" align="center" />
        <el-table-column prop="continent" label="所属洲别" min-width="110" align="center" />
        <el-table-column prop="reason" label="推荐说明" min-width="240" show-overflow-tooltip />
      </el-table>
    </section>
  </div>
</template>

<script setup>
// 推荐结果展示页逻辑
import { computed, ref } from "vue";
import { useRouter } from "vue-router";
import { Download } from "@element-plus/icons-vue";

import { exportRecommendationExcelApi } from "@/api";
import { getLocalizedCountryName } from "@/utils/countryNameMap";
import { getStorage } from "@/utils/storage";

// 路由实例，用于页面跳转
const router = useRouter();

// 从本地缓存中读取推荐结果参数
const recommendationPayload = getStorage("recommendation_result_payload") || {};

// 查询年份
const resultYear = recommendationPayload.year || "--";

// 原始结果列表
const rawResults = recommendationPayload.results || [];

// 导出按钮状态
const exportLoading = ref(false);

// 统一格式化数值字段
function formatNumber(value) {
  const numericValue = Number(value);
  if (Number.isNaN(numericValue)) {
    return "--";
  }
  return numericValue.toFixed(2);
}

// 兼容旅游指数明细数据旧缓存或没有明细字段的情况
function normalizeTourismDetail(detail = {}) {
  return {
    destination_attraction_score: formatNumber(detail.destination_attraction_score),
    visa_convenience_score: formatNumber(detail.visa_convenience_score),
    tourism_infrastructure_score: formatNumber(detail.tourism_infrastructure_score),
    travel_environment_score: formatNumber(detail.travel_environment_score),
    tourism_level: detail.tourism_level || "--",
  };
}

// 表格数据，直接使用后端真实返回字段
const tableData = ref(
  rawResults.map((item, index) => ({
    country_id: item.country_id,
    rank: item.rank ?? index + 1,
    country_name: getLocalizedCountryName(item.country_name || item.country_name_en),
    country_name_en: item.country_name_en || "",
    score: formatNumber(item.score),
    tourism_index: formatNumber(item.tourism_index),
    tourism_detail: normalizeTourismDetail(item.tourism_detail),
    safety_index: formatNumber(item.safety_index),
    safety_requirement: item.safety_requirement || "--",
    safety_matched: item.safety_matched !== false,
    safety_matched_text: item.safety_matched === false ? "未完全满足" : "满足",
    ppp_index: formatNumber(item.ppp_index),
    cost_index: formatNumber(item.cost_index ?? item.ppp_index),
    happiness_index: formatNumber(item.happiness_index),
    estimated_cost: item.estimated_cost || "--",
    continent: item.continent || "--",
    reason: item.reason || "暂无推荐说明",
  })),
);

// 计算最高得分
const maxScore = computed(() => {
  if (!tableData.value.length) {
    return "--";
  }
  return Math.max(...tableData.value.map((item) => Number(item.score) || 0)).toFixed(2);
});

// 按综合得分降序排序
function sortByScoreDesc() {
  tableData.value.sort((a, b) => {
    return (Number(b.score) || 0) - (Number(a.score) || 0);
  });
}

function downloadBlob(blob, filename) {
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
}

async function handleExport() {
  if (!tableData.value.length) {
    ElMessage.warning("暂无可导出的推荐结果");
    return;
  }

  exportLoading.value = true;
  try {
    const exportYear = resultYear === "--" ? "" : resultYear;
    const blob = await exportRecommendationExcelApi({
      year: exportYear,
      results: tableData.value,
    });
    const filenameYear = exportYear || "当前";
    downloadBlob(blob, `安全旅游推荐结果_${filenameYear}.xlsx`);
    ElMessage.success("推荐结果 Excel 已导出");
  } catch (error) {
    ElMessage.error("导出失败，请稍后重试");
  } finally {
    exportLoading.value = false;
  }
}

// 返回推荐输入页
function goBack() {
  router.push("/app/recommendation");
}

// 跳转到可视化分析页
function goVisualization() {
  router.push("/app/visualization");
}

function goCountryDetail(countryId) {
  if (!countryId) {
    ElMessage.warning("当前推荐结果缺少国家 ID");
    return;
  }
  router.push(`/app/countries/${countryId}`);
}

// 页面初始化时默认按得分排序
sortByScoreDesc();
</script>

<style scoped>
.result-page {
  display: grid;
  gap: 18px;
}

.result-hero {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
  padding: 26px;
  border: 1px solid var(--color-line);
  border-radius: 8px;
  background:
    linear-gradient(135deg, rgba(40, 106, 115, 0.08), transparent 44%),
    #ffffff;
  color: var(--color-text);
  box-shadow: var(--shadow-panel);
}

.hero-tag {
  margin: 0 0 10px;
  color: var(--color-primary);
  text-transform: uppercase;
  letter-spacing: 0;
  font-size: 12px;
  font-weight: 900;
}

.result-hero h2 {
  margin: 0 0 10px;
  font-size: 30px;
}

.hero-desc {
  margin: 0;
  max-width: 760px;
  line-height: 1.7;
  color: var(--color-text-secondary);
}

.hero-actions {
  display: flex;
  gap: 12px;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.summary-card {
  padding: 22px;
  border: 1px solid rgba(16, 59, 70, 0.12);
  border-radius: 8px;
  background: var(--color-panel);
  box-shadow: var(--shadow-panel);
}

.summary-label {
  display: block;
  margin-bottom: 10px;
  color: #6f7b76;
  font-size: 14px;
}

.summary-card strong {
  color: var(--color-primary-dark);
  font-size: 28px;
}

.table-panel {
  padding: 24px;
  border: 1px solid rgba(16, 59, 70, 0.12);
  border-radius: 8px;
  background: var(--color-panel);
  box-shadow: var(--shadow-panel);
}

.panel-header {
  margin-bottom: 18px;
}

.panel-header h3 {
  margin: 0 0 8px;
  color: var(--color-primary-dark);
}

.panel-header p {
  margin: 0;
  color: #667570;
  line-height: 1.6;
}

.tourism-detail-popover p {
  margin: 6px 0;
  color: #465a54;
  line-height: 1.5;
}

@media (max-width: 900px) {
  .result-hero {
    flex-direction: column;
    align-items: flex-start;
  }

  .summary-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .hero-actions {
    flex-direction: column;
    width: 100%;
  }
}
</style>
