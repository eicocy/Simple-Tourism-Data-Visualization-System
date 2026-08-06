<template>
  <main class="travel-analytics-page">
    <header class="topbar">
      <div class="brand">
        <span class="brand-mark">旅</span>
        <div>
          <p>Graduation project UI preview</p>
          <h1>安全旅游分析可视化系统</h1>
        </div>
      </div>

      <div class="topbar-actions">
        <button class="ghost-button" type="button" @click="goHome">返回首页</button>
        <button class="primary-button" type="button" @click="goRecommendation">进入推荐流程</button>
      </div>
    </header>

    <section class="hero-panel">
      <div class="hero-copy">
        <span class="section-label">最终选型稿</span>
        <h2>用一张地图看懂目的地安全、成本与旅游适宜度</h2>
        <p>
          面向旅行前决策，把国家指标、风险提醒、推荐排序和模型解释放在同一屏。
          用户不只是看到“推荐哪个国家”，也能看懂为什么推荐、哪里需要谨慎。
        </p>
      </div>

      <dl class="hero-metrics">
        <div v-for="metric in heroMetrics" :key="metric.label">
          <dt>{{ metric.label }}</dt>
          <dd>{{ metric.value }}</dd>
          <small>{{ metric.note }}</small>
        </div>
      </dl>
    </section>

    <section class="workspace">
      <aside class="side-nav">
        <div class="side-title">
          <strong>安全旅游</strong>
          <span>分析可视化</span>
        </div>
        <button
          v-for="item in navigationItems"
          :key="item"
          class="nav-button"
          :class="{ active: item === '综合分析' }"
          type="button"
        >
          {{ item }}
        </button>
      </aside>

      <div class="dashboard">
        <section class="analysis-header">
          <div>
            <p><span class="live-dot"></span>国家指标已同步 · 推荐模型已就绪</p>
            <h3>本次分析：亚洲优先，中等预算，高安全需求</h3>
          </div>
          <div class="readiness-score">
            <span>出行适配度</span>
            <strong>92</strong>
            <small>建议优先考虑</small>
          </div>
        </section>

        <section class="summary-row">
          <article v-for="card in summaryCards" :key="card.label" class="summary-card">
            <span>{{ card.label }}</span>
            <strong>{{ card.value }}</strong>
            <small>{{ card.note }}</small>
          </article>
        </section>

        <section class="main-grid">
          <article class="preference-panel">
            <div class="panel-heading">
              <h4>推荐条件</h4>
              <span>当前输入</span>
            </div>
            <div v-for="item in preferences" :key="item.label" class="preference-item">
              <span>{{ item.label }}</span>
              <strong>{{ item.value }}</strong>
              <small>{{ item.note }}</small>
            </div>
            <button class="primary-button full" type="button">重新计算推荐</button>
          </article>

          <article class="map-panel">
            <div class="map-header">
              <div>
                <span>Travel safety visualization</span>
                <h4>全球旅游安全分析图</h4>
              </div>
              <div class="legend">
                <span><i class="safe"></i>适合</span>
                <span><i class="watch"></i>观察</span>
                <span><i class="avoid"></i>避让</span>
              </div>
            </div>

            <div class="map-canvas" aria-label="全球旅游安全分析地图演示">
              <div class="continent continent-america"></div>
              <div class="continent continent-europe"></div>
              <div class="continent continent-africa"></div>
              <div class="continent continent-asia"></div>
              <div class="continent continent-oceania"></div>
              <div class="latitude-line line-one"></div>
              <div class="latitude-line line-two"></div>
              <span
                v-for="point in mapPoints"
                :key="point.code"
                class="map-marker"
                :class="point.level"
                :style="{ left: point.x, top: point.y }"
              >
                <b>{{ point.code }}</b>
                <small>{{ point.name }}</small>
              </span>
            </div>
          </article>

          <article class="ranking-panel">
            <div class="panel-heading">
              <h4>推荐结果</h4>
              <span>TOP 3</span>
            </div>
            <div v-for="item in destinations" :key="item.country" class="ranking-item">
              <span class="rank">{{ item.rank }}</span>
              <div>
                <strong>{{ item.country }}</strong>
                <p>{{ item.reason }}</p>
                <small>{{ item.caution }}</small>
              </div>
              <b>{{ item.score }}</b>
            </div>
          </article>
        </section>

        <section class="bottom-grid">
          <article class="risk-panel">
            <div class="panel-heading">
              <h4>风险监测</h4>
              <span>影响推荐排序</span>
            </div>
            <div v-for="risk in riskSignals" :key="risk.name" class="risk-item">
              <i :class="risk.level"></i>
              <div>
                <strong>{{ risk.name }}</strong>
                <small>{{ risk.detail }}</small>
              </div>
              <span>{{ risk.action }}</span>
            </div>
          </article>

          <article class="model-panel">
            <div class="panel-heading">
              <h4>模型权重</h4>
              <span>固定算法</span>
            </div>
            <label v-for="row in weightRows" :key="row.name" class="weight-row">
              <span>{{ row.name }}</span>
              <strong>{{ row.value }}%</strong>
              <i :style="{ width: `${row.value * 2}%` }"></i>
            </label>
          </article>
        </section>
      </div>
    </section>
  </main>
