<template>
  <div class="visualization-page">
    <!-- 页面头部说明区域 -->
    <section class="page-hero">
      <div>
        <p class="hero-tag">Visualization</p>
        <h2>推荐结果可视化分析</h2>
        <p class="hero-desc">
          本页面使用 ECharts 对推荐结果进行图形化展示，便于观察不同国家的综合得分与指标差异，
          当前图表已纳入旅游适宜指数，能够更直观地体现旅游目的地特征。
        </p>
      </div>
      <div class="hero-actions">
        <el-button plain @click="goRecommendation">返回推荐页</el-button>
        <el-button type="primary" @click="renderCharts">刷新图表</el-button>
      </div>
    </section>

    <!-- 数据摘要信息 -->
    <section class="summary-grid">
      <article class="summary-card">
        <span class="summary-label">结果数量</span>
        <strong>{{ chartData.length }}</strong>
      </article>
      <article class="summary-card">
        <span class="summary-label">最高综合得分</span>
        <strong>{{ maxScore }}</strong>
      </article>
      <article class="summary-card">
        <span class="summary-label">当前数据来源</span>
        <strong>{{ dataSourceText }}</strong>
      </article>
    </section>

    <!-- 图表区域 -->
    <section class="chart-grid">
      <article class="chart-card">
        <div class="card-header">
          <div>
            <h3>国家综合得分对比</h3>
            <p>柱状图展示各推荐国家的综合得分高低，便于快速比较推荐优先级。</p>
          </div>
        </div>
        <div ref="barChartRef" class="chart-box"></div>
      </article>

      <article class="chart-card">
        <div class="card-header">
          <div>
            <h3>国家指标雷达图</h3>
            <p>雷达图展示重点国家在旅游适宜、安全、幸福、消费与综合得分上的差异。</p>
          </div>
        </div>
        <div ref="radarChartRef" class="chart-box"></div>
      </article>
    </section>

    <!-- 表格辅助说明区域 -->
    <section class="table-card">
      <div class="card-header">
        <div>
          <h3>可视化数据明细</h3>
          <p>该表格用于配合图表展示，便于核对图形数据来源。</p>
        </div>
      </div>

      <el-empty
        v-if="!chartData.length"
        description="暂无推荐结果数据，请先完成推荐操作后再查看可视化页面"
      >
        <el-button type="primary" @click="goRecommendation">前往推荐页</el-button>
      </el-empty>

      <el-table
        v-else
        :data="chartData"
        border
        stripe
        style="width: 100%"
      >
        <el-table-column prop="country_name" label="国家名称" min-width="140" />
        <el-table-column prop="score" label="综合得分" min-width="100" align="center" />
        <el-table-column prop="tourism_index" label="旅游适宜指数" min-width="120" align="center" />
        <el-table-column prop="tourism_level" label="适宜等级" min-width="100" align="center" />
        <el-table-column prop="visa_convenience_score" label="签证便利度" min-width="110" align="center" />
        <el-table-column prop="destination_attraction_score" label="旅游吸引力" min-width="110" align="center" />
        <el-table-column prop="safety_index" label="安全指数" min-width="100" align="center" />
        <el-table-column prop="safety_requirement" label="安全需求" min-width="110" align="center" />
        <el-table-column prop="safety_matched_text" label="安全匹配" min-width="100" align="center" />
        <el-table-column prop="ppp_index" label="消费指数" min-width="100" align="center" />
        <el-table-column prop="happiness_index" label="幸福指数" min-width="100" align="center" />
        <el-table-column prop="estimated_cost" label="预计消费" min-width="100" align="center" />
      </el-table>
    </section>
  </div>
</template>

<script setup>
// 推荐结果可视化页面逻辑
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from "vue";
import { useRouter } from "vue-router";

import echarts from "@/plugins/echarts";
import { getLocalizedCountryName } from "@/utils/countryNameMap";
import { getStorage } from "@/utils/storage";

// 路由实例，用于页面跳转
const router = useRouter();

// 图表 DOM 引用
const barChartRef = ref(null);
const radarChartRef = ref(null);

// 图表实例引用，便于页面卸载时销毁
let barChartInstance = null;
let radarChartInstance = null;

// 从本地缓存中读取推荐结果
const recommendationPayload = getStorage("recommendation_result_payload") || {};
const rawResults = recommendationPayload.results || [];

// 统一格式化数值字段
function formatNumber(value) {
  const numericValue = Number(value);
  if (Number.isNaN(numericValue)) {
    return 0;
  }
  return Number(numericValue.toFixed(2));
}

// 将推荐结果转换成图表和表格统一使用的数据结构
const chartData = ref(
  rawResults.map((item) => ({
    tourism_detail: item.tourism_detail || {},
    country_name: getLocalizedCountryName(item.country_name || item.country_name_en),
    score: formatNumber(item.score),
    tourism_index: formatNumber(item.tourism_index),
    tourism_level: item.tourism_detail?.tourism_level || "--",
    visa_convenience_score: formatNumber(item.tourism_detail?.visa_convenience_score),
    destination_attraction_score: formatNumber(item.tourism_detail?.destination_attraction_score),
    safety_index: formatNumber(item.safety_index),
    safety_requirement: item.safety_requirement || "--",
    safety_matched_text: item.safety_matched === false ? "未满足" : "已满足",
    ppp_index: formatNumber(item.ppp_index),
    happiness_index: formatNumber(item.happiness_index),
    estimated_cost: item.estimated_cost || "--",
  })),
);

