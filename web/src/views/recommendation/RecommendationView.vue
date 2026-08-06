<template>
  <div class="recommendation-page">
    <!-- 页面头部说明 -->
    <section class="page-header">
      <div>
        <p class="page-tag">Recommendation Input</p>
        <h2>安全旅游推荐输入</h2>
        <p class="page-desc">
          输入预算、洲别偏好和安全需求后，系统会结合旅游指数、安全指数、幸福指数和消费友好度，
          生成适合出行的国家排序和可解释结果。
        </p>
      </div>
      <div class="method-summary">
        <span>模型输出</span>
        <strong>综合推荐指数</strong>
        <p>0-100 分，越高越推荐</p>
      </div>
    </section>

    <section class="dimension-strip">
      <article v-for="dimension in analysisDimensions" :key="dimension.name">
        <span>{{ dimension.name }}</span>
        <strong>{{ dimension.weight }}</strong>
        <p>{{ dimension.description }}</p>
      </article>
    </section>

    <div class="page-grid">
      <!-- 左侧推荐参数输入区域 -->
      <section class="form-panel">
        <h3>出行条件</h3>

        <el-form
          ref="formRef"
          :model="formData"
          :rules="formRules"
          label-position="top"
        >
          <el-form-item label="预算等级" prop="budget_level">
            <el-select
              v-model="formData.budget_level"
              placeholder="请选择预算等级"
              style="width: 100%"
            >
              <el-option
                v-for="item in BUDGET_LEVEL_OPTIONS"
                :key="item.value"
                :label="item.label"
                :value="item.value"
              />
            </el-select>
          </el-form-item>

          <el-form-item label="偏好洲别">
            <el-select
              v-model="formData.preferred_continent"
              placeholder="请选择偏好洲别"
              clearable
              style="width: 100%"
            >
              <el-option
                v-for="item in continentOptions"
                :key="item"
                :label="item"
                :value="item"
              />
            </el-select>
          </el-form-item>

          <el-form-item label="安全需求">
            <el-select
              v-model="formData.safety_requirement"
              placeholder="请选择安全需求"
              style="width: 100%"
            >
              <el-option
                v-for="item in SAFETY_REQUIREMENT_OPTIONS"
                :key="item.value"
                :label="item.label"
                :value="item.value"
              />
            </el-select>
          </el-form-item>

          <div class="fixed-weight-panel">
            <div class="weight-title">
              <div>
                <h4>推荐模型权重</h4>
                <p>固定权重用于保证毕业设计演示时推荐逻辑稳定、可复现。</p>
              </div>
              <el-tag type="success">固定模型</el-tag>
            </div>

            <div class="weight-grid">
              <article class="weight-card tourism">
                <span>旅游适宜指数</span>
                <strong>40%</strong>
              </article>
              <article class="weight-card safety">
                <span>安全指数</span>
                <strong>30%</strong>
              </article>
              <article class="weight-card happiness">
                <span>幸福指数</span>
                <strong>15%</strong>
              </article>
              <article class="weight-card cost">
                <span>消费指数</span>
                <strong>15%</strong>
              </article>
            </div>

            <div class="formula-box">
              综合得分 = 旅游适宜指数 × 40% + 安全指数 × 30% + 幸福指数 × 15% + 消费友好度 × 15%
            </div>
          </div>

          <el-form-item>
            <el-button
              type="primary"
              :loading="loading"
              style="width: 100%"
              @click="handleSubmit"
            >
              生成安全旅游推荐
            </el-button>
          </el-form-item>
        </el-form>
      </section>

      <!-- 右侧推荐结果预览区域 -->
      <section class="result-panel">
        <div class="result-header">
          <div>
            <h3>推荐结果预览</h3>
            <p>提交后会跳转到结果页，这里保留最近一次推荐摘要，便于快速核对。</p>
          </div>
          <el-tag v-if="resultList.length" type="success">
            共 {{ resultList.length }} 条
          </el-tag>
        </div>

        <el-empty
          v-if="!resultList.length"
          description="请先填写出行条件并获取推荐结果"
        />

        <div v-else class="result-list">
          <article
            v-for="item in resultList"
            :key="`${item.country_id}-${item.rank}`"
            class="result-card"
          >
            <div class="result-rank">TOP {{ item.rank }}</div>
            <div class="result-main">
              <div class="result-top">
                <h4>{{ getLocalizedCountryName(item.country_name || item.country_name_en) }}</h4>
                <el-tag :type="item.budget_matched ? 'success' : 'warning'">
                  {{ item.budget_matched ? "预算匹配" : "预算偏高" }}
                </el-tag>
              </div>
              <p class="result-meta">
                所属洲别：{{ item.continent || "--" }} · 综合得分：{{ item.score }}
              </p>
              <div class="metric-row">
                <span>旅游适宜指数：{{ formatDisplayNumber(item.tourism_index) }}</span>
                <span>安全指数：{{ formatDisplayNumber(item.safety_index) }}</span>
              </div>
              <div class="metric-row">
                <span>幸福指数：{{ formatDisplayNumber(item.happiness_index) }}</span>
                <span>消费指数：{{ formatDisplayNumber(item.ppp_index) }}</span>
              </div>
              <div class="metric-row">
                <span>安全需求：{{ item.safety_requirement || "--" }}</span>
                <span>{{ item.safety_matched ? "满足安全需求" : "安全需求未完全满足" }}</span>
              </div>
              <p class="result-reason">{{ item.reason }}</p>
            </div>
          </article>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
