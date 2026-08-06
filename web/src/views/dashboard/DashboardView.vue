<template>
  <div class="home-shell">
    <section class="portfolio-frame">
      <header class="portfolio-nav">
        <button class="brand-chip" type="button" @click="goHomeTop">SAFE TRAVEL</button>
        <nav class="nav-tabs" aria-label="首页导航">
          <button class="active" type="button">Dashboard</button>
          <button type="button" @click="goSystem">Project</button>
          <button type="button" @click="goVisualization">Case Study</button>
        </nav>
        <div class="nav-actions">
          <button class="minimize-button" type="button" aria-label="Minimize">?</button>
          <el-button class="home-ghost-button" plain @click="openLoginDialog">登录</el-button>
          <el-button class="home-primary-button" type="primary" @click="openRegisterDialog">注册</el-button>
        </div>
      </header>

      <main class="portfolio-grid">
        <article class="portfolio-card hello-card">
          <div class="code-globe" aria-hidden="true">
            <span v-for="row in codeRows" :key="row">{{ row }}</span>
          </div>
          <h1>Hello<br />Traveler</h1>
          <p>
            let destination = safer.route(); &gt; The analysis is open.
            Type nothing. Just explore.
          </p>
        </article>

        <HomeGaugeCard
          :display-value="highestScore"
          value-label="Top index"
          :left-label="latestYear"
          center-label="Recommendation model"
          right-label="100"
        />

        <HomeSkillMatrix
          :skills="skillMatrix"
          :tools="matrixTools"
          :note="`${worldMapData.length || 0} countries improving`"
        />

        <article class="portfolio-card tunnel-card">
          <div class="perspective-stage" aria-hidden="true">
            <i class="plane plane-back"></i>
            <i class="plane plane-mid"></i>
            <i class="plane plane-front"></i>
            <span
              v-for="tile in tunnelTiles"
              :key="tile.label"
              :class="['floating-tile', tile.className]"
            >
              {{ tile.label }}
            </span>
          </div>
          <div class="tunnel-actions">
            <button type="button" @click="openLoginDialog">Who are you?</button>
            <button type="button" @click="goSystem">Open system</button>
          </div>
        </article>

        <article class="portfolio-card experience-card">
          <div class="experience-head">
            <span>? My experience</span>
            <b>{{ worldMapData.length || "--" }} countries</b>
          </div>
          <el-empty
            v-if="!worldMapData.length && !mapLoading"
            class="home-empty"
            description="暂无地图数据，请先导入国家指标数据"
          />
          <div v-show="worldMapData.length" ref="mapRef" class="map-canvas"></div>
          <div class="coordinate-tags" aria-hidden="true">
            <span>42.3601° N, 71.0589° W</span>
            <span>37.7749° N, 122.4194° W</span>
            <span>31.2304° N, 121.4737° E</span>
          </div>
        </article>
      </main>
    </section>

    <el-dialog
      v-model="loginDialogVisible"
      title="用户登录"
      width="420px"
      destroy-on-close
    >
      <el-form
        ref="loginFormRef"
        :model="loginForm"
        :rules="loginRules"
        label-position="top"
      >
        <el-form-item label="用户名" prop="username">
          <el-input v-model="loginForm.username" placeholder="请输入用户名" clearable />
        </el-form-item>

        <el-form-item label="密码" prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            show-password
            clearable
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="loginDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="loginLoading" @click="handleLogin">
          登录
        </el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="registerDialogVisible"
      title="用户注册"
      width="460px"
      destroy-on-close
    >
      <el-form
        ref="registerFormRef"
        :model="registerForm"
        :rules="registerRules"
        label-position="top"
      >
        <el-form-item label="用户名" prop="username">
          <el-input v-model="registerForm.username" placeholder="请输入用户名" clearable />
        </el-form-item>

        <el-form-item label="昵称">
          <el-input v-model="registerForm.nickname" placeholder="请输入昵称" clearable />
        </el-form-item>

        <el-form-item label="邮箱">
          <el-input v-model="registerForm.email" placeholder="请输入邮箱" clearable />
        </el-form-item>

        <el-form-item label="密码" prop="password">
          <el-input
            v-model="registerForm.password"
            type="password"
            placeholder="请输入密码"
            show-password
            clearable
          />
        </el-form-item>

        <el-form-item label="确认密码" prop="confirm_password">
          <el-input
            v-model="registerForm.confirm_password"
            type="password"
            placeholder="请再次输入密码"
            show-password
            clearable
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="registerDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="registerLoading" @click="handleRegister">
          注册
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, reactive, ref } from "vue";
import { useRouter } from "vue-router";