</template>

<script setup>
import { useRouter } from "vue-router";

const router = useRouter();

const navigationItems = ["综合分析", "国家地图", "推荐结果", "风险监测", "算法说明"];

const heroMetrics = [
  { label: "覆盖国家", value: "126", note: "用于地图与排序分析" },
  { label: "推荐维度", value: "4", note: "旅游、安全、幸福、消费" },
  { label: "风险规则", value: "18", note: "影响避让与降权" },
];

const summaryCards = [
  { label: "最高推荐指数", value: "94.2", note: "日本" },
  { label: "安全阈值", value: "80+", note: "低于阈值进入观察" },
  { label: "预算匹配度", value: "76%", note: "中等预算友好" },
  { label: "解释覆盖率", value: "100%", note: "每个推荐都有理由" },
];

const preferences = [
  { label: "预算等级", value: "中等预算", note: "兼顾住宿、交通与当地消费" },
  { label: "偏好洲别", value: "亚洲优先", note: "优先考虑短航程与签证便利" },
  { label: "安全需求", value: "高安全", note: "自动过滤高风险目的地" },
  { label: "旅行画像", value: "首次出境家庭", note: "更重视医疗、交通和城市治安" },
];

const mapPoints = [
  { code: "JP", name: "日本", level: "safe", x: "74%", y: "38%" },
  { code: "SG", name: "新加坡", level: "safe", x: "66%", y: "63%" },
  { code: "TH", name: "泰国", level: "watch", x: "61%", y: "56%" },
  { code: "FR", name: "法国", level: "safe", x: "44%", y: "36%" },
  { code: "UA", name: "避让", level: "avoid", x: "51%", y: "32%" },
];

const destinations = [
  {
    rank: "01",
    country: "日本",
    reason: "安全指数高，公共交通成熟，旅游适宜指数稳定。",
    caution: "旺季住宿成本偏高，建议提前规划城市间交通。",
    score: 94,
  },
  {
    rank: "02",
    country: "新加坡",
    reason: "城市治安和医疗保障强，适合短途高确定性旅行。",
    caution: "消费指数偏高，预算模型已做轻度降权。",
    score: 91,
  },
  {
    rank: "03",
    country: "泰国",
    reason: "预算友好，目的地吸引力突出，签证便利度较好。",
    caution: "部分地区进入观察，建议避开临时预警区域。",
    score: 86,
  },
];

const riskSignals = [
  { name: "区域冲突", detail: "命中国家不进入推荐池，地图保留红色标注。", level: "danger", action: "排除" },
  { name: "公共卫生", detail: "有传播风险时保留目的地，但提示保险和疫苗。", level: "warning", action: "提示" },
  { name: "预算波动", detail: "住宿和汇率超过阈值时降低消费友好度。", level: "normal", action: "降权" },
];

