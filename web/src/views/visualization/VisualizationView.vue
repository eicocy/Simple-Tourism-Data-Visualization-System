<template>
  <div class="visualization-page">
    <section class="page-hero">
      <div>
        <p class="hero-tag">Visualization Agent</p>
        <h2>智能问答地图与推荐结果可视化</h2>
        <p class="hero-desc">
          通过对话识别风险查询和风景偏好，自动改变世界地图国家标注，并给出目的地文字详情、
          不推荐理由或推荐说明。下方继续保留推荐结果图表分析。
        </p>
      </div>
      <div class="hero-actions">
        <el-button plain @click="goRecommendation">返回推荐页</el-button>
        <el-button type="primary" @click="refreshAllCharts">刷新可视化</el-button>
      </div>
    </section>

    <section class="summary-grid">
      <article class="summary-card">
        <span class="summary-label">结果数量</span>
        <strong>{{ chartData.length }}</strong>
      </article>
      <article class="summary-card">
        <span class="summary-label">地图覆盖国家</span>
        <strong>{{ worldMapData.length }}</strong>
      </article>
      <article class="summary-card">
        <span class="summary-label">当前数据来源</span>
        <strong>{{ dataSourceText }}</strong>
      </article>
    </section>

    <section class="agent-layout">
      <article class="map-card">
        <div class="card-header map-card-header">
          <div>
            <h3>智能地图标注</h3>
            <p>风险查询会标红国家，风景推荐会高亮候选目的地。</p>
          </div>
          <el-tag :type="agentTargets.length ? activeTagType : 'info'">
            {{ agentTargets.length ? `${agentTargets.length} 个标注` : "等待提问" }}
          </el-tag>
        </div>

        <el-empty
          v-if="!worldMapData.length && !mapLoading"
          description="暂无地图数据，请先导入国家指标数据"
        />
        <div v-show="worldMapData.length" ref="worldMapRef" class="world-map-box"></div>
      </article>

      <article class="agent-card">
        <div class="card-header">
          <div>
            <h3>地图问答助手</h3>
          </div>
        </div>

        <div class="quick-question-row">
          <el-button
            v-for="question in quickQuestions"
            :key="question"
            size="small"
            plain
            @click="sendAgentQuestion(question)"
          >
            {{ question }}
          </el-button>
        </div>

        <div class="chat-window">
          <div
            v-for="(message, index) in agentMessages"
            :key="index"
            class="chat-message"
            :class="message.role"
          >
            <span>{{ message.content }}</span>
          </div>
        </div>

        <div class="agent-input-row">
          <el-input
            v-model="agentInput"
            placeholder="输入你的地图问题"
            clearable
            @keyup.enter="sendAgentQuestion()"
          />
          <el-button type="primary" :loading="agentLoading" @click="sendAgentQuestion()">
            发送
          </el-button>
        </div>

        <div v-if="agentTargets.length" class="target-list">
          <div
            v-for="target in agentTargets"
            :key="`${target.country_id}-${target.category}`"
            class="target-item"
            :class="target.category"
          >
            <div class="target-title-row">
              <strong>{{ target.country_name }}</strong>
              <el-tag size="small" :type="target.category === 'risk' ? 'danger' : 'success'">
                {{ target.category === "risk" ? "风险标红" : "推荐高亮" }}
              </el-tag>
            </div>
            <p>{{ target.detail }}</p>
            <p class="target-reason">{{ target.reason }}</p>
          </div>
        </div>
      </article>
    </section>

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

    <section class="table-card">
      <div class="card-header">
        <div>
          <h3>可视化数据明细</h3>
          <p>该表格用于配合图表展示，便于核对图形数据来源。</p>
        </div>
      </div>

      <el-empty
        v-if="!chartData.length"
        description="暂无推荐结果数据，请先完成推荐操作后再查看推荐图表"
      >
        <el-button type="primary" @click="goRecommendation">前往推荐页</el-button>
      </el-empty>

      <el-table v-else :data="chartData" border stripe style="width: 100%">
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
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";

