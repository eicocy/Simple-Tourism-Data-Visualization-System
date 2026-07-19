// 可视化模块接口封装
import request from "@/api/request";

// 智能地图问答助手
export function chatWithMapAgentApi(data, config = {}) {
  return request({
    url: "/visualization/agent/chat/",
    method: "post",
    data,
    timeout: 30000,
    ...config,
  });
}
