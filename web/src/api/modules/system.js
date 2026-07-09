// 系统管理模块接口封装
import request from "@/api/request";

// 查询后台操作日志列表
export function getOperationLogListApi(params = {}, config = {}) {
  return request({
    url: "/system/operation-logs/",
    method: "get",
    params,
    ...config,
  });
}