import { chatWithMapAgentApi, getCountryMapDataApi } from "@/api";
import echarts from "@/plugins/echarts";
import { getLocalizedCountryName } from "@/utils/countryNameMap";
import { getStorage } from "@/utils/storage";

const router = useRouter();

const barChartRef = ref(null);
const radarChartRef = ref(null);
const worldMapRef = ref(null);

let barChartInstance = null;
let radarChartInstance = null;
let worldMapInstance = null;

const recommendationPayload = getStorage("recommendation_result_payload") || {};
const rawResults = recommendationPayload.results || [];

const mapLoading = ref(false);
const worldMapData = ref([]);
const latestMapYear = ref("--");
const agentInput = ref("");
const agentLoading = ref(false);
const agentTargets = ref([]);
const activeAgentResult = ref(null);
const agentMessages = ref([
  {
    role: "assistant",
    content: "你可以问我“现在哪里有战事？”、“哪里有传染病流行？”或“我想去看欧洲的山”。",
  },
]);

const quickQuestions = ["现在哪里有战事？", "哪里有传染病流行？", "我想去看欧洲的山"];
const WORLD_MAP_SCRIPT_URLS = [
  "https://cdn.jsdelivr.net/npm/echarts-maps@1.1.0/world.js",
  "https://unpkg.com/echarts-maps@1.1.0/world.js",
];

function formatNumber(value) {
  const numericValue = Number(value);
  if (Number.isNaN(numericValue)) {
    return 0;
  }
  return Number(numericValue.toFixed(2));
}

function normalizeMapName(name) {
  const aliasMap = {
    USA: "United States of America",
    "United States": "United States of America",
    UAE: "United Arab Emirates",
    UK: "United Kingdom",
    "South Korea": "Korea",
    Vietnam: "Vietnam",
  };
  return aliasMap[name] || name;
}

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

const agentTargetMap = computed(() => {
  const targetMap = new Map();
  agentTargets.value.forEach((target) => {
    targetMap.set(normalizeMapName(target.country_name_en), target);
  });
  return targetMap;
});

const dataSourceText = computed(() => {
  if (activeAgentResult.value?.is_ai_generated) {
    return "国家指标 + 大模型润色";
  }
  if (worldMapData.value.length) {
    return `国家指标数据库（${latestMapYear.value || "--"}）`;
  }
  return "暂无可视化数据";
});

const activeTagType = computed(() => {
  return agentTargets.value.some((item) => item.category === "risk") ? "danger" : "success";
});

function loadScript(url) {
  return new Promise((resolve, reject) => {
    const existedScript = document.querySelector(`script[src="${url}"]`);
    if (existedScript) {
      resolve();
      return;
    }

    const script = document.createElement("script");
    script.src = url;
    script.async = true;
    script.onload = resolve;
    script.onerror = reject;
    document.head.appendChild(script);
  });
}

async function ensureWorldMapRegistered() {
  if (echarts.getMap("world")) {
    return;
  }

  window.echarts = echarts;
  let lastError = null;
  for (const url of WORLD_MAP_SCRIPT_URLS) {
    try {
      await loadScript(url);
      if (echarts.getMap("world")) {
        return;
      }
    } catch (error) {
      lastError = error;
    }
  }

  throw lastError || new Error("世界地图加载失败");
}

async function loadWorldMapData() {
  mapLoading.value = true;
  try {
    const result = await getCountryMapDataApi();
    const results = result?.data?.results || [];
    latestMapYear.value = result?.data?.year || "--";
    worldMapData.value = results
      .filter((item) => item.country_name_en)
      .map((item) => ({
        name: normalizeMapName(item.country_name_en),
        value: Number(item.recommendation_index ?? 0),
        country_id: item.country_id,
        country_name: item.country_name,
        country_name_en: item.country_name_en,
        tourism_index: Number(item.tourism_index ?? 0),
        tourism_detail: item.tourism_detail || {},
        safety_index: Number(item.safety_index ?? 0),
        ppp_index: Number(item.ppp_index ?? 0),
        happiness_index: Number(item.happiness_index ?? 0),
      }));
  } finally {
    mapLoading.value = false;
  }
}

