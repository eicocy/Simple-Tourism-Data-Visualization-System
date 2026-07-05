<template>
  <div class="home-page">
    <header class="top-bar">
      <div class="brand-block">
        <p class="brand-tag">Graduation Project</p>
        <h1>安全旅游国家推荐与可视化系统</h1>
      </div>

      <div class="auth-actions">
        <el-button plain @click="openLoginDialog">登录</el-button>
        <el-button type="primary" @click="openRegisterDialog">注册</el-button>
      </div>
    </header>

    <section class="hero-layout">
      <section class="intro-panel">
        <p class="intro-tag">World Insight</p>
        <h2>基于国家指标的世界旅游安全地图</h2>
        <p class="intro-desc">
          地图以最新国家指标数据为基础进行着色，颜色由浅到深表示推荐指数由低到高。
          当前首页直接读取后端数据库中的真实国家数据，用于展示系统的核心可视化效果。
        </p>

        <div class="intro-stats">
          <article class="stat-card">
            <span>覆盖国家</span>
            <strong>{{ worldMapData.length }}</strong>
          </article>
          <article class="stat-card">
            <span>最高推荐指数</span>
            <strong>{{ highestScore }}</strong>
          </article>
          <article class="stat-card">
            <span>数据年份</span>
            <strong>{{ latestYear }}</strong>
          </article>
        </div>

        <div class="intro-buttons">
          <el-button type="primary" @click="goSystem">进入系统</el-button>
          <el-button plain @click="openLoginDialog">管理员登录</el-button>
        </div>
      </section>

      <section class="map-stage">
        <div class="map-panel">
          <div class="map-panel-header">
            <div>
              <p class="map-tag">Global Map</p>
              <h3>世界旅游推荐指数分布</h3>
            </div>
            <el-tag type="success">颜色越深推荐越高</el-tag>
          </div>

          <el-empty
            v-if="!worldMapData.length && !mapLoading"
            description="暂无地图数据，请先导入国家指标数据"
          />
          <div v-show="worldMapData.length" ref="mapRef" class="map-canvas"></div>
        </div>
      </section>
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
import { ElMessage } from "element-plus";

import echarts from "@/plugins/echarts";
import { getCountryMapDataApi, loginApi, registerApi } from "@/api";
import { useUserStore } from "@/store";

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

