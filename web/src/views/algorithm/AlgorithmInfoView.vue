<template>
  <div class="algorithm-page">
    <!-- 页面头部：面向毕设论文和答辩说明算法思路 -->
    <section class="page-hero">
      <div>
        <p class="hero-tag">Algorithm Design</p>
        <h2>推荐算法与指标来源说明</h2>
        <p class="hero-desc">
          本页面整理系统的推荐公式、旅游适宜指数计算方法、预算与安全需求匹配策略和数据来源，便于在毕业论文和答辩演示中说明系统设计依据。
        </p>
      </div>
      <el-button type="primary" @click="router.push('/app/recommendation')">
        返回推荐页
      </el-button>
    </section>

    <!-- 最终推荐模型说明 -->
    <section class="panel">
      <div class="panel-header">
        <h3>综合推荐指数模型</h3>
        <p>系统采用加权评分模型，将旅游适宜、安全、幸福和消费水平综合为最终推荐指数。</p>
      </div>

      <div class="formula-card">
        <span>Score = 0.40 × T + 0.30 × S + 0.15 × H + 0.15 × C'</span>
      </div>

      <el-table :data="recommendationFactors" border stripe style="width: 100%">
        <el-table-column prop="symbol" label="符号" width="110" align="center" />
        <el-table-column prop="name" label="指标名称" width="170" />
        <el-table-column prop="weight" label="权重" width="110" align="center" />
        <el-table-column prop="description" label="说明" />
      </el-table>
    </section>

    <!-- 旅游适宜指数说明 -->
    <section class="panel">
      <div class="panel-header">
        <h3>旅游适宜指数模型</h3>
        <p>旅游适宜指数用于区分“安全但不一定适合旅游”的国家，使推荐结果更贴近旅游场景。</p>
      </div>

      <div class="formula-card accent">
        <span>T = 0.40 × A + 0.30 × V + 0.20 × I + 0.10 × E</span>
      </div>

      <section class="factor-grid">
        <article v-for="item in tourismFactors" :key="item.symbol" class="factor-card">
          <p>{{ item.symbol }}</p>
          <h4>{{ item.name }}</h4>
          <strong>{{ item.weight }}</strong>
          <span>{{ item.description }}</span>
        </article>
      </section>
    </section>

    <!-- 预算过滤说明 -->
    <section class="panel">
      <div class="panel-header">
        <h3>预算与安全需求匹配策略</h3>
        <p>推荐接口会根据用户预算等级、偏好洲别和安全需求处理候选国家，对消费或安全条件不完全匹配的国家进行降权排序。</p>
      </div>

      <el-steps :active="3" finish-status="success" align-center>
        <el-step title="接收预算与安全需求" description="预算等级、安全需求、偏好洲别" />
        <el-step title="匹配消费与安全指数" description="根据消费指数和安全指数判断候选国家适配程度" />
        <el-step title="综合排序" description="预算或安全需求不匹配时降低最终推荐得分" />
      </el-steps>
    </section>

    <!-- 数据来源说明 -->
    <section class="panel">
      <div class="panel-header">
        <h3>数据来源与字段对应</h3>
        <p>当前系统数据来自导入的 Excel 文件与后端模型字段，便于论文中说明数据采集与预处理过程。</p>
      </div>

      <el-table :data="dataSources" border stripe style="width: 100%">
        <el-table-column prop="field" label="数据库字段" width="190" />
        <el-table-column prop="source" label="数据来源" width="280" />
        <el-table-column prop="usage" label="用途说明" />
      </el-table>
    </section>
  </div>
</template>

<script setup>
// 算法说明页面：主要用于展示论文可写入的推荐模型说明
import { useRouter } from "vue-router";

const router = useRouter();

