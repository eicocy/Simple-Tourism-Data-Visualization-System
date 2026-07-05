// 应用级状态管理
import { defineStore } from "pinia";

export const useAppStore = defineStore("app", {
  state: () => ({
    // 当前系统名称
    systemName: "安全旅游国家推荐与可视化系统",
    // 侧边栏是否折叠，后续可扩展为响应式布局控制
    sidebarCollapsed: false,
  }),
  actions: {
    // 切换侧边栏展开状态
    toggleSidebar() {
      this.sidebarCollapsed = !this.sidebarCollapsed;
    },
  },
});
