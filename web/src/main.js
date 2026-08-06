// Vue 应用入口文件
import { createApp } from "vue";
import { createPinia } from "pinia";

import App from "./App.vue";
import router from "./router";
import "@/styles/index.css";

// 创建 Vue 应用实例
const app = createApp(App);

// 注册 Pinia 状态管理
app.use(createPinia());

// 注册路由
app.use(router);


// 挂载应用
app.mount("#app");
