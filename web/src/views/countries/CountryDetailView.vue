<template>
  <div class="detail-page" v-loading="loading">
    <!-- 国家基础信息头部 -->
    <section class="page-hero">
      <div>
        <p class="hero-tag">{{ country.continent || "Country Detail" }}</p>
        <h2>{{ displayName }}</h2>
        <p class="hero-desc">
          英文名称：{{ country.name_en || "--" }} · 国家代码：{{ country.code || "--" }}
        </p>
      </div>

      <div class="hero-actions">
        <el-button plain @click="router.back()">返回</el-button>
        <el-button type="primary" @click="router.push('/app/countries')">
          国家指标分析
        </el-button>
      </div>
    </section>

    <!-- 核心指标卡片 -->
    <section class="summary-grid">
      <article class="summary-card">
        <span>推荐指数</span>
        <strong>{{ formatNumber(indicator.recommendation_index) }}</strong>
      </article>
      <article class="summary-card">
        <span>旅游适宜指数</span>
        <strong>{{ formatNumber(indicator.tourism_index) }}</strong>
      </article>
      <article class="summary-card">
        <span>安全指数</span>
        <strong>{{ formatNumber(indicator.safety_index) }}</strong>
      </article>
      <article class="summary-card">
        <span>幸福指数</span>
        <strong>{{ formatNumber(indicator.happiness_index) }}</strong>
      </article>
    </section>

    <!-- 指标图表区域 -->
    <section class="content-grid">
      <article class="panel">
        <div class="panel-header">
          <h3>核心指标雷达图</h3>
          <p>雷达图展示该国家在推荐、旅游适宜、安全、幸福和消费友好度上的综合表现。</p>
        </div>
        <div ref="radarChartRef" class="chart-box"></div>
      </article>

      <article class="panel">
        <div class="panel-header">
          <h3>旅游适宜指数拆分</h3>
          <p>该图展示旅游适宜指数内部四个维度，有助于解释为什么该国家适合或不适合推荐。</p>
        </div>
        <div ref="tourismChartRef" class="chart-box"></div>
      </article>
    </section>

    <!-- 指标明细说明 -->
    <section class="panel">
      <div class="panel-header">
        <h3>指标明细</h3>
        <p>最新数据年份：{{ indicator.year || "--" }}，数据来源：{{ indicator.data_source || "系统导入数据" }}</p>
      </div>

      <el-descriptions border :column="2">
        <el-descriptions-item label="所属洲别">{{ country.continent || "--" }}</el-descriptions-item>
        <el-descriptions-item label="首都">{{ country.capital || "--" }}</el-descriptions-item>
        <el-descriptions-item label="语言">{{ country.language || "--" }}</el-descriptions-item>
        <el-descriptions-item label="货币">{{ country.currency || "--" }}</el-descriptions-item>
        <el-descriptions-item label="消费指数">{{ formatNumber(indicator.cost_index) }}</el-descriptions-item>
        <el-descriptions-item label="PPP 指数">{{ formatNumber(indicator.ppp_index) }}</el-descriptions-item>
        <el-descriptions-item label="签证便利度">{{ formatNumber(indicator.visa_index) }}</el-descriptions-item>
        <el-descriptions-item label="适宜等级">{{ tourismDetail.tourism_level || "--" }}</el-descriptions-item>
        <el-descriptions-item label="旅游吸引力">
          {{ formatNumber(tourismDetail.destination_attraction_score) }}
        </el-descriptions-item>
        <el-descriptions-item label="基础设施代理分">
          {{ formatNumber(tourismDetail.tourism_infrastructure_score) }}
        </el-descriptions-item>
        <el-descriptions-item label="旅游环境分">
          {{ formatNumber(tourismDetail.travel_environment_score) }}
        </el-descriptions-item>
        <el-descriptions-item label="签证便利代理分">
          {{ formatNumber(tourismDetail.visa_convenience_score) }}
        </el-descriptions-item>
      </el-descriptions>
    </section>
  </div>
</template>

<script setup>
// 国家详情分析页面：展示单个国家的基础资料、最新指标和算法拆分结果
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage } from "element-plus";

import { getCountryInsightDetailApi } from "@/api";
import echarts from "@/plugins/echarts";
import { getLocalizedCountryName } from "@/utils/countryNameMap";

const route = useRoute();
const router = useRouter();

const loading = ref(false);
const country = ref({});
const indicator = ref({});
const tourismDetail = ref({});
const radarChartRef = ref(null);
const tourismChartRef = ref(null);

let radarChart = null;
let tourismChart = null;

// 国家显示名优先使用中文，缺失时再使用英文名称映射
const displayName = computed(() => {
  return getLocalizedCountryName(country.value.name_zh || country.value.name_en);
});

// 消费友好度用于雷达图，消费指数越低代表成本越友好
const costFriendliness = computed(() => {
  const costIndex = Number(indicator.value.cost_index);
  if (Number.isNaN(costIndex)) {
    return 0;
  }
  return Math.max(0, Math.min(100, 100 - costIndex));
});

// 统一格式化数值
function formatNumber(value) {
  const numericValue = Number(value);
  return Number.isNaN(numericValue) ? "--" : numericValue.toFixed(2);
}