// 国家推荐输入页逻辑
import { reactive, ref } from "vue";
import { useRouter } from "vue-router";

import { getRecommendationApi } from "@/api";
import { getLocalizedCountryName } from "@/utils/countryNameMap";
import { BUDGET_LEVEL_OPTIONS, SAFETY_REQUIREMENT_OPTIONS } from "@/utils/constants";
import { setStorage } from "@/utils/storage";

// 路由实例，用于跳转到结果页
const router = useRouter();

// 表单引用，用于触发表单校验
const formRef = ref(null);

// 按钮加载状态
const loading = ref(false);

// 推荐结果列表
const resultList = ref([]);

// 偏好洲别选项
const continentOptions = ["亚洲", "欧洲", "北美洲", "南美洲", "非洲", "大洋洲"];

const analysisDimensions = [
  { name: "旅游适宜", weight: "40%", description: "衡量目的地吸引力、签证便利、基础设施和旅游环境。" },
  { name: "安全指数", weight: "30%", description: "作为高安全需求下的核心筛选维度。" },
  { name: "幸福指数", weight: "15%", description: "作为社会环境和生活舒适度的辅助参考。" },
  { name: "消费友好", weight: "15%", description: "用于降低高成本目的地的推荐优先级。" },
];

// 推荐请求参数
const formData = reactive({
  budget_level: "medium",
  preferred_continent: "亚洲",
  safety_requirement: "high",
});

// 表单校验规则
const formRules = {
  budget_level: [
    {
      required: true,
      message: "请选择预算等级",
      trigger: "change",
    },
  ],
};

// 统一格式化数值显示
function formatDisplayNumber(value) {
  const numericValue = Number(value);
  if (Number.isNaN(numericValue)) {
    return "--";
  }
  return numericValue.toFixed(2);
}