// 综合推荐指数中的各项权重
const recommendationFactors = [
  {
    symbol: "T",
    name: "旅游适宜指数",
    weight: "40%",
    description: "衡量国家是否适合作为旅游目的地，是综合推荐中的核心指标。",
  },
  {
    symbol: "S",
    name: "安全指数",
    weight: "30%",
    description: "反映旅游国家公共安全水平，安全性越高越适合推荐。",
  },
  {
    symbol: "H",
    name: "幸福指数",
    weight: "15%",
    description: "反映国家社会生活质量和整体幸福水平，作为旅游体验的辅助指标。",
  },
  {
    symbol: "C'",
    name: "消费友好度",
    weight: "15%",
    description: "由消费指数转换得到，消费压力越低，消费友好度越高。",
  },
];

// 旅游适宜指数内部维度
const tourismFactors = [
  {
    symbol: "A",
    name: "旅游吸引力",
    weight: "40%",
    description: "根据签证便利、经济水平和安全水平综合估算目的地吸引力。",
  },
  {
    symbol: "V",
    name: "签证便利度",
    weight: "30%",
    description: "来自中国护照签证评分，反映中国游客前往该国的便利程度。",
  },
  {
    symbol: "I",
    name: "基础设施代理分",
    weight: "20%",
    description: "使用经济水平和消费相关指标近似表示旅游基础设施成熟度。",
  },
  {
    symbol: "E",
    name: "旅游环境分",
    weight: "10%",
    description: "结合安全指数和幸福指数，表示当地旅游环境与体验稳定性。",
  },
];

// 数据来源说明，用于论文数据库设计和数据预处理章节
const dataSources = [
  {
    field: "safety_index",
    source: "global_safety_full_144.xlsx",
    usage: "作为公共安全水平指标，参与推荐指数和旅游环境计算。",
  },
  {
    field: "overall_score",
    source: "2024_happiness_minmax_normalized.xlsx",
    usage: "作为幸福指数，反映目的地社会生活质量和旅游体验辅助因素。",
  },
  {
    field: "cost_index",
    source: "latest_gdp_per_capita.xlsx",
    usage: "用于估算消费水平和基础设施代理分，并参与预算过滤。",
  },
  {
    field: "visa_index",
    source: "china_passport_visa_score_144.xlsx",
    usage: "用于衡量中国游客前往各国的签证便利程度。",
  },
  {
    field: "tourism_index",
    source: "系统算法计算生成",
    usage: "综合旅游吸引力、签证便利度、基础设施和旅游环境后得到。",
  },
];
</script>

<style scoped>
.algorithm-page {
  display: grid;
  gap: 20px;
}

.page-hero,
.panel {
  padding: 24px;
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
.panel-header p,
.factor-card span {
  margin: 0;
  color: #647587;
  line-height: 1.7;
}

.panel-header {
  margin-bottom: 18px;
}

.panel-header h3 {
  margin: 0 0 8px;
  color: #1f3347;
  font-size: 20px;
}

.formula-card {
  margin-bottom: 18px;
  padding: 18px 22px;
  border-radius: 16px;
  background: linear-gradient(135deg, #e9f3ff, #f7fbff);
  color: #164b8f;
  font-size: 24px;
  font-weight: 700;
  text-align: center;
}

.formula-card.accent {
  background: linear-gradient(135deg, #eef8ef, #fbfff8);
  color: #246047;
}

.factor-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
}

.factor-card {
  padding: 18px;
  border-radius: 16px;
  background: #f7fbff;
  border: 1px solid #dfe7ef;
}

.factor-card p {
  margin: 0 0 10px;
  color: #2f72c8;
  font-size: 28px;
  font-weight: 800;
}

.factor-card h4 {
  margin: 0 0 8px;
  color: #1f3347;
}

.factor-card strong {
  display: block;
  margin-bottom: 8px;
  color: #246047;
  font-size: 20px;
}

@media (max-width: 980px) {
  .page-hero {
    flex-direction: column;
    align-items: flex-start;
  }

  .factor-grid {
    grid-template-columns: 1fr;
  }
}
</style>