function buildWorldMapSeriesData() {
  return worldMapData.value.map((item) => {
    const target = agentTargetMap.value.get(item.name);
    if (!target) {
      return item;
    }

    const isRisk = target.category === "risk";
    return {
      ...item,
      value: 100,
      agent_target: target,
      itemStyle: {
        areaColor: isRisk ? "#e60012" : "#ff8a00",
        borderColor: "#ffffff",
        borderWidth: 2.8,
        shadowBlur: 18,
        shadowColor: isRisk ? "rgba(230, 0, 18, 0.72)" : "rgba(255, 138, 0, 0.68)",
      },
      emphasis: {
        itemStyle: {
          areaColor: isRisk ? "#b40000" : "#d66b00",
          borderColor: "#ffffff",
          borderWidth: 3.2,
        },
      },
      label: {
        show: true,
        color: "#ffffff",
        fontWeight: 700,
        formatter: item.country_name,
      },
    };
  });
}

function buildWorldMapOption() {
  const hasAgentTargets = agentTargets.value.length > 0;
  const option = {
    backgroundColor: "transparent",
    tooltip: {
      trigger: "item",
      formatter: (params) => {
        const data = params.data || {};
        const target = data.agent_target;
        const lines = [
          data.country_name || params.name,
          `推荐指数：${params.value ?? "暂无数据"}`,
          `旅游适宜指数：${data.tourism_index ?? "--"}`,
          `安全指数：${data.safety_index ?? "--"}`,
          `PPP 指数：${data.ppp_index ?? "--"}`,
          `幸福指数：${data.happiness_index ?? "--"}`,
        ];
        if (target) {
          lines.push(`标注：${target.title}`);
          lines.push(target.detail);
          lines.push(target.reason);
        }
        return lines.join("<br/>");
      },
    },
    series: [
      {
        name: "推荐指数",
        type: "map",
        map: "world",
        roam: false,
        zoom: 1.12,
        emphasis: {
          label: {
            show: true,
            color: "#ffffff",
            formatter: (params) => params.data?.country_name || params.name,
          },
          itemStyle: {
            areaColor: "#d9af6b",
          },
        },
        itemStyle: {
          areaColor: hasAgentTargets ? "#dfe8e4" : "#edf5f1",
          borderColor: hasAgentTargets ? "rgba(106, 126, 120, 0.55)" : "rgba(78, 118, 103, 0.55)",
          borderWidth: 1,
        },
        data: buildWorldMapSeriesData(),
      },
    ],
  };

  if (!hasAgentTargets) {
    option.visualMap = {
      min: 0,
      max: 100,
      text: ["高", "低"],
      calculable: true,
      orient: "vertical",
      right: 22,
      bottom: 24,
      textStyle: {
        color: "#53635e",
      },
      inRange: {
        color: ["#eef4f1", "#cfe3d9", "#8dbda8", "#3e8267"],
      },
    };
  }

  return option;
}

async function renderWorldMap() {
  if (!worldMapRef.value || !worldMapData.value.length) {
    return;
  }

  await ensureWorldMapRegistered();

  if (worldMapInstance) {
    worldMapInstance.dispose();
  }

  worldMapInstance = echarts.init(worldMapRef.value);
  worldMapInstance.setOption(buildWorldMapOption());
}

async function sendAgentQuestion(question = agentInput.value) {
  const messageText = String(question || "").trim();
  if (!messageText || agentLoading.value) {
    return;
  }

  agentInput.value = "";
  agentMessages.value.push({ role: "user", content: messageText });
  agentLoading.value = true;

  try {
    const result = await chatWithMapAgentApi({ message: messageText });
    const data = result?.data || {};
    activeAgentResult.value = data;
    agentTargets.value = data.map_targets || [];
    agentMessages.value.push({
      role: "assistant",
      content: data.answer || "已完成地图标注。",
    });
    await nextTick();
    await renderWorldMap();
  } catch (error) {
    if (!error?.response) {
      ElMessage.error("智能地图助手暂时无法连接后端服务");
    }
  } finally {
    agentLoading.value = false;
  }
}

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