// 图表使用数值，空值时返回 0
function chartNumber(value) {
  const numericValue = Number(value);
  return Number.isNaN(numericValue) ? 0 : Number(numericValue.toFixed(2));
}

// 加载国家详情数据
async function loadDetail() {
  loading.value = true;
  try {
    const result = await getCountryInsightDetailApi(route.params.id);
    country.value = result.data?.country || {};
    indicator.value = result.data?.latest_indicator || {};
    tourismDetail.value = indicator.value.tourism_detail || {};
    renderCharts();
  } catch (error) {
    ElMessage.error("国家详情加载失败，请检查该国家是否存在指标数据");
  } finally {
    loading.value = false;
  }
}

// 渲染页面图表
function renderCharts() {
  nextTick(() => {
    renderRadarChart();
    renderTourismChart();
  });
}

// 渲染核心指标雷达图
function renderRadarChart() {
  if (!radarChartRef.value || !indicator.value.country_id) {
    return;
  }

  radarChart?.dispose();
  radarChart = echarts.init(radarChartRef.value);
  radarChart.setOption({
    tooltip: {},
    radar: {
      radius: "62%",
      indicator: [
        { name: "推荐指数", max: 100 },
        { name: "旅游适宜", max: 100 },
        { name: "安全", max: 100 },
        { name: "幸福", max: 100 },
        { name: "消费友好", max: 100 },
      ],
    },
    series: [
      {
        name: "核心指标",
        type: "radar",
        data: [
          {
            name: displayName.value,
            value: [
              chartNumber(indicator.value.recommendation_index),
              chartNumber(indicator.value.tourism_index),
              chartNumber(indicator.value.safety_index),
              chartNumber(indicator.value.happiness_index),
              chartNumber(costFriendliness.value),
            ],
          },
        ],
        areaStyle: {
          color: "rgba(47, 114, 200, 0.18)",
        },
        lineStyle: {
          color: "#1e5fbf",
        },
        itemStyle: {
          color: "#1e5fbf",
        },
      },
    ],
  });
}

// 渲染旅游适宜指数拆分柱状图
function renderTourismChart() {
  if (!tourismChartRef.value || !tourismDetail.value.tourism_index) {
    return;
  }

  tourismChart?.dispose();
  tourismChart = echarts.init(tourismChartRef.value);
  tourismChart.setOption({
    tooltip: { trigger: "axis" },
    grid: { left: "4%", right: "4%", bottom: "8%", containLabel: true },
    xAxis: {
      type: "category",
      data: ["旅游吸引力", "签证便利度", "基础设施", "旅游环境"],
      axisLabel: { color: "#4d6074" },
    },
    yAxis: {
      type: "value",
      max: 100,
      axisLabel: { color: "#4d6074" },
    },
    series: [
      {
        name: "维度得分",
        type: "bar",
        barWidth: 34,
        data: [
          chartNumber(tourismDetail.value.destination_attraction_score),
          chartNumber(tourismDetail.value.visa_convenience_score),
          chartNumber(tourismDetail.value.tourism_infrastructure_score),
          chartNumber(tourismDetail.value.travel_environment_score),
        ],
        itemStyle: {
          borderRadius: [8, 8, 0, 0],
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: "#1e5fbf" },
            { offset: 1, color: "#9fcbff" },
          ]),
        },
      },
    ],
  });
}

// 页面尺寸变化时重绘图表
function handleResize() {
  radarChart?.resize();
  tourismChart?.resize();
}

onMounted(() => {
  loadDetail();
  window.addEventListener("resize", handleResize);
});

onBeforeUnmount(() => {
  window.removeEventListener("resize", handleResize);
  radarChart?.dispose();
  tourismChart?.dispose();
});
</script>

<style scoped>
.detail-page {
  display: grid;
  gap: 20px;
}

.page-hero,
.summary-card,
.panel {
  padding: 20px;
  border: 1px solid #dfe7ef;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.94);
  box-shadow: 0 14px 34px rgba(36, 74, 118, 0.07);
}

.page-hero {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
}

.hero-tag {
  margin: 0 0 8px;
  color: #2f72c8;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  font-size: 12px;
}

.page-hero h2 {
  margin: 0 0 8px;
  color: #1f3347;
  font-size: 28px;
}

.hero-desc,
.panel-header p {
  margin: 0;
  color: #647587;
  line-height: 1.7;
}

.hero-actions {
  display: flex;
  gap: 12px;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
}

.summary-card span {
  display: block;
  margin-bottom: 8px;
  color: #647587;
}

.summary-card strong {
  color: #1f3347;
  font-size: 28px;
}

.content-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 20px;
}

.panel-header {
  margin-bottom: 16px;
}

.panel-header h3 {
  margin: 0 0 8px;
  color: #1f3347;
  font-size: 20px;
}

.chart-box {
  height: 340px;
}

@media (max-width: 980px) {
  .page-hero {
    flex-direction: column;
    align-items: flex-start;
  }

  .summary-grid,
  .content-grid {
    grid-template-columns: 1fr;
  }
}
</style>
