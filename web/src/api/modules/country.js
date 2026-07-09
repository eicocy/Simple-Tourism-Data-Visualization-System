// 国家模块接口封装
import request from "@/api/request";

// 查询国家列表
export function getCountryListApi(params) {
  return request({
    url: "/countries/",
    method: "get",
    params,
  });
}

// 查询国家详情
export function getCountryDetailApi(id) {
  return request({
    url: `/countries/${id}/`,
    method: "get",
  });
}

// 查询国家指标数据
export function getCountryIndicatorListApi(params) {
  return request({
    url: "/countries/indicators/",
    method: "get",
    params,
  });
}

// 上传 Excel 批量导入国家指标数据
export function uploadCountryIndicatorExcelApi(file, payload = {}, config = {}) {
  const formData = new FormData();
  formData.append("file", file);
  if (payload.year) {
    formData.append("year", payload.year);
  }

  return request({
    url: "/countries/indicators/import-excel/",
    method: "post",
    data: formData,
    timeout: 30000,
    ...config,
  });
}

// 查询首页世界地图所需的最新国家指标数据
export function getCountryMapDataApi() {
  return request({
    url: "/countries/map-data/",
    method: "get",
  });
}

// 查询按洲别统计的国家指标数据
export function getCountryContinentStatsApi() {
  return request({
    url: "/countries/continent-stats/",
    method: "get",
  });
}

// 查询国家洞察详情
export function getCountryInsightDetailApi(id) {
  return request({
    url: `/countries/${id}/insight/`,
    method: "get",
  });
}