const weightRows = [
  { name: "旅游适宜指数", value: 40 },
  { name: "安全指数", value: 30 },
  { name: "幸福指数", value: 15 },
  { name: "消费友好度", value: 15 },
];

function goHome() {
  router.push("/");
}

function goRecommendation() {
  router.push("/app/recommendation");
}
</script>

<style scoped>
.travel-analytics-page {
  min-height: 100vh;
  padding: 24px;
  background:
    linear-gradient(135deg, rgba(20, 92, 103, 0.14), transparent 34%),
    linear-gradient(180deg, #eef4f2 0%, #dce8e5 100%);
  color: #142724;
}

.topbar,
.hero-panel,
.workspace {
  width: min(1440px, 100%);
  margin: 0 auto;
}

.topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 18px;
  margin-bottom: 18px;
}

.brand {
  display: flex;
  align-items: center;
  gap: 14px;
}

.brand-mark {
  display: grid;
  width: 52px;
  height: 52px;
  place-items: center;
  border-radius: 8px;
  background: #103b46;
  color: #f3bd55;
  font-size: 24px;
  font-weight: 900;
}

.brand p,
.section-label,
.map-header span {
  margin: 0 0 6px;
  color: #60716d;
  font-size: 12px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0;
}

.brand h1 {
  margin: 0;
  color: #102521;
  font-size: 30px;
  line-height: 1.2;
}

.topbar-actions {
  display: flex;
  gap: 10px;
}

.ghost-button,
.primary-button {
  min-height: 40px;
  padding: 0 16px;
  border-radius: 8px;
  font-weight: 800;
  cursor: pointer;
}

.ghost-button {
  border: 1px solid #b9c9c5;
  background: #f8fbfa;
  color: #18322d;
}

.primary-button {
  border: 1px solid #103b46;
  background: #103b46;
  color: #ffffff;
}

.primary-button.full {
  width: 100%;
  margin-top: 16px;
}

.hero-panel {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 520px;
  gap: 18px;
  margin-bottom: 18px;
  padding: 22px;
  border: 1px solid rgba(16, 59, 70, 0.14);
  border-radius: 8px;
  background: #fbfdfb;
}

.hero-copy h2 {
  max-width: 820px;
  margin: 0;
  color: #0f2f36;
  font-size: 38px;
  line-height: 1.16;
}

.hero-copy p {
  max-width: 840px;
  margin: 14px 0 0;
  color: #4e625d;
  font-size: 15px;
  line-height: 1.8;
}

.hero-metrics {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
  margin: 0;
}

.hero-metrics div,
.summary-card,
.preference-panel,
.map-panel,
.ranking-panel,
.risk-panel,
.model-panel,
.analysis-header {
  border: 1px solid rgba(16, 59, 70, 0.12);
  border-radius: 8px;
  background: #ffffff;
}

.hero-metrics div {
  padding: 14px;
}

.hero-metrics dt,
.summary-card span,
.preference-item span,
.panel-heading span,
.ranking-item small,
.risk-item small,
.weight-row span {
  color: #63746f;
  font-size: 12px;
}

.hero-metrics dd {
  margin: 8px 0 4px;
  color: #103b46;
  font-size: 32px;
  font-weight: 900;
}

.hero-metrics small,
.summary-card small {
  color: #4f625d;
  line-height: 1.45;
}

.workspace {
  display: grid;
  grid-template-columns: 132px 1fr;
  min-height: 760px;
  overflow: hidden;
  border: 1px solid #123c45;
  border-radius: 8px;
  background: #103b46;
}

.side-nav {
  display: grid;
  align-content: start;
  gap: 10px;
  padding: 18px 14px;
  background: #082832;
}

.side-title {
  display: grid;
  gap: 4px;
  padding-bottom: 16px;
}

.side-title strong {
  color: #f3bd55;
  font-size: 17px;
}

.side-title span {
  color: rgba(224, 242, 240, 0.72);
  font-size: 12px;
}

