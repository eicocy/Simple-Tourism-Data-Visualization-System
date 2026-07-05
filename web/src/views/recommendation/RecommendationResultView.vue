<template>
  <div class="result-page">
    <!-- 页面头部说明 -->
    <section class="result-hero">
      <div>
        <p class="hero-tag">Result Center</p>
        <h2>旅游推荐结果展示</h2>
        <p class="hero-desc">
          本页以表格形式展示旅游国家推荐结果，支持按综合得分排序，
          同时展示旅游适宜指数、安全指数、幸福指数和消费指数，便于毕业设计演示。
        </p>
      </div>
      <div class="hero-actions">
        <el-button plain @click="goBack">返回重新推荐</el-button>
        <el-button plain @click="goVisualization">查看可视化</el-button>
        <el-button type="primary" @click="sortByScoreDesc">按得分排序</el-button>
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

    <!-- 表格展示区域 -->
    <section class="table-panel">
      <div class="panel-header">
        <div>
          <h3>推荐国家列表</h3>
          <p>表格默认按综合得分从高到低排列，旅游适宜指数已在结果中单独体现。</p>
        </div>
      </div>

      <el-empty
        v-if="!tableData.length"
        description="暂无推荐结果，请先前往推荐输入页提交推荐条件"
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
        <el-table-column prop="country_name" label="国家名称" min-width="140" />
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

import { getLocalizedCountryName } from "@/utils/countryNameMap";
import { getStorage } from "@/utils/storage";

// 路由实例，用于页面跳转
const router = useRouter();

// 从本地缓存中读取推荐结果数据
const recommendationPayload = getStorage("recommendation_result_payload") || {};

// 查询年份
const resultYear = recommendationPayload.year || "--";

// 原始结果列表
const rawResults = recommendationPayload.results || [];

// 统一格式化数值字段
function formatNumber(value) {
  const numericValue = Number(value);
  if (Number.isNaN(numericValue)) {
    return "--";
  }
  return numericValue.toFixed(2);
}

// 整理旅游适宜指数明细，兼容旧缓存中没有明细字段的情况
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
    rank: item.rank ?? index + 1,
    country_name: getLocalizedCountryName(item.country_name || item.country_name_en),
    score: formatNumber(item.score),
    tourism_index: formatNumber(item.tourism_index),
    tourism_detail: normalizeTourismDetail(item.tourism_detail),
    safety_index: formatNumber(item.safety_index),
    safety_requirement: item.safety_requirement || "--",
    safety_matched_text: item.safety_matched === false ? "未完全满足" : "满足",
    ppp_index: formatNumber(item.ppp_index),
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

// 返回推荐输入页
function goBack() {
  router.push("/app/recommendation");
}

// 跳转到可视化分析页
function goVisualization() {
  router.push("/app/visualization");
}

// 页面初始化时默认按得分排序
sortByScoreDesc();
</script>

<style scoped>
.result-page {
  display: grid;
  gap: 20px;
}

.result-hero {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
  padding: 28px;
  border-radius: 24px;
  background: linear-gradient(135deg, #21453d 0%, #3b7466 100%);
  color: #fffef9;
  box-shadow: 0 18px 42px rgba(20, 42, 37, 0.14);
}

.hero-tag {
  margin: 0 0 10px;
  color: rgba(255, 254, 249, 0.72);
  text-transform: uppercase;
  letter-spacing: 0.12em;
  font-size: 12px;
}

.result-hero h2 {
  margin: 0 0 10px;
  font-size: 30px;
}

.hero-desc {
  margin: 0;
  max-width: 760px;
  line-height: 1.7;
  color: rgba(255, 254, 249, 0.86);
}

.hero-actions {
  display: flex;
  gap: 12px;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 18px;
}

.summary-card {
  padding: 22px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.92);
  box-shadow: 0 12px 30px rgba(26, 43, 39, 0.08);
}

.summary-label {
  display: block;
  margin-bottom: 10px;
  color: #6f7b76;
  font-size: 14px;
}

.summary-card strong {
  color: #21443c;
  font-size: 28px;
}

.table-panel {
  padding: 24px;
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.94);
  box-shadow: 0 12px 32px rgba(24, 43, 38, 0.08);
}

.panel-header {
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
