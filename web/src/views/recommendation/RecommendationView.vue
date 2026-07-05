<template>
  <div class="recommendation-page">
    <!-- 页面头部说明 -->
    <section class="page-header">
      <div>
        <p class="page-tag">Recommendation</p>
        <h2>旅游国家推荐</h2>
        <p class="page-desc">
          本页用于提交预算等级、偏好洲别与安全需求，系统将基于固定推荐模型生成旅游国家排序结果。
          当前算法已引入旅游适宜指数，用于更好地区分适合旅游的目的地国家。
        </p>
      </div>
    </section>

    <div class="page-grid">
      <!-- 左侧推荐条件输入区域 -->
      <section class="form-panel">
        <h3>推荐条件输入</h3>

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
                <h4>当前推荐算法固定权重</h4>
                <p>为保证推荐逻辑稳定，系统当前不再手动调整权重。</p>
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
              获取推荐结果
            </el-button>
          </el-form-item>
        </el-form>
      </section>

      <!-- 右侧推荐结果预览区域 -->
      <section class="result-panel">
        <div class="result-header">
          <div>
            <h3>推荐结果预览</h3>
            <p>提交后将优先跳转到结果页，同时这里也会显示最新一次推荐结果摘要。</p>
          </div>
          <el-tag v-if="resultList.length" type="success">
            共 {{ resultList.length }} 条
          </el-tag>
        </div>

        <el-empty
          v-if="!resultList.length"
          description="请先填写条件并点击获取推荐结果"
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
                所属洲别：{{ item.continent || "--" }} ｜ 综合得分：{{ item.score }}
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
// 旅游推荐输入页逻辑
import { reactive, ref } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";

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

// 推荐表单数据
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
    // 当前后端已使用固定权重算法，这里保留兼容字段用于平稳联调
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
      // 将推荐结果缓存到本地存储，便于结果页与可视化页直接读取
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
    // 错误提示已由 Axios 统一处理，这里保留日志方便排查
    console.error("推荐请求失败：", error);
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.recommendation-page {
  display: grid;
  gap: 20px;
}

.page-header {
  padding: 28px;
  border-radius: 24px;
  background: linear-gradient(135deg, #f3ede0 0%, #fffaf1 100%);
  box-shadow: 0 16px 40px rgba(43, 58, 52, 0.08);
}

.page-tag {
  margin: 0 0 10px;
  color: #8a6a2f;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  font-size: 12px;
}

.page-header h2 {
  margin: 0 0 10px;
  color: #25413a;
  font-size: 30px;
}

.page-desc {
  margin: 0;
  max-width: 760px;
  color: #5f706b;
  line-height: 1.7;
}

.page-grid {
  display: grid;
  grid-template-columns: 420px 1fr;
  gap: 20px;
}

.form-panel,
.result-panel {
  padding: 24px;
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.9);
  box-shadow: 0 12px 32px rgba(24, 43, 38, 0.08);
}

.form-panel h3,
.result-panel h3 {
  margin: 0 0 18px;
  color: #26453d;
}

.fixed-weight-panel {
  margin-bottom: 22px;
  padding: 18px;
  border-radius: 18px;
  background: linear-gradient(135deg, #f7faf9 0%, #eef5f2 100%);
  border: 1px solid rgba(47, 107, 90, 0.08);
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
  border-radius: 16px;
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
  background: #edf7ff;
}

.weight-card.safety {
  background: #eef8f3;
}

.weight-card.happiness {
  background: #fff7ea;
}

.weight-card.cost {
  background: #f5f2ff;
}

.formula-box {
  margin-top: 14px;
  padding: 12px 14px;
  border-radius: 12px;
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
  border-radius: 18px;
  background: linear-gradient(135deg, #fafcf9 0%, #f4f7f2 100%);
  border: 1px solid rgba(47, 107, 90, 0.08);
}

.result-rank {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 72px;
  border-radius: 16px;
  background: linear-gradient(135deg, #2f6b5a 0%, #4a8775 100%);
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
  .page-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
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