.nav-button {
  min-height: 46px;
  border: 1px solid rgba(224, 242, 240, 0.16);
  border-radius: 8px;
  background: transparent;
  color: rgba(224, 242, 240, 0.82);
  font-weight: 800;
  cursor: pointer;
}

.nav-button.active {
  border-color: #f3bd55;
  background: #f3bd55;
  color: #082832;
}

.dashboard {
  padding: 16px;
  background: #dce8e5;
}

.analysis-header {
  display: flex;
  justify-content: space-between;
  gap: 18px;
  padding: 18px;
}

.analysis-header p {
  margin: 0 0 8px;
  color: #526762;
  font-size: 13px;
  font-weight: 800;
}

.analysis-header h3 {
  max-width: 820px;
  margin: 0;
  color: #0f2f36;
  font-size: 28px;
  line-height: 1.25;
}

.live-dot {
  display: inline-block;
  width: 9px;
  height: 9px;
  margin-right: 8px;
  border-radius: 50%;
  background: #2bbf79;
  box-shadow: 0 0 0 6px rgba(43, 191, 121, 0.16);
}

.readiness-score {
  display: grid;
  min-width: 156px;
  place-items: center;
  border-left: 1px solid #d4dfdc;
}

.readiness-score span,
.readiness-score small {
  color: #526762;
  font-size: 12px;
  font-weight: 800;
}

.readiness-score strong {
  color: #103b46;
  font-size: 52px;
  line-height: 1;
}

.summary-row {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
  margin-top: 10px;
}

.summary-card {
  padding: 14px;
}

.summary-card strong {
  display: block;
  margin: 8px 0 3px;
  color: #102f36;
  font-size: 28px;
}

.main-grid {
  display: grid;
  grid-template-columns: 280px minmax(430px, 1fr) 360px;
  gap: 12px;
  margin-top: 12px;
}

.preference-panel,
.ranking-panel,
.risk-panel,
.model-panel {
  padding: 16px;
}

.panel-heading {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
  margin-bottom: 14px;
}

.panel-heading h4 {
  margin: 0;
  color: #0f2f36;
  font-size: 18px;
}

.panel-heading span {
  padding: 6px 8px;
  border-radius: 8px;
  background: #edf5f2;
  color: #31544d;
  font-weight: 900;
}

.preference-item {
  display: grid;
  gap: 6px;
  padding: 12px 0;
  border-bottom: 1px solid #dfe8e5;
}

.preference-item strong {
  color: #102f36;
  font-size: 16px;
}

.preference-item small {
  color: #526762;
  line-height: 1.55;
}

.map-panel {
  min-height: 540px;
  overflow: hidden;
  background: #103b46;
}

.map-header {
  position: relative;
  z-index: 2;
  display: flex;
  justify-content: space-between;
  gap: 14px;
  padding: 16px;
  color: #e0f2f0;
}

.map-header h4 {
  margin: 0;
  font-size: 20px;
}

.legend {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  color: rgba(224, 242, 240, 0.82);
  font-size: 12px;
}

.legend span {
  display: inline-flex;
  align-items: center;
  gap: 5px;
}

.legend i,
.risk-item i {
  width: 9px;
  height: 9px;
  border-radius: 50%;
}

.safe,
.normal {
  background: #8ee8c5;
}

.watch,
.warning {
  background: #f3bd55;
}

.avoid,
.danger {
  background: #ff786c;
}

.map-canvas {
  position: relative;
  height: 466px;
  overflow: hidden;
  background:
    linear-gradient(90deg, rgba(142, 232, 197, 0.08) 1px, transparent 1px),
    linear-gradient(180deg, rgba(142, 232, 197, 0.08) 1px, transparent 1px),
    radial-gradient(circle at 65% 48%, rgba(142, 232, 197, 0.22), transparent 18%),
    #103b46;
  background-size: 34px 34px, 34px 34px, auto, auto;
}

.continent {
  position: absolute;
  border: 1px solid rgba(224, 242, 240, 0.2);
  border-radius: 44% 56% 47% 53%;
  background: rgba(224, 242, 240, 0.12);
}

