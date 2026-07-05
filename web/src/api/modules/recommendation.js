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