// 提交推荐请求
async function handleSubmit() {
  await formRef.value?.validate();

  loading.value = true;

  try {
    // 当前后端使用固定权重算法，这里保留权重字段便于联调。
    const result = await getRecommendationApi({
      budget_level: formData.budget_level,
      preferred_continent: formData.preferred_continent,
      safety_requirement: formData.safety_requirement,
      safety_weight: 30,
      ppp_weight: 15,
      happiness_weight: 15,
    });

    resultList.value = result?.data?.results || [];

    if (resultList.value.length) {
      // 将推荐结果保存到本地存储，便于结果页和可视化页直接读取。
      setStorage("recommendation_result_payload", {
        year: result?.data?.year || "--",
        results: resultList.value,
      });

      ElMessage.success("推荐结果获取成功");
      router.push("/app/recommendation/result");
    } else {
      ElMessage.info("当前没有符合条件的推荐结果");
    }
  } catch (error) {
    // 错误提示交由 Axios 统一处理，这里保留日志方便排查。
    console.error("推荐请求失败：", error);
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.recommendation-page {
  display: grid;
  gap: 18px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  align-items: flex-start;
  padding: 26px;
  border: 1px solid rgba(16, 59, 70, 0.14);
  border-radius: 8px;
  background:
    linear-gradient(135deg, rgba(20, 92, 103, 0.08), transparent 38%),
    #fbfdfb;
  box-shadow: var(--shadow-panel);
}

.method-summary {
  min-width: 210px;
  padding: 16px;
  border: 1px solid var(--color-line);
  border-radius: 8px;
  background: #f4f8f6;
}

.method-summary span,
.dimension-strip span {
  color: var(--color-text-secondary);
  font-size: 12px;
  font-weight: 800;
}

.method-summary strong {
  display: block;
  margin: 8px 0 4px;
  color: var(--color-primary-dark);
  font-size: 20px;
}

.method-summary p {
  margin: 0;
  color: var(--color-text-secondary);
  font-size: 13px;
}

.page-tag {
  margin: 0 0 10px;
  color: var(--color-primary);
  text-transform: uppercase;
  letter-spacing: 0;
  font-size: 12px;
  font-weight: 900;
}

.page-header h2 {
  margin: 0 0 10px;
  color: var(--color-primary-dark);
  font-size: 32px;
}

.page-desc {
  margin: 0;
  max-width: 760px;
  color: #5f706b;
  line-height: 1.7;
}

.dimension-strip {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
}

.dimension-strip article {
  padding: 16px;
  border: 1px solid var(--color-line);
  border-radius: 8px;
  background: var(--color-panel);
  box-shadow: var(--shadow-panel);
}

.dimension-strip strong {
  display: block;
  margin: 8px 0;
  color: var(--color-primary);
  font-size: 24px;
}

.dimension-strip p {
  margin: 0;
  color: var(--color-text-secondary);
  font-size: 13px;
  line-height: 1.65;
}

.page-grid {
  display: grid;
  grid-template-columns: 390px 1fr;
  gap: 18px;
}

.form-panel,
.result-panel {
  padding: 22px;
  border: 1px solid rgba(16, 59, 70, 0.12);
  border-radius: 8px;
  background: var(--color-panel);
  box-shadow: var(--shadow-panel);
}

.form-panel h3,
.result-panel h3 {
  margin: 0 0 18px;
  color: #26453d;
}

.fixed-weight-panel {
  margin-bottom: 22px;
  padding: 18px;
  border-radius: 8px;
  background: #eef5f3;
  border: 1px solid rgba(16, 59, 70, 0.1);
}

.weight-title {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 16px;
}

.weight-title h4 {
  margin: 0 0 6px;
  color: #2b4b42;
  font-size: 16px;
}

.weight-title p {
  margin: 0;
  color: #70827c;
  line-height: 1.6;
  font-size: 13px;
}

.weight-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.weight-card {
  padding: 16px;
  border-radius: 8px;
  color: #1e3d36;
}

.weight-card span {
  display: block;
  margin-bottom: 8px;
  color: #55716a;
  font-size: 13px;
}

.weight-card strong {
  font-size: 28px;
}

.weight-card.tourism {
  background: #e5f3f1;
}

.weight-card.safety {
  background: #e8f7ef;
}

.weight-card.happiness {
  background: #fff6e2;
}

.weight-card.cost {
  background: #edf2f5;
}

.formula-box {
  margin-top: 14px;
  padding: 12px 14px;
  border-radius: 8px;
  background: #ffffff;
  color: #4c605b;
  line-height: 1.7;
  font-size: 14px;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 18px;
}

.result-header p {
  margin: 8px 0 0;
  color: #657570;
  line-height: 1.6;
}

.result-list {
  display: grid;
  gap: 16px;
}

.result-card {
  display: grid;
  grid-template-columns: 88px 1fr;
  gap: 16px;
  padding: 18px;
  border-radius: 8px;
  background: #f7fbfa;
  border: 1px solid rgba(16, 59, 70, 0.1);
}

.result-rank {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 72px;
  border-radius: 8px;
  background: linear-gradient(135deg, var(--color-primary-dark), var(--color-primary));
  color: #fff;
  font-weight: 700;
}

.result-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.result-top h4 {
  margin: 0;
  color: #294740;
  font-size: 20px;
}

.result-meta {
  margin: 10px 0 8px;
  color: #657570;
}

.metric-row {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin: 6px 0;
  color: #46625a;
  font-size: 14px;
}

.result-reason {
  margin: 10px 0 0;
  color: #435650;
  line-height: 1.7;
}

@media (max-width: 980px) {
  .page-header {
    flex-direction: column;
  }

  .dimension-strip {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .page-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .dimension-strip {
    grid-template-columns: 1fr;
  }

  .weight-grid,
  .result-card {
    grid-template-columns: 1fr;
  }

  .weight-title,
  .result-top {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>