import HomeGaugeCard from "@/components/home/HomeGaugeCard.vue";
import HomeSkillMatrix from "@/components/home/HomeSkillMatrix.vue";
import { loadEcharts } from "@/plugins/echarts";
import { getCountryMapDataApi, loginApi, registerApi } from "@/api";
import { useUserStore } from "@/store";
import { getLocalizedCountryName } from "@/utils/countryNameMap";
import { runWhenVisible } from "@/utils/lazyChart";

const router = useRouter();
const userStore = useUserStore();

const mapRef = ref(null);
const loginFormRef = ref(null);
const registerFormRef = ref(null);

const loginDialogVisible = ref(false);
const registerDialogVisible = ref(false);
const loginLoading = ref(false);
const registerLoading = ref(false);
const mapLoading = ref(false);
const latestYear = ref("--");
const worldMapData = ref([]);

let worldMapInstance = null;
let echartsInstance = null;
let stopWorldMapRender = null;

// 世界地图英文名到中文名映射统一复用工具函数。
const WORLD_MAP_SCRIPT_URLS = [
  "https://cdn.jsdelivr.net/npm/echarts-maps@1.1.0/world.js",
  "https://unpkg.com/echarts-maps@1.1.0/world.js",
];

const highestScore = computed(() => {
  if (!worldMapData.value.length) {
    return "--";
  }
  return Math.max(...worldMapData.value.map((item) => item.value)).toFixed(2);
});

const codeRows = [
  "risk.map(country).score().sort(desc)",
  "visa.signal + safety.index + ppp.cost",
  "tourism.weight = 0.40; safety = 0.30",
  "route.click(country) -> country.detail",
  "agent.answer('where should I go?')",
  "dataset.sync(year).normalize(0, 100)",
  "if safety < threshold: mark.watch",
  "happiness.index contributes comfort",
];

const skillMatrix = computed(() => [
  { name: "Tourism Suitability", score: 40 },
  { name: "Safety Index", score: 30 },
  { name: "Budget Comfort", score: 15 },
  { name: "Happiness Signal", score: 15 },
  { name: "Map Interaction", score: worldMapData.value.length ? 100 : 0 },
  { name: "Recommendation Flow", score: 100 },
  { name: "Risk Explanation", score: 90 },
  { name: "Country Detail", score: 85 },
  { name: "Visualization Agent", score: 80 },
]);

const matrixTools = [
  "Vue",
  "Tailwind",
  "ECharts",
  "Element Plus",
  "Pinia",
  "Django API",
  "Recommendation",
  "Map Agent",
];

const tunnelTiles = [
  { label: "Safety", className: "tile-safety" },
  { label: "Budget", className: "tile-budget" },
  { label: "Visa", className: "tile-visa" },
  { label: "Index", className: "tile-index" },
  { label: "Map", className: "tile-map" },
];

const loginForm = reactive({
  username: "admin",
  password: "lll190",
});

const registerForm = reactive({
  username: "",
  nickname: "",
  email: "",
  password: "",
  confirm_password: "",
});

const loginRules = {
  username: [{ required: true, message: "请输入用户名", trigger: "blur" }],
  password: [{ required: true, message: "请输入密码", trigger: "blur" }],
};