.continent-america {
  left: 15%;
  top: 23%;
  width: 120px;
  height: 220px;
  transform: rotate(-14deg);
}

.continent-europe {
  left: 40%;
  top: 22%;
  width: 112px;
  height: 90px;
}

.continent-africa {
  left: 45%;
  top: 42%;
  width: 120px;
  height: 160px;
  transform: rotate(9deg);
}

.continent-asia {
  left: 57%;
  top: 25%;
  width: 230px;
  height: 175px;
  border-radius: 45% 55% 54% 46%;
}

.continent-oceania {
  left: 74%;
  top: 68%;
  width: 98px;
  height: 62px;
}

.latitude-line {
  position: absolute;
  left: 6%;
  right: 6%;
  height: 1px;
  background: rgba(243, 189, 85, 0.22);
}

.line-one {
  top: 39%;
}

.line-two {
  top: 63%;
}

.map-marker {
  position: absolute;
  z-index: 2;
  display: grid;
  min-width: 62px;
  gap: 2px;
  padding: 7px 9px;
  border: 1px solid rgba(255, 255, 255, 0.86);
  border-radius: 8px;
  color: #082832;
  font-size: 12px;
  font-weight: 900;
  text-align: center;
  box-shadow: 0 10px 26px rgba(0, 0, 0, 0.18);
  transform: translate(-50%, -50%);
}

.map-marker.avoid {
  color: #ffffff;
}

.map-marker small {
  font-size: 11px;
}

.ranking-item {
  display: grid;
  grid-template-columns: 42px 1fr 50px;
  gap: 12px;
  align-items: start;
  padding: 14px 0;
  border-bottom: 1px solid #dfe8e5;
}

.ranking-item .rank {
  color: #f3bd55;
  font-weight: 900;
}

.ranking-item strong {
  color: #102f36;
  font-size: 18px;
}

.ranking-item p {
  margin: 5px 0;
  color: #526762;
  font-size: 12px;
  line-height: 1.5;
}

.ranking-item small {
  color: #8a5a1e;
  line-height: 1.5;
}

.ranking-item b {
  color: #103b46;
  font-size: 22px;
}

.bottom-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.25fr) minmax(320px, 0.75fr);
  gap: 12px;
  margin-top: 12px;
}

.risk-item {
  display: grid;
  grid-template-columns: 12px 1fr 54px;
  gap: 12px;
  align-items: center;
  padding: 11px 0;
  border-top: 1px solid #dfe8e5;
}

.risk-item strong {
  display: block;
  margin-bottom: 4px;
  color: #102f36;
}

.risk-item > span {
  color: #31544d;
  font-weight: 900;
  text-align: right;
}

.weight-row {
  display: grid;
  grid-template-columns: 1fr 48px;
  gap: 8px;
  align-items: center;
  margin-top: 12px;
}

.weight-row i {
  grid-column: 1 / -1;
  display: block;
  height: 8px;
  border-radius: 8px;
  background: #103b46;
}

button:focus-visible {
  outline: 3px solid rgba(47, 128, 160, 0.35);
  outline-offset: 2px;
}

@media (max-width: 1120px) {
  .hero-panel,
  .workspace,
  .main-grid,
  .bottom-grid {
    grid-template-columns: 1fr;
  }

  .side-nav {
    grid-template-columns: repeat(6, minmax(0, 1fr));
  }

  .summary-row,
  .hero-metrics {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 680px) {
  .travel-analytics-page {
    padding: 16px;
  }

  .topbar,
  .analysis-header,
  .map-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .topbar-actions {
    flex-direction: column;
    width: 100%;
  }

  .hero-copy h2 {
    font-size: 30px;
  }

  .side-nav,
  .summary-row,
  .hero-metrics {
    grid-template-columns: 1fr;
  }

  .readiness-score {
    width: 100%;
    border-left: none;
    border-top: 1px solid #d4dfdc;
    padding-top: 14px;
  }
}
</style>
