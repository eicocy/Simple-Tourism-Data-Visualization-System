// 用户模块接口封装
import request from "@/api/request";

// 获取 CSRF Cookie 接口
export function fetchCsrfTokenApi(config = {}) {
  return request({
    url: "/users/csrf/",
    method: "get",
    ...config,
  });
}

// 用户登录接口
export function loginApi(data, config = {}) {
  return request({
    url: "/users/login/",
    method: "post",
    data,
    ...config,
  });
}

// 用户注册接口
export function registerApi(data, config = {}) {
  return request({
    url: "/users/register/",
    method: "post",
    data,
    ...config,
  });
}

// 获取当前登录用户信息接口
export function getCurrentUserApi(config = {}) {
  return request({
    url: "/users/me/",
    method: "get",
    ...config,
  });
}

// 用户退出接口
export function logoutApi(config = {}) {
  return request({
    url: "/users/logout/",
    method: "post",
    ...config,
  });
}

// 当前用户资料更新接口
export function updateProfileApi(data, config = {}) {
  return request({
    url: "/users/profile/",
    method: "patch",
    data,
    ...config,
  });
}

// 当前用户修改密码接口
export function changePasswordApi(data, config = {}) {
  return request({
    url: "/users/change-password/",
    method: "post",
    data,
    ...config,
  });
}

// 管理员概览接口
export function getAdminSummaryApi(config = {}) {
  return request({
    url: "/users/admin/summary/",
    method: "get",
    ...config,
  });
}

// 管理员用户列表接口
export function getAdminUsersApi(params = {}, config = {}) {
  return request({
    url: "/users/admin/users/",
    method: "get",
    params,
    ...config,
  });
}

// 管理员更新用户状态接口
export function updateAdminUserApi(userId, data, config = {}) {
  return request({
    url: `/users/admin/users/${userId}/`,
    method: "patch",
    data,
    ...config,
  });
}
