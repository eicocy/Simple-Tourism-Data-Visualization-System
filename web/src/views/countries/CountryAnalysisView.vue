<template>
  <div class="analysis-page">
    <!-- 页面头部：说明当前页面用于国家指标总览分析 -->
    <section class="page-hero">
      <div>
        <p class="hero-tag">Country Analytics</p>
        <h2>国家指标分析</h2>
        <p class="hero-desc">
          本页面按洲别汇总国家推荐表现，并展示国家最新指标明细，适合毕业设计答辩时说明数据分析过程。
        </p>
      </div>

      <div class="hero-actions">
        <el-select
          v-model="selectedContinent"
          clearable
          placeholder="筛选洲别"
          style="width: 180px"
        >
          <el-option
            v-for="item in continentOptions"
            :key="item"
            :label="item"
            :value="item"
          />
        </el-select>
        <el-button type="primary" :loading="loading" @click="loadAllData">
          刷新数据
        </el-button>
      </div>
    </section>

    <!-- 顶部统计卡片 -->
    <section class="summary-grid">
      <article class="summary-card">
        <span>国家总数</span>
        <strong>{{ filteredCountries.length }}</strong>
      </article>
      <article class="summary-card">
        <span>最高推荐指数</span>
        <strong>{{ maxRecommendationIndex }}</strong>
      </article>
      <article class="summary-card">
        <span>最高洲别</span>
        <strong>{{ topContinent }}</strong>
      </article>
      <article class="summary-card">
        <span>统计年份</span>
        <strong>{{ latestYear }}</strong>
      </article>
    </section>

    <!-- 按洲别统计图表 -->
    <section class="chart-grid">
      <article class="panel">
        <div class="panel-header">
          <h3>各洲平均推荐指数</h3>
          <p>柱状图用于比较不同洲别在综合推荐模型中的平均表现。</p>
        </div>
        <div ref="continentChartRef" class="chart-box"></div>
      </article>

      <article class="panel">
        <div class="panel-header">
          <h3>各洲国家数量占比</h3>
          <p>环形图展示当前数据库中各洲国家样本数量，便于说明数据覆盖情况。</p>
        </div>
        <div ref="countChartRef" class="chart-box"></div>
      </article>
    </section>

    <!-- 国家指标明细表 -->
    <section class="panel">
      <div class="panel-header table-header">
        <div>
          <h3>国家指标明细</h3>
          <p>点击“查看详情”可进入单个国家的指标拆分页面。</p>
        </div>
        <el-input
          v-model="searchKeyword"
          placeholder="搜索国家名称"
          clearable
          style="width: 260px"
        />
      </div>

      <el-table
        :data="filteredCountries"
        border
        stripe
        v-loading="loading"
        style="width: 100%"
      >
        <el-table-column prop="country_name" label="国家名称" min-width="140" />
        <el-table-column prop="continent" label="所属洲别" min-width="110" align="center" />
        <el-table-column
          prop="recommendation_index"
          label="推荐指数"
          min-width="110"
          align="center"
          sortable
        />
        <el-table-column
          prop="tourism_index"
          label="旅游适宜指数"
          min-width="130"
          align="center"
          sortable
        />
        <el-table-column
          prop="safety_index"
          label="安全指数"
          min-width="100"
          align="center"
          sortable
        />
        <el-table-column
          prop="happiness_index"
          label="幸福指数"
          min-width="100"
          align="center"
          sortable
        />
        <el-table-column
          prop="cost_index"
          label="消费指数"
          min-width="100"
          align="center"
          sortable
        />
        <el-table-column label="操作" width="120" align="center">
          <template #default="scope">
            <el-button link type="primary" @click="goDetail(scope.row.country_id)">
              查看详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </section>
  </div>
</template>

<script setup>
// 国家指标分析页面：从后端读取最新地图数据与洲别统计数据
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";

import { getCountryContinentStatsApi, getCountryMapDataApi } from "@/api";
import echarts from "@/plugins/echarts";
import { getLocalizedCountryName } from "@/utils/countryNameMap";

const router = useRouter();

// 页面状态
const loading = ref(false);
const latestYear = ref("--");
const selectedContinent = ref("");
const searchKeyword = ref("");
const continentStats = ref([]);
const countryRows = ref([]);

// 图表容器引用
const continentChartRef = ref(null);
const countChartRef = ref(null);

// ECharts 实例，卸载页面时需要销毁，避免内存占用
let continentChart = null;
let countChart = null;

// 洲别下拉选项
const continentOptions = computed(() => {
  return continentStats.value
    .map((item) => item.continent)
    .filter(Boolean);
});

// 根据洲别和关键词筛选国家表格
const filteredCountries = computed(() => {
  const keyword = searchKeyword.value.trim().toLowerCase();
  return countryRows.value.filter((item) => {
    const matchedContinent = !selectedContinent.value || item.continent === selectedContinent.value;
    const matchedKeyword =
      !keyword ||
      item.country_name.toLowerCase().includes(keyword) ||
      (item.country_name_en || "").toLowerCase().includes(keyword);
    return matchedContinent && matchedKeyword;
  });
});

