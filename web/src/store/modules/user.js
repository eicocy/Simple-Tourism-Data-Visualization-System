// 用户状态管理
import { defineStore } from "pinia";

import { getStorage, removeStorage, setStorage } from "@/utils/storage";

const USER_STORAGE_KEY = "current_user_info";
const ACCESS_TOKEN_STORAGE_KEY = "access_token";
const REFRESH_TOKEN_STORAGE_KEY = "refresh_token";

export const useUserStore = defineStore("user", {
  state: () => ({
    // 当前登录用户信息，默认先从本地缓存恢复
    userInfo: getStorage(USER_STORAGE_KEY),
    // JWT Access Token，用于后续接口认证
    token: getStorage(ACCESS_TOKEN_STORAGE_KEY),
    refreshToken: getStorage(REFRESH_TOKEN_STORAGE_KEY),
    // 标记是否已完成一次登录状态初始化
    initialized: false,
  }),
  getters: {
    // 是否已登录
    isAuthenticated: (state) => Boolean(state.userInfo?.id),
    // 是否为管理员
    isAdmin: (state) =>
      state.userInfo?.role === "admin" ||
      Boolean(state.userInfo?.is_staff || state.userInfo?.is_superuser),
    isNormalUser: (state) => state.userInfo?.role === "user" && !state.userInfo?.is_staff,
    // 页面展示名，优先昵称，其次用户名
    displayName: (state) => state.userInfo?.profile?.nickname || state.userInfo?.username || "未登录",
  },
  actions: {
    // 设置用户信息并同步到本地缓存
    setUserInfo(userInfo) {
      this.userInfo = userInfo;
      this.initialized = true;
      setStorage(USER_STORAGE_KEY, userInfo);
    },
    // 设置后端认证 Token
    setToken(accessToken, refreshToken = this.refreshToken) {
      this.token = accessToken;
      this.refreshToken = refreshToken;
      setStorage(ACCESS_TOKEN_STORAGE_KEY, accessToken);
      if (refreshToken) {
        setStorage(REFRESH_TOKEN_STORAGE_KEY, refreshToken);
      }
    },
    // 登录成功时同时保存用户信息与 Token
    setAuthPayload(payload) {
      this.setToken(payload?.access || payload?.token || "", payload?.refresh || "");
      this.setUserInfo(payload?.user || payload);
    },
    // 从本地缓存恢复用户信息
    hydrateUserInfo() {
      this.userInfo = getStorage(USER_STORAGE_KEY);
      this.token = getStorage(ACCESS_TOKEN_STORAGE_KEY);
      this.refreshToken = getStorage(REFRESH_TOKEN_STORAGE_KEY);
      return this.userInfo;
    },
    // 标记登录状态初始化完成
    markInitialized() {
      this.initialized = true;
    },
    // 清空用户信息与缓存
    clearUserInfo() {
      this.userInfo = null;
      this.token = null;
      this.refreshToken = null;
      this.initialized = true;
      removeStorage(USER_STORAGE_KEY);
      removeStorage(ACCESS_TOKEN_STORAGE_KEY);
      removeStorage(REFRESH_TOKEN_STORAGE_KEY);
      removeStorage("auth_token");
    },
  },
});
