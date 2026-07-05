// 项目常量定义文件

// 预算等级选项，后续推荐表单可直接复用
export const BUDGET_LEVEL_OPTIONS = [
  { label: "低预算", value: "low" },
  { label: "中等预算", value: "medium" },
  { label: "高预算", value: "high" },
];

// 安全需求选项，用于推荐表单和后端安全匹配逻辑
export const SAFETY_REQUIREMENT_OPTIONS = [
  { label: "一般安全需求", value: "normal" },
  { label: "较高安全需求", value: "high" },
  { label: "高安全需求", value: "strict" },
];