// 计算最高得分
const maxScore = computed(() => {
  if (!chartData.value.length) {
    return "--";
  }
  return Math.max(...chartData.value.map((item) => Number(item.score) || 0)).toFixed(2);
});

// 数据来源说明
const dataSourceText = computed(() => {
  return chartData.value.length ? "后端推荐接口真实数据" : "暂无可视化数据";
});

// 渲染柱状图
function renderBarChart() {
  if (!barChartRef.value || !chartData.value.length) {
    return;
  }

  if (barChartInstance) {
    barChartInstance.dispose();
  }

  barChartInstance = echarts.init(barChartRef.value);
  barChartInstance.setOption({
    tooltip: {
      trigger: "axis",
      axisPointer: {
        type: "shadow",
      },
    },
    grid: {
      left: "4%",
      right: "4%",
      bottom: "8%",
      containLabel: true,
    },
    xAxis: {
      type: "category",
      data: chartData.value.map((item) => item.country_name),
      axisLabel: {
        interval: 0,
        rotate: 18,
      },
    },
    yAxis: {
      type: "value",
      name: "综合得分",
      max: 100,
    },
    series: [
      {
        name: "综合得分",
        type: "bar",
        barWidth: 34,
        data: chartData.value.map((item) => item.score),
        itemStyle: {
          borderRadius: [8, 8, 0, 0],
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: "#2f6b5a" },
            { offset: 1, color: "#78a996" },
          ]),
        },
      },
    ],
  });
}

// 渲染雷达图
function renderRadarChart() {
  if (!radarChartRef.value || !chartData.value.length) {
    return;
  }

  if (radarChartInstance) {
    radarChartInstance.dispose();
  }

  const radarSource = [...chartData.value]
    .sort((a, b) => b.score - a.score)
    .slice(0, 3);

  radarChartInstance = echarts.init(radarChartRef.value);
  radarChartInstance.setOption({
    tooltip: {},
    legend: {
      bottom: 0,
      data: radarSource.map((item) => item.country_name),
    },
    radar: {
      radius: "58%",
      indicator: [
        { name: "综合得分", max: 100 },
        { name: "旅游适宜指数", max: 100 },
        { name: "安全指数", max: 100 },
        { name: "幸福指数", max: 100 },
        { name: "消费指数", max: 100 },
      ],
    },
    series: [
      {
        type: "radar",
        data: radarSource.map((item) => ({
          value: [
            item.score,
            item.tourism_index,
            item.safety_index,
            item.happiness_index,
            item.ppp_index,
          ],
          name: item.country_name,
        })),
        areaStyle: {
          opacity: 0.12,
        },
      },
    ],
  });
}

// 统一渲染图表
function renderCharts() {
  nextTick(() => {
    renderBarChart();
    renderRadarChart();
  });
}

// 返回推荐页
function goRecommendation() {
  router.push("/app/recommendation");
}

// 图表自适应函数
function handleResize() {
  barChartInstance?.resize();
  radarChartInstance?.resize();
}

// 页面挂载时渲染图表
onMounted(() => {
  renderCharts();
  window.addEventListener("resize", handleResize);
});

// 页面卸载前销毁图表实例和事件监听
onBeforeUnmount(() => {
  window.removeEventListener("resize", handleResize);

  if (barChartInstance) {
    barChartInstance.dispose();
    barChartInstance = null;
  }
  if (radarChartInstance) {
    radarChartInstance.dispose();
    radarChartInstance = null;
  }
});
</script>

<style scoped>
.visualization-page {
  display: grid;
  gap: 20px;
}

.page-hero {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
  padding: 28px;
  border-radius: 24px;
  background: linear-gradient(135deg, #1d3f52 0%, #2d6b7b 100%);
  color: #f7fbfc;
  box-shadow: 0 18px 42px rgba(22, 43, 53, 0.14);
}

.hero-tag {
  margin: 0 0 10px;
  color: rgba(247, 251, 252, 0.7);
  text-transform: uppercase;
  letter-spacing: 0.12em;
  font-size: 12px;
}

.page-hero h2 {
  margin: 0 0 10px;
  font-size: 30px;
}

.hero-desc {
  margin: 0;
  max-width: 760px;
  line-height: 1.7;
  color: rgba(247, 251, 252, 0.86);
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
  background: rgba(255, 255, 255, 0.94);
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

.chart-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 20px;
}

.chart-card,
.table-card {
  padding: 24px;
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.94);
  box-shadow: 0 12px 32px rgba(24, 43, 38, 0.08);
}

.card-header {
  margin-bottom: 18px;
}

.card-header h3 {
  margin: 0 0 8px;
  color: #28473f;
}

.card-header p {
  margin: 0;
  color: #667570;
  line-height: 1.6;
}

.chart-box {
  width: 100%;
  height: 380px;
}

@media (max-width: 980px) {
  .page-hero {
    flex-direction: column;
    align-items: flex-start;
  }

  .summary-grid,
  .chart-grid {
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