const registerRules = {
  username: [{ required: true, message: "请输入用户名", trigger: "blur" }],
  password: [{ required: true, message: "请输入密码", trigger: "blur" }],
  confirm_password: [
    { required: true, message: "请输入确认密码", trigger: "blur" },
    {
      validator: (_rule, value, callback) => {
        if (value !== registerForm.password) {
          callback(new Error("两次输入的密码不一致"));
          return;
        }
        callback();
      },
      trigger: "blur",
    },
  ],
};

function openLoginDialog() {
  loginDialogVisible.value = true;
}

function openRegisterDialog() {
  registerDialogVisible.value = true;
}

function goSystem() {
  router.push("/app/recommendation");
}

function goVisualization() {
  router.push("/app/visualization");
}

function goHomeTop() {
  window.scrollTo({ top: 0, behavior: "smooth" });
}

async function handleLogin() {
  await loginFormRef.value?.validate();
  loginLoading.value = true;

  try {
    const result = await loginApi(loginForm);
    userStore.setAuthPayload(result.data);
    ElMessage.success(result.message || "登录成功");
    loginDialogVisible.value = false;
    router.push(userStore.isAdmin ? "/app/admin" : "/app/recommendation");
  } catch (error) {
    if (!error?.response) {
      ElMessage.error("无法连接后端服务，请检查 Django 服务是否已启动");
    }
  } finally {
    loginLoading.value = false;
  }
}

async function handleRegister() {
  await registerFormRef.value?.validate();
  registerLoading.value = true;

  try {
    const result = await registerApi(registerForm);
    ElMessage.success(result.message || "注册成功，请登录");
    registerDialogVisible.value = false;
    loginForm.username = registerForm.username;
    loginForm.password = registerForm.password;
    loginDialogVisible.value = true;
  } catch (error) {
    if (!error?.response) {
      ElMessage.error("无法连接后端服务，请检查 Django 服务是否已启动");
    }
  } finally {
    registerLoading.value = false;
  }
}

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

async function getEcharts() {
  if (!echartsInstance) {
    echartsInstance = await loadEcharts();
  }
  return echartsInstance;
}

async function ensureWorldMapRegistered() {
  const echarts = await getEcharts();
  if (echarts.getMap("world")) {
    return echarts;
  }

  window.echarts = echarts;

  let lastError = null;
  for (const url of WORLD_MAP_SCRIPT_URLS) {
    try {
      await loadScript(url);
      if (echarts.getMap("world")) {
        return echarts;
      }
    } catch (error) {
      lastError = error;
    }
  }

  throw lastError || new Error("世界地图加载失败");
}

function normalizeMapName(name) {
  const aliasMap = {
    USA: "United States",
    "United States": "United States of America",
    UAE: "United Arab Emirates",
    UK: "United Kingdom",
    "South Korea": "Korea",
    "Hong Kong": "Hong Kong",
    "Vietnam": "Vietnam",
  };
  return aliasMap[name] || name;
}

