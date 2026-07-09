// 推荐模块接口封装
import request from "@/api/request";

// 提交推荐请求
export function getRecommendationApi(data) {
  return request({
    url: "/recommendation/generate/",
    method: "post",
    data,
  });
}

// 导出推荐结果 Excel
export function exportRecommendationExcelApi(data, config = {}) {
  return request({
    url: "/recommendation/export/",
    method: "post",
    data,
    responseType: "blob",
    timeout: 30000,
    ...config,
  });
}

// 获取单个国家 AI 推荐说明
export function getRecommendationExplanationApi(countryId, config = {}) {
  return request({
    url: `/recommendation/explanation/${countryId}/`,
    method: "get",
    timeout: 30000,
    ...config,
  });
}
