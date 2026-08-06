import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import tailwindcss from "@tailwindcss/vite";
import AutoImport from "unplugin-auto-import/vite";
import Components from "unplugin-vue-components/vite";
import { ElementPlusResolver } from "unplugin-vue-components/resolvers";
import path from "path";

const elementPlusResolver = ElementPlusResolver({
  importStyle: "css",
  directives: true,
});

export default defineConfig(async ({ mode }) => {
  const analyzePlugin =
    mode === "analyze"
      ? (await import("rollup-plugin-visualizer")).visualizer({
          filename: "dist/bundle-stats.html",
          gzipSize: true,
          brotliSize: true,
          open: false,
        })
      : null;

  return {
    plugins: [
      vue(),
      tailwindcss(),
      AutoImport({
        dts: false,
        resolvers: [elementPlusResolver],
      }),
      Components({
        dts: false,
        resolvers: [elementPlusResolver],
      }),
      analyzePlugin,
    ].filter(Boolean),
    resolve: {
      alias: {
        "@": path.resolve(__dirname, "src"),
      },
    },
    server: {
      port: 5173,
      host: "0.0.0.0",
    },
    build: {
      rollupOptions: {
        output: {
          manualChunks(id) {
            if (!id.includes("node_modules")) {
              return undefined;
            }

            const normalizedId = id.replace(/\\/g, "/");

            if (/[\\/]node_modules[\\/](vue|vue-router|pinia)[\\/]/.test(id)) {
              return "vue-vendor";
            }

            if (normalizedId.includes("/node_modules/zrender/")) {
              return "zrender-vendor";
            }

            if (normalizedId.includes("/node_modules/echarts/")) {
              if (
                normalizedId.includes("/echarts/lib/chart/") ||
                normalizedId.includes("/echarts/charts")
              ) {
                return "echarts-charts";
              }

              if (
                normalizedId.includes("/echarts/lib/component/") ||
                normalizedId.includes("/echarts/components")
              ) {
                return "echarts-components";
              }

              return "echarts-core";
            }

            if (/[\\/]node_modules[\\/]axios[\\/]/.test(id)) {
              return "network-vendor";
            }

            return undefined;
          },
        },
      },
    },
  };
});