function isEnglishText(value) {
  return /^[A-Za-z\s().,'&-]+$/.test(String(value || "").trim());
}

function getDisplayCountryName(data, mapName) {
  const backendName = data?.country_name;
  if (backendName && !isEnglishText(backendName)) {
    return backendName;
  }
  return getLocalizedCountryName(mapName || backendName) || backendName || mapName;
}

async function loadWorldMapData() {
  mapLoading.value = true;
  try {
    const result = await getCountryMapDataApi();
    const results = result?.data?.results || [];
    latestYear.value = result?.data?.year || "--";
    worldMapData.value = results
      .filter((item) => item.country_name_en)
      .map((item) => ({
        name: normalizeMapName(item.country_name_en),
        value: Number(item.recommendation_index ?? 0),
        country_id: item.country_id,
        country_name: item.country_name,
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

async function renderWorldMap() {
  if (!mapRef.value || !worldMapData.value.length) {
    return;
  }

  const echarts = await ensureWorldMapRegistered();

  if (worldMapInstance) {
    worldMapInstance.dispose();
  }

  worldMapInstance = echarts.init(mapRef.value);
  worldMapInstance.setOption({
    backgroundColor: "transparent",
    tooltip: {
      trigger: "item",
      formatter: (params) => {
        const data = params.data || {};
        const displayName = getDisplayCountryName(data, params.name);
        const detail = data.tourism_detail || {};
        return [
          `${displayName}`,
          `推荐指数：${params.value ?? "暂无数据"}`,
          `旅游适宜指数：${data.tourism_index ?? "--"}`,
          `旅游吸引力：${detail.destination_attraction_score ?? "--"}`,
          `签证便利度：${detail.visa_convenience_score ?? "--"}`,
          `基础设施代理分：${detail.tourism_infrastructure_score ?? "--"}`,
          `旅游环境分：${detail.travel_environment_score ?? "--"}`,
          `安全指数：${data.safety_index ?? "--"}`,
          `PPP 指数：${data.ppp_index ?? "--"}`,
          `幸福指数：${data.happiness_index ?? "--"}`,
        ].join("<br/>");
      },
    },
    visualMap: {
      min: 0,
      max: 100,
      text: ["高", "低"],
      calculable: true,
      orient: "vertical",
      right: 24,
      bottom: 26,
      textStyle: {
        color: "rgba(255, 255, 255, 0.62)",
      },
      inRange: {
        color: ["#17201d", "#31584e", "#7ec6a6", "#c7ff64"],
      },
    },
    series: [
      {
        name: "推荐指数",
        type: "map",
        map: "world",
        roam: true,
        zoom: 1.12,
        emphasis: {
          label: {
            show: true,
            color: "#ffffff",
            formatter: (params) => getLocalizedCountryName(params.name),
          },
          itemStyle: {
            areaColor: "#ffb84d",
          },
        },
        itemStyle: {
          areaColor: "#111714",
          borderColor: "rgba(199, 255, 100, 0.24)",
          borderWidth: 1,
        },
        data: worldMapData.value,
      },
    ],
  });

  // 点击地图上的国家后进入国家详情页，未登录用户会由路由守卫引导到登录页
  worldMapInstance.off("click");
  worldMapInstance.on("click", (params) => {
    const countryId = params.data?.country_id;
    if (countryId) {
      router.push(`/app/countries/${countryId}`);
    }
  });
}

function scheduleWorldMapRender() {
  if (worldMapInstance) {
    renderWorldMap();
    return;
  }

  stopWorldMapRender?.();
  stopWorldMapRender = runWhenVisible(mapRef, () => {
    renderWorldMap().catch(() => {
      ElMessage.error("首页地图加载失败，请检查后端接口或网络后刷新页面");
    });
  });
}

function handleResize() {
  worldMapInstance?.resize();
}

onMounted(async () => {
  try {
    await loadWorldMapData();
    await nextTick();
    scheduleWorldMapRender();
    window.addEventListener("resize", handleResize);
  } catch (error) {
    ElMessage.error("首页地图加载失败，请检查后端接口或网络后刷新页面");
  }
});

onBeforeUnmount(() => {
  window.removeEventListener("resize", handleResize);
  stopWorldMapRender?.();

  if (worldMapInstance) {
    worldMapInstance.dispose();
    worldMapInstance = null;
  }
});
</script>

<style scoped>
.home-page {
  min-height: 100vh;
  overflow: auto;
  background:
    linear-gradient(90deg, rgba(40, 106, 115, 0.055) 1px, transparent 1px),
    linear-gradient(180deg, rgba(40, 106, 115, 0.055) 1px, transparent 1px),
    #f4f7f5;
  background-size: 40px 40px;
}

.top-bar {
  position: relative;
  z-index: 2;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 20px;
  padding: 26px 34px 0;
}

.brand-block h1 {
  margin: 8px 0 0;
  color: var(--color-primary-dark);
  font-size: 32px;
  font-weight: 800;
}

.brand-tag {
  margin: 0;
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0;
  font-size: 12px;
  font-weight: 800;
}

.auth-actions {
  display: flex;
  gap: 12px;
}

.hero-layout {
  position: relative;
  z-index: 2;
  display: grid;
  grid-template-columns: 430px minmax(620px, 1fr);
  gap: 18px;
  align-items: stretch;
  padding: 34px;
}

.intro-panel {
  display: flex;
  flex-direction: column;
  padding: 24px;
  border: 1px solid var(--color-line);
  border-radius: 8px;
  background: var(--color-panel);
  box-shadow: var(--shadow-panel);
}

.intro-tag {
  margin: 0 0 12px;
  color: #145c67;
  letter-spacing: 0;
  text-transform: uppercase;
  font-size: 12px;
  font-weight: 900;
}

.intro-panel h2 {
  margin: 0 0 14px;
  color: #0b2f38;
  font-size: 38px;
  line-height: 1.16;
}

.intro-desc {
  margin: 0;
  color: #526762;
  line-height: 1.8;
  font-size: 15px;
}

.intro-stats {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
  margin-top: 22px;
}

.stat-card {
  padding: 16px;
  border-radius: 8px;
  background: #f4f8f6;
  border: 1px solid var(--color-line);
}

.stat-card span {
  display: block;
  margin-bottom: 8px;
  color: #60716d;
  font-size: 13px;
}

.stat-card strong {
  color: #0b2f38;
  font-size: 28px;
}

.intro-buttons {
  display: flex;
  gap: 12px;
  margin-top: 24px;
}

.analysis-notes {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  margin-top: auto;
  padding-top: 22px;
  color: var(--color-text-secondary);
  font-size: 13px;
  font-weight: 700;
}

.analysis-notes span:first-child {
  color: var(--color-primary);
}

.method-note {
  margin-top: 14px;
  padding-top: 14px;
  border-top: 1px solid var(--color-line);
}

.method-note strong,
.source-note span {
  color: var(--color-primary-dark);
  font-size: 13px;
  font-weight: 900;
}

.method-note p,
.source-note p {
  margin: 6px 0 0;
  color: var(--color-text-secondary);
  font-size: 13px;
  line-height: 1.7;
}

.map-stage {
  min-height: 74vh;
}

.map-panel {
  min-height: 74vh;
  padding: 20px 20px 10px;
  border-radius: 8px;
  background: #fbfdfb;
  border: 1px solid var(--color-line);
  box-shadow: var(--shadow-panel);
}

.map-panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  padding: 4px 10px 12px;
}

.map-tag {
  margin: 0 0 8px;
  color: #145c67;
  letter-spacing: 0;
  text-transform: uppercase;
  font-size: 12px;
  font-weight: 900;
}

.map-panel-header h3 {
  margin: 0;
  color: #0b2f38;
  font-size: 26px;
}

.map-toolbar {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: center;
  padding: 10px;
  border-top: 1px solid var(--color-line);
  border-bottom: 1px solid var(--color-line);
}

.scale-block,
.map-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--color-text-secondary);
  font-size: 12px;
  font-weight: 700;
}

.scale-block i {
  display: block;
  width: 160px;
  height: 10px;
  border-radius: 999px;
  background: linear-gradient(90deg, #edf4f2, #bcd7d3, #6aaeb0, #286a73);
}

.map-canvas {
  width: 100%;
  height: calc(72vh - 130px);
  min-height: 470px;
}

.source-note {
  display: grid;
  grid-template-columns: 72px 1fr;
  gap: 10px;
  padding: 10px;
  border-top: 1px solid var(--color-line);
}

@media (max-width: 980px) {
  .top-bar {
    flex-direction: column;
  }

  .brand-block h1 {
    font-size: 28px;
  }

  .hero-layout {
    grid-template-columns: 1fr;
    padding: 28px 16px 24px;
  }

  .intro-panel {
    padding: 22px;
  }

  .intro-panel h2 {
    font-size: 32px;
  }

  .intro-stats {
    grid-template-columns: 1fr;
  }

  .map-panel {
    min-height: 58vh;
  }

  .map-canvas {
    min-height: 420px;
    height: 52vh;
  }
}

@media (max-width: 640px) {
  .top-bar {
    padding: 18px 16px 0;
  }

  .auth-actions,
  .intro-buttons {
    flex-direction: column;
    width: 100%;
  }
}

.map-canvas {
  width: 100%;
  height: min(68vh, 720px);
  min-height: 510px;
}

.home-empty {
  min-height: 510px;
  --el-empty-fill-color-0: rgba(255, 255, 255, 0.9);
  --el-empty-fill-color-1: rgba(255, 255, 255, 0.16);
  --el-empty-fill-color-2: rgba(255, 255, 255, 0.14);
  --el-empty-fill-color-3: rgba(255, 255, 255, 0.12);
  --el-empty-fill-color-4: rgba(255, 255, 255, 0.1);
  --el-empty-fill-color-5: rgba(255, 255, 255, 0.08);
  --el-empty-fill-color-6: rgba(255, 255, 255, 0.06);
  --el-empty-fill-color-7: rgba(255, 255, 255, 0.04);
  --el-empty-fill-color-8: rgba(255, 255, 255, 0.02);
  color: rgba(255, 255, 255, 0.58);
}

.home-primary-button:deep(.el-button),
.home-primary-button {
  border-color: #c7ff64;
  background: #c7ff64;
  color: #050605;
  font-weight: 900;
}

.home-primary-button:hover,
.home-primary-button:focus {
  border-color: #ddff95;
  background: #ddff95;
  color: #050605;
}

.home-ghost-button,
.home-dark-button {
  border-color: rgba(255, 255, 255, 0.2);
  background: rgba(255, 255, 255, 0.04);
  color: rgba(255, 255, 255, 0.82);
  font-weight: 800;
}

.home-ghost-button:hover,
.home-dark-button:hover,
.home-ghost-button:focus,
.home-dark-button:focus {
  border-color: rgba(255, 255, 255, 0.5);
  background: rgba(255, 255, 255, 0.1);
  color: #ffffff;
}

@media (max-width: 980px) {
  .map-canvas {
    height: 58vh;
    min-height: 420px;
  }
}

.home-shell {
  min-height: 100vh;
  padding: 8px;
  overflow-x: hidden;
  background: #000000;
  color: #ffffff;
}

.portfolio-frame {
  min-height: calc(100vh - 16px);
  padding: 8px;
  border-radius: 18px;
  background: #f0f0ee;
}

.portfolio-nav {
  display: grid;
  grid-template-columns: 1fr minmax(280px, 346px) 1fr;
  align-items: center;
  gap: 16px;
  padding: 8px 18px 14px;
}

.brand-chip {
  justify-self: start;
  min-height: 32px;
  padding: 0 10px;
  border: none;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.66);
  color: #171717;
  font-size: 16px;
  font-weight: 700;
}

.nav-tabs {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  height: 26px;
  padding: 1px;
  border: 1px solid #dededc;
  border-radius: 999px;
  background: #f6f6f4;
}

.nav-tabs button {
  border: 0;
  border-radius: 999px;
  background: transparent;
  color: #171717;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
}

.nav-tabs button.active {
  background: #171717;
  color: #ffffff;
}

.nav-actions {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 10px;
}

.minimize-button {
  display: grid;
  width: 44px;
  height: 30px;
  place-items: center;
  border: 0;
  border-radius: 999px;
  background: #ffffff;
  color: #7a7a78;
  font-size: 22px;
  font-weight: 900;
}

.portfolio-grid {
  display: grid;
  grid-template-columns: minmax(280px, 0.9fr) minmax(280px, 0.9fr) minmax(420px, 1.85fr);
  grid-template-rows: minmax(428px, 0.92fr) minmax(468px, 1fr);
  gap: 8px;
  min-width: 0;
}

:global(.portfolio-card) {
  min-width: 0;
  border-radius: 14px;
  background: #171717;
  color: #ffffff;
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.035);
}

.hello-card {
  position: relative;
  min-height: 428px;
  padding: 26px;
  overflow: hidden;
}

.hello-card h1 {
  position: relative;
  z-index: 2;
  margin: 0;
  color: rgba(255, 255, 255, 0.52);
  font-family: var(--font-display);
  font-size: clamp(52px, 5vw, 72px);
  font-weight: 300;
  line-height: 0.92;
}

.hello-card p {
  position: absolute;
  right: 26px;
  bottom: 24px;
  left: 26px;
  z-index: 2;
  margin: 0;
  color: rgba(255, 255, 255, 0.62);
  font-family: var(--font-mono);
  font-size: 11px;
  font-weight: 700;
  line-height: 1.5;
}

.code-globe {
  position: absolute;
  inset: 20px 0 0 -26px;
  display: grid;
  align-content: start;
  gap: 2px;
  width: 115%;
  transform: perspective(620px) rotateX(54deg) rotateZ(0deg);
  transform-origin: top center;
  opacity: 0.76;
  mask-image: radial-gradient(circle at 52% 36%, #000 0 30%, rgba(0, 0, 0, 0.72) 42%, transparent 70%);
}

.code-globe span {
  display: block;
  color: rgba(255, 255, 255, 0.34);
  font-family: var(--font-mono);
  font-size: 10px;
  white-space: nowrap;
  text-shadow:
    54px 12px 0 rgba(255, 255, 255, 0.18),
    108px 26px 0 rgba(255, 255, 255, 0.12),
    162px 40px 0 rgba(255, 255, 255, 0.22),
    216px 54px 0 rgba(255, 255, 255, 0.1);
}

.tunnel-card {
  position: relative;
  grid-column: span 2;
  min-height: 468px;
  overflow: hidden;
  background:
    radial-gradient(circle at 50% 50%, rgba(255, 255, 255, 0.12), transparent 2px),
    #171717;
  background-size: 58px 58px, auto;
}

.perspective-stage {
  position: absolute;
  inset: 30px;
  perspective: 720px;
}

.plane {
  position: absolute;
  inset: 0;
  border: 1px solid rgba(255, 255, 255, 0.13);
  transform-style: preserve-3d;
}

.plane-back {
  transform: translateZ(-180px) scale(0.62);
}

.plane-mid {
  transform: translateZ(-70px) scale(0.82);
}

.plane-front {
  transform: translateZ(20px);
}

.plane::before,
.plane::after {
  position: absolute;
  background: rgba(255, 255, 255, 0.09);
  content: "";
}

.plane::before {
  top: 50%;
  left: -40%;
  width: 180%;
  height: 1px;
}

.plane::after {
  top: -40%;
  left: 50%;
  width: 1px;
  height: 180%;
}

.floating-tile {
  position: absolute;
  display: grid;
  min-width: 86px;
  min-height: 52px;
  place-items: center;
  border: 1px solid rgba(255, 255, 255, 0.16);
  border-radius: 6px;
  color: #ffffff;
  font-size: 13px;
  font-weight: 900;
  box-shadow: 0 18px 46px rgba(0, 0, 0, 0.34);
}

.tile-safety {
  top: 22%;
  left: 11%;
  background: linear-gradient(135deg, #1439ff, #df43ff);
  transform: rotateY(42deg);
}

.tile-budget {
  top: 12%;
  right: 23%;
  background: linear-gradient(135deg, #1f2937, #f2c94c);
  transform: rotateX(55deg);
}

.tile-visa {
  top: 38%;
  right: 8%;
  background: linear-gradient(135deg, #f96856, #111111);
  transform: rotateY(-38deg);
}

.tile-index {
  bottom: 13%;
  left: 27%;
  background: linear-gradient(135deg, #ff5c39, #ffffff);
  color: #171717;
  transform: rotateX(58deg);
}

.tile-map {
  right: 22%;
  bottom: 21%;
  background: linear-gradient(135deg, #12d59a, #3948ff);
  transform: rotateX(58deg);
}

.tunnel-actions {
  position: absolute;
  inset: 0;
  z-index: 2;
  display: grid;
  place-content: center;
  gap: 10px;
}

.tunnel-actions button {
  min-width: 128px;
  min-height: 34px;
  border: 0;
  border-radius: 999px;
  background: #ffffff;
  color: #5c5c5c;
  font-weight: 900;
  cursor: pointer;
}

.tunnel-actions button + button {
  background: #050505;
  color: rgba(255, 255, 255, 0.72);
}

.experience-card {
  position: relative;
  min-height: 468px;
  padding: 14px 18px 18px;
  overflow: hidden;
}

.experience-head {
  position: relative;
  z-index: 3;
  display: flex;
  justify-content: space-between;
  gap: 12px;
  color: rgba(255, 255, 255, 0.62);
  font-size: 12px;
  font-weight: 900;
  text-transform: uppercase;
}

.experience-head b {
  color: rgba(255, 255, 255, 0.42);
}

.coordinate-tags {
  position: absolute;
  inset: 20% 11% 17%;
  pointer-events: none;
}

.coordinate-tags span {
  position: absolute;
  padding: 5px 10px;
  border: 1px solid rgba(255, 255, 255, 0.16);
  border-radius: 999px;
  background: rgba(30, 30, 30, 0.82);
  color: rgba(255, 255, 255, 0.54);
  font-family: var(--font-mono);
  font-size: 10px;
}

.coordinate-tags span:nth-child(1) {
  top: 16%;
  left: 4%;
}

.coordinate-tags span:nth-child(2) {
  left: 2%;
  bottom: 22%;
}

.coordinate-tags span:nth-child(3) {
  right: 3%;
  bottom: 27%;
}

.experience-card .map-canvas {
  height: 426px;
  min-height: 0;
  margin-top: 8px;
  opacity: 0.96;
  filter: grayscale(0.2) contrast(1.08);
}

.experience-card .home-empty {
  min-height: 402px;
}

.home-primary-button {
  border-color: #c7ff64;
  background: #c7ff64;
  color: #050605;
  font-weight: 900;
}

.home-primary-button:hover,
.home-primary-button:focus {
  border-color: #d9ff8a;
  background: #d9ff8a;
  color: #050605;
}

.home-ghost-button {
  border-color: #d8d8d6;
  background: #ffffff;
  color: #171717;
  font-weight: 900;
}

.home-ghost-button:hover,
.home-ghost-button:focus {
  border-color: #171717;
  background: #171717;
  color: #ffffff;
}

@media (max-width: 1180px) {
  .portfolio-grid {
    grid-template-columns: 1fr 1fr;
    grid-template-rows: auto;
  }

  .skill-card,
  .experience-card {
    grid-column: span 2;
  }
}

@media (max-width: 760px) {
  .home-shell {
    padding: 0;
  }

  .portfolio-frame {
    min-height: 100vh;
    border-radius: 0;
  }

  .portfolio-nav {
    grid-template-columns: 1fr;
    padding: 8px 8px 12px;
  }

  .brand-chip,
  .nav-tabs,
  .nav-actions {
    justify-self: stretch;
  }

  .nav-actions {
    justify-content: flex-start;
    flex-wrap: wrap;
  }

  .portfolio-grid {
    grid-template-columns: 1fr;
    width: 100%;
    overflow: hidden;
  }

  .tunnel-card,
  .skill-card,
  .experience-card {
    grid-column: auto;
  }

  .hello-card,
  .tunnel-card,
  .experience-card {
    min-height: 360px;
  }

  .hello-card h1 {
    font-size: 56px;
  }

  .experience-card .map-canvas {
    height: 340px;
  }
}
</style>