// 世界地图英文名到中文名映射，用于地图悬浮与强调显示汉化
const WORLD_NAME_MAP = {
  Afghanistan: "阿富汗",
  Albania: "阿尔巴尼亚",
  Algeria: "阿尔及利亚",
  Angola: "安哥拉",
  Argentina: "阿根廷",
  Armenia: "亚美尼亚",
  Australia: "澳大利亚",
  Austria: "奥地利",
  Azerbaijan: "阿塞拜疆",
  Bahamas: "巴哈马",
  Bahrain: "巴林",
  Bangladesh: "孟加拉国",
  Belarus: "白俄罗斯",
  Belgium: "比利时",
  Belize: "伯利兹",
  Benin: "贝宁",
  Bhutan: "不丹",
  Bolivia: "玻利维亚",
  "Bosnia and Herzegovina": "波斯尼亚和黑塞哥维那",
  Botswana: "博茨瓦纳",
  Brazil: "巴西",
  Brunei: "文莱",
  Bulgaria: "保加利亚",
  "Burkina Faso": "布基纳法索",
  Burundi: "布隆迪",
  Cambodia: "柬埔寨",
  Cameroon: "喀麦隆",
  Canada: "加拿大",
  Chad: "乍得",
  Chile: "智利",
  China: "中国",
  Colombia: "哥伦比亚",
  Congo: "刚果",
  "Costa Rica": "哥斯达黎加",
  Croatia: "克罗地亚",
  Cuba: "古巴",
  Cyprus: "塞浦路斯",
  Czechia: "捷克",
  Denmark: "丹麦",
  Djibouti: "吉布提",
  "Dominican Republic": "多米尼加",
  Ecuador: "厄瓜多尔",
  Egypt: "埃及",
  "El Salvador": "萨尔瓦多",
  Estonia: "爱沙尼亚",
  Ethiopia: "埃塞俄比亚",
  Finland: "芬兰",
  France: "法国",
  Gabon: "加蓬",
  Gambia: "冈比亚",
  Georgia: "格鲁吉亚",
  Germany: "德国",
  Ghana: "加纳",
  Greece: "希腊",
  Greenland: "格陵兰",
  Guatemala: "危地马拉",
  Guinea: "几内亚",
  Guyana: "圭亚那",
  Haiti: "海地",
  Honduras: "洪都拉斯",
  "Hong Kong": "中国香港",
  Hungary: "匈牙利",
  Iceland: "冰岛",
  India: "印度",
  Indonesia: "印度尼西亚",
  Iran: "伊朗",
  Iraq: "伊拉克",
  Ireland: "爱尔兰",
  Israel: "以色列",
  Italy: "意大利",
  Jamaica: "牙买加",
  Japan: "日本",
  Jordan: "约旦",
  Kazakhstan: "哈萨克斯坦",
  Kenya: "肯尼亚",
  Kosovo: "科索沃",
  Kuwait: "科威特",
  Kyrgyzstan: "吉尔吉斯斯坦",
  Laos: "老挝",
  Latvia: "拉脱维亚",
  Lebanon: "黎巴嫩",
  Lesotho: "莱索托",
  Liberia: "利比里亚",
  Libya: "利比亚",
  Lithuania: "立陶宛",
  Luxembourg: "卢森堡",
  Macao: "中国澳门",
  Madagascar: "马达加斯加",
  Malawi: "马拉维",
  Malaysia: "马来西亚",
  Mali: "马里",
  Malta: "马耳他",
  Mauritania: "毛里塔尼亚",
  Mauritius: "毛里求斯",
  Mexico: "墨西哥",
  Moldova: "摩尔多瓦",
  Mongolia: "蒙古",
  Montenegro: "黑山",
  Morocco: "摩洛哥",
  Mozambique: "莫桑比克",
  Myanmar: "缅甸",
  Namibia: "纳米比亚",
  Nepal: "尼泊尔",
  Netherlands: "荷兰",
  "New Zealand": "新西兰",
  Nicaragua: "尼加拉瓜",
  Niger: "尼日尔",
  Nigeria: "尼日利亚",
  "North Korea": "朝鲜",
  "North Macedonia": "北马其顿",
  Norway: "挪威",
  Oman: "阿曼",
  Pakistan: "巴基斯坦",
  Panama: "巴拿马",
  Paraguay: "巴拉圭",
  Peru: "秘鲁",
  Philippines: "菲律宾",
  Poland: "波兰",
  Portugal: "葡萄牙",
  Qatar: "卡塔尔",
  Romania: "罗马尼亚",
  Russia: "俄罗斯",
  Rwanda: "卢旺达",
  "Saudi Arabia": "沙特阿拉伯",
  Senegal: "塞内加尔",
  Serbia: "塞尔维亚",
  "Sierra Leone": "塞拉利昂",
  Singapore: "新加坡",
  Slovakia: "斯洛伐克",
  Slovenia: "斯洛文尼亚",
  Somalia: "索马里",
  "South Africa": "南非",
  "South Korea": "韩国",
  Korea: "韩国",
  Spain: "西班牙",
  "Sri Lanka": "斯里兰卡",
  Sudan: "苏丹",
  Suriname: "苏里南",
  Sweden: "瑞典",
  Switzerland: "瑞士",
  Syria: "叙利亚",
  Taiwan: "中国台湾",
  Tajikistan: "塔吉克斯坦",
  Tanzania: "坦桑尼亚",
  Thailand: "泰国",
  Togo: "多哥",
  Tunisia: "突尼斯",
  Turkey: "土耳其",
  Turkmenistan: "土库曼斯坦",
  Uganda: "乌干达",
  Ukraine: "乌克兰",
  "United Arab Emirates": "阿联酋",
  "United Kingdom": "英国",
  "United States of America": "美国",
  "United States": "美国",
  Uruguay: "乌拉圭",
  Uzbekistan: "乌兹别克斯坦",
  Venezuela: "委内瑞拉",
  Vietnam: "越南",
  Yemen: "也门",
  Zambia: "赞比亚",
  Zimbabwe: "津巴布韦",
};

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
  return WORLD_NAME_MAP[mapName] || WORLD_NAME_MAP[backendName] || backendName || mapName;
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

  await ensureWorldMapRegistered();

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
        color: "#4d6b8a",
      },
      inRange: {
        color: ["#dceeff", "#9fcbff", "#5f9ef5", "#1e5fbf"],
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
            formatter: (params) => WORLD_NAME_MAP[params.name] || params.name,
          },
          itemStyle: {
            areaColor: "#d9af6b",
          },
        },
        itemStyle: {
          areaColor: "#edf5ff",
          borderColor: "rgba(103, 145, 198, 0.75)",
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

function handleResize() {
  worldMapInstance?.resize();
}

onMounted(async () => {
  try {
    await loadWorldMapData();
    await nextTick();
    await renderWorldMap();
    window.addEventListener("resize", handleResize);
  } catch (error) {
    ElMessage.error("首页地图加载失败，请检查后端接口或网络后刷新页面");
  }
});

onBeforeUnmount(() => {
  window.removeEventListener("resize", handleResize);

  if (worldMapInstance) {
    worldMapInstance.dispose();
    worldMapInstance = null;
  }
});
</script>

<style scoped>
.home-page {
  min-height: 100vh;
  overflow: hidden;
  background:
    radial-gradient(circle at top left, rgba(132, 185, 255, 0.2), transparent 24%),
    radial-gradient(circle at bottom right, rgba(185, 216, 255, 0.24), transparent 20%),
    linear-gradient(180deg, #ffffff 0%, #f3f8ff 48%, #eef5ff 100%);
}

.top-bar {
  position: relative;
  z-index: 2;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 20px;
  padding: 28px 34px 0;
}

.brand-block h1 {
  margin: 8px 0 0;
  color: #173b63;
  font-size: 34px;
  font-weight: 700;
}

.brand-tag {
  margin: 0;
  color: rgba(23, 59, 99, 0.72);
  text-transform: uppercase;
  letter-spacing: 0.14em;
  font-size: 12px;
}

.auth-actions {
  display: flex;
  gap: 12px;
}

.hero-layout {
  position: relative;
  z-index: 2;
  display: grid;
  grid-template-columns: 620px minmax(580px, 1fr);
  gap: 28px;
  align-items: center;
  padding: 6vh 34px 34px;
}

.intro-panel {
  padding: 28px;
  border: 1px solid rgba(142, 180, 224, 0.38);
  border-radius: 28px;
  background: rgba(255, 255, 255, 0.88);
  backdrop-filter: blur(14px);
  box-shadow: 0 24px 60px rgba(74, 116, 167, 0.12);
}

.intro-tag {
  margin: 0 0 12px;
  color: #4d7ec4;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  font-size: 12px;
}

.intro-panel h2 {
  margin: 0 0 14px;
  color: #183b62;
  font-size: 42px;
  line-height: 1.18;
}

.intro-desc {
  margin: 0;
  color: rgba(42, 72, 108, 0.82);
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
  border-radius: 18px;
  background: linear-gradient(180deg, #f7fbff 0%, #edf5ff 100%);
  border: 1px solid rgba(145, 184, 231, 0.32);
}

.stat-card span {
  display: block;
  margin-bottom: 8px;
  color: rgba(69, 103, 145, 0.74);
  font-size: 13px;
}

.stat-card strong {
  color: #17416b;
  font-size: 24px;
}

.intro-buttons {
  display: flex;
  gap: 12px;
  margin-top: 24px;
}

.map-stage {
  min-height: 72vh;
}

.map-panel {
  min-height: 72vh;
  padding: 20px 20px 10px;
  border-radius: 32px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.96), rgba(241, 247, 255, 0.96));
  border: 1px solid rgba(150, 187, 232, 0.4);
  backdrop-filter: blur(8px);
  box-shadow: 0 24px 60px rgba(83, 122, 173, 0.14);
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
  color: #4d7ec4;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  font-size: 12px;
}

.map-panel-header h3 {
  margin: 0;
  color: #173b63;
  font-size: 26px;
}

.map-canvas {
  width: 100%;
  height: calc(72vh - 70px);
  min-height: 540px;
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
</style>

