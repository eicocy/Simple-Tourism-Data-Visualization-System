// Vite 基础配置文件
import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import path from "path";

export default defineConfig({
  plugins: [vue()],
  resolve: {
    // 配置路径别名，便于后续统一使用 @ 指向 src 目录
    alias: {
      "@": path.resolve(__dirname, "src"),
    },
  },
  server: {
    // 指定本地开发端口，便于与 Django 后端联调
    port: 5173,
    host: "0.0.0.0",
  },
});