function renderRadarChart() {
  if (!radarChartRef.value || !chartData.value.length) {
    return;
  }

  if (radarChartInstance) {
    radarChartInstance.dispose();
  }

  const radarSource = [...chartData.value].sort((a, b) => b.score - a.score).slice(0, 3);

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

function renderCharts() {
  nextTick(() => {
    renderBarChart();
    renderRadarChart();
  });
}

async function refreshAllCharts() {
  await loadWorldMapData();
  await nextTick();
  await renderWorldMap();
  renderCharts();
}

function goRecommendation() {
  router.push("/app/recommendation");
}

function handleResize() {
  barChartInstance?.resize();
  radarChartInstance?.resize();
  worldMapInstance?.resize();
}

onMounted(async () => {
  renderCharts();
  try {
    await loadWorldMapData();
    await nextTick();
    await renderWorldMap();
  } catch (error) {
    ElMessage.error("世界地图加载失败，请检查地图接口或网络后刷新页面");
  }
  window.addEventListener("resize", handleResize);
});

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
  if (worldMapInstance) {
    worldMapInstance.dispose();
    worldMapInstance = null;
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
  max-width: 820px;
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
  font-size: 26px;
}

.agent-layout {
  display: grid;
  grid-template-columns: minmax(0, 1.35fr) minmax(360px, 0.65fr);
  gap: 20px;
}

.chart-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 20px;
}

.map-card,
.agent-card,
.chart-card,
.table-card {
  padding: 24px;
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.94);
  box-shadow: 0 12px 32px rgba(24, 43, 38, 0.08);
}

.map-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
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

.world-map-box {
  width: 100%;
  height: 520px;
  min-height: 420px;
}

.quick-question-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 14px;
}

.chat-window {
  display: grid;
  align-content: start;
  gap: 10px;
  height: 220px;
  overflow-y: auto;
  padding: 14px;
  border: 1px solid rgba(86, 115, 105, 0.16);
  border-radius: 14px;
  background: #f7faf8;
}

.chat-message {
  display: flex;
}

.chat-message span {
  max-width: 90%;
  padding: 10px 12px;
  border-radius: 12px;
  line-height: 1.6;
  font-size: 14px;
}

.chat-message.assistant span {
  color: #28473f;
  background: #ffffff;
  border: 1px solid rgba(76, 115, 101, 0.12);
}

.chat-message.user {
  justify-content: flex-end;
}

.chat-message.user span {
  color: #ffffff;
  background: #2f6b5a;
}

.agent-input-row {
  display: grid;
  grid-template-columns: 1fr 76px;
  gap: 10px;
  margin-top: 14px;
}

.target-list {
  display: grid;
  gap: 10px;
  max-height: 300px;
  overflow-y: auto;
  margin-top: 16px;
}

.target-item {
  padding: 12px;
  border-radius: 14px;
  border: 1px solid rgba(69, 120, 101, 0.18);
  background: #f9fbfa;
}

.target-item.risk {
  border-color: rgba(217, 77, 69, 0.28);
  background: #fff7f6;
}

.target-title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.target-title-row strong {
  color: #28473f;
}

.target-item p {
  margin: 0 0 8px;
  color: #5d6d67;
  line-height: 1.55;
  font-size: 13px;
}

.target-reason {
  color: #334d45;
}

.chart-box {
  width: 100%;
  height: 380px;
}

@media (max-width: 1180px) {
  .agent-layout,
  .chart-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 980px) {
  .page-hero {
    flex-direction: column;
    align-items: flex-start;
  }

  .summary-grid {
    grid-template-columns: 1fr;
  }

  .world-map-box {
    height: 460px;
  }
}

@media (max-width: 640px) {
  .hero-actions,
  .agent-input-row {
    grid-template-columns: 1fr;
    flex-direction: column;
    width: 100%;
  }

  .map-card-header,
  .target-title-row {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
