// Axios 请求封装文件
import axios from "axios";
import { ElMessage } from "element-plus";

import { getStorage, removeStorage, setStorage } from "@/utils/storage";

const ACCESS_TOKEN_STORAGE_KEY = "access_token";
const REFRESH_TOKEN_STORAGE_KEY = "refresh_token";

// 获取浏览器 Cookie 的工具函数
function getCookie(name) {
  const cookieValue = document.cookie
    .split("; ")
    .find((item) => item.startsWith(`${name}=`));
  return cookieValue ? decodeURIComponent(cookieValue.split("=")[1]) : "";
}

// 创建 Axios 实例
const request = axios.create({
  // 从环境变量中读取后端接口根地址
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 10000,
  withCredentials: true,
  headers: {
    "Content-Type": "application/json",
  },
});

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    if (typeof FormData !== "undefined" && config.data instanceof FormData) {
      if (typeof config.headers?.delete === "function") {
        config.headers.delete("Content-Type");
      } else {
        delete config.headers["Content-Type"];
      }
    }

    // 自动携带 CSRF Token，便于 Session 登录与受保护写操作正常提交
    const csrfToken = getCookie("csrftoken");
    if (csrfToken) {
      config.headers["X-CSRFToken"] = csrfToken;
    }
    const authToken = getStorage(ACCESS_TOKEN_STORAGE_KEY) || getStorage("auth_token");
    if (authToken) {
      config.headers.Authorization = `Bearer ${authToken}`;
    }
    return config;
  },
  (error) => Promise.reject(error),
);

// 响应拦截器
request.interceptors.response.use(
  (response) => {
    // 后端统一返回结构时，直接返回 data 部分
    return response.data;
  },
  (error) => {
    const silentError = error?.config?.silentError;
    const statusCode = error?.response?.status;
    const responseData = error?.response?.data || {};
    const originalRequest = error?.config || {};

    if (statusCode === 401 && !originalRequest._retry) {
      const refreshToken = getStorage(REFRESH_TOKEN_STORAGE_KEY);
      if (refreshToken) {
        originalRequest._retry = true;
        return axios
          .post(
            `${import.meta.env.VITE_API_BASE_URL}/users/token/refresh/`,
            { refresh: refreshToken },
            { headers: { "Content-Type": "application/json" } },
          )
          .then((refreshResponse) => {
            const accessToken = refreshResponse.data?.data?.access;
            if (accessToken) {
              setStorage(ACCESS_TOKEN_STORAGE_KEY, accessToken);
              originalRequest.headers.Authorization = `Bearer ${accessToken}`;
              return request(originalRequest);
            }
            return Promise.reject(error);
          })
          .catch(() => {
            removeStorage("current_user_info");
            removeStorage(ACCESS_TOKEN_STORAGE_KEY);
            removeStorage(REFRESH_TOKEN_STORAGE_KEY);
            removeStorage("auth_token");
            return Promise.reject(error);
          });
      }
    }

    // 尽量提取后端返回的真实错误信息
    const errorMessage =
      responseData.message ||
      responseData.detail ||
      responseData.non_field_errors?.[0] ||
      responseData.username?.[0] ||
      responseData.password?.[0] ||
      "请求失败，请稍后重试";

    // 未提供身份认证信息时，说明后端 Session 已失效，需要清理本地缓存
    if (
      statusCode === 401 ||
      responseData.detail === "身份认证信息未提供。" ||
      responseData.detail === "Authentication credentials were not provided."
    ) {
      removeStorage("current_user_info");
      removeStorage(ACCESS_TOKEN_STORAGE_KEY);
      removeStorage(REFRESH_TOKEN_STORAGE_KEY);
      removeStorage("auth_token");
    }

    if (!silentError) {
      ElMessage.error(errorMessage);
    }

    return Promise.reject(error);
  },
);

export default request;