// 当前筛选结果中的最高推荐指数
const maxRecommendationIndex = computed(() => {
  if (!filteredCountries.value.length) {
    return "--";
  }
  return Math.max(...filteredCountries.value.map((item) => item.recommendation_index)).toFixed(2);
});

// 推荐指数最高的洲别
const topContinent = computed(() => {
  if (!continentStats.value.length) {
    return "--";
  }
  return continentStats.value[0].continent || "--";
});

// 统一格式化数值，避免接口空值影响图表
function formatNumber(value) {
  const numericValue = Number(value);
  return Number.isNaN(numericValue) ? 0 : Number(numericValue.toFixed(2));
}

// 加载后端真实数据
async function loadAllData() {
  loading.value = true;
  try {
    const [statsResult, mapResult] = await Promise.all([
      getCountryContinentStatsApi(),
      getCountryMapDataApi(),
    ]);

    latestYear.value = statsResult?.data?.year || mapResult?.data?.year || "--";
    continentStats.value = (statsResult?.data?.results || []).map((item) => ({
      ...item,
      avg_recommendation_index: formatNumber(item.avg_recommendation_index),
      avg_tourism_index: formatNumber(item.avg_tourism_index),
      avg_safety_index: formatNumber(item.avg_safety_index),
      avg_cost_index: formatNumber(item.avg_cost_index),
      avg_happiness_index: formatNumber(item.avg_happiness_index),
    }));

    countryRows.value = (mapResult?.data?.results || []).map((item) => ({
      ...item,
      country_name: getLocalizedCountryName(item.country_name || item.country_name_en),
      country_name_en: item.country_name_en || "",
      continent: item.continent || "未分类",
      recommendation_index: formatNumber(item.recommendation_index),
      tourism_index: formatNumber(item.tourism_index),
      safety_index: formatNumber(item.safety_index),
      happiness_index: formatNumber(item.happiness_index),
      cost_index: formatNumber(item.cost_index),
    }));

    renderCharts();
  } catch (error) {
    ElMessage.error("国家指标数据加载失败，请检查后端服务是否正常");
  } finally {
    loading.value = false;
  }
}

// 渲染全部图表
function renderCharts() {
  nextTick(() => {
    renderContinentChart();
    renderCountChart();
  });
}

// 渲染各洲平均推荐指数柱状图
function renderContinentChart() {
  if (!continentChartRef.value || !continentStats.value.length) {
    return;
  }

  continentChart?.dispose();
  continentChart = echarts.init(continentChartRef.value);
  continentChart.setOption({
    tooltip: { trigger: "axis" },
    legend: { top: 0 },
    grid: { left: "4%", right: "4%", bottom: "8%", containLabel: true },
    xAxis: {
      type: "category",
      data: continentStats.value.map((item) => item.continent),
      axisLabel: { color: "#4d6074" },
    },
    yAxis: {
      type: "value",
      max: 100,
      axisLabel: { color: "#4d6074" },
    },
    series: [
      {
        name: "平均推荐指数",
        type: "bar",
        barWidth: 34,
        data: continentStats.value.map((item) => item.avg_recommendation_index),
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

// 渲染各洲国家数量环形图
function renderCountChart() {
  if (!countChartRef.value || !continentStats.value.length) {
    return;
  }

  countChart?.dispose();
  countChart = echarts.init(countChartRef.value);
  countChart.setOption({
    tooltip: { trigger: "item" },
    legend: {
      bottom: 0,
      textStyle: { color: "#4d6074" },
    },
    series: [
      {
        name: "国家数量",
        type: "pie",
        radius: ["42%", "68%"],
        center: ["50%", "45%"],
        data: continentStats.value.map((item) => ({
          name: item.continent,
          value: item.country_count,
        })),
        itemStyle: {
          borderColor: "#ffffff",
          borderWidth: 2,
        },
      },
    ],
  });
}

// 跳转到国家详情页
function goDetail(countryId) {
  router.push(`/app/countries/${countryId}`);
}

// 浏览器窗口变化时重绘图表
function handleResize() {
  continentChart?.resize();
  countChart?.resize();
}

onMounted(() => {
  loadAllData();
  window.addEventListener("resize", handleResize);
});

onBeforeUnmount(() => {
  window.removeEventListener("resize", handleResize);
  continentChart?.dispose();
  countChart?.dispose();
});
</script>

<style scoped>
.analysis-page {
  display: grid;
  gap: 20px;
}

.page-hero {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
  padding: 24px;
  border: 1px solid #dfe7ef;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.92);
  box-shadow: 0 14px 34px rgba(36, 74, 118, 0.08);
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
  align-items: center;
  gap: 12px;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
}

.chart-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.summary-card,
.panel {
  padding: 20px;
  border: 1px solid #dfe7ef;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.94);
  box-shadow: 0 14px 34px rgba(36, 74, 118, 0.07);
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

.panel-header {
  margin-bottom: 16px;
}

.panel-header h3 {
  margin: 0 0 8px;
  color: #1f3347;
  font-size: 20px;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
}

.chart-box {
  height: 340px;
}

@media (max-width: 980px) {
  .page-hero,
  .table-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .summary-grid,
  .chart-grid {
    grid-template-columns: 1fr;
  }
}
</style>
