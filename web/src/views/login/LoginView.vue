<template>
  <div class="login-page">
    <div class="login-card">
      <div class="card-header">
        <h2>用户登录</h2>
        <p>请输入用户名和密码，登录安全旅游国家推荐与可视化系统。</p>
      </div>

      <!-- 登录表单 -->
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-position="top"
        @keyup.enter="handleLogin"
      >
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="formData.username"
            placeholder="请输入用户名"
            clearable
          />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="formData.password"
            type="password"
            placeholder="请输入密码"
            show-password
            clearable
          />
        </el-form-item>
        <el-form-item>
          <el-button
            type="primary"
            :loading="loading"
            style="width: 100%"
            @click="handleLogin"
          >
            登录
          </el-button>
        </el-form-item>
      </el-form>

      <!-- 演示账号提示 -->
      <div class="login-tip">
        <span>演示管理员账号：admin</span>
        <span>演示密码：lll190</span>
      </div>
    </div>
  </div>
</template>

<script setup>
// 登录页组件逻辑
import { reactive, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage } from "element-plus";

import { fetchCsrfTokenApi, loginApi } from "@/api";
import { useUserStore } from "@/store";

// 路由实例，用于登录成功后跳转首页
const route = useRoute();
const router = useRouter();

// 用户状态管理实例
const userStore = useUserStore();

// 表单引用，用于触发表单校验
const formRef = ref(null);

// 登录加载状态
const loading = ref(false);

// 登录表单数据
const formData = reactive({
  username: "admin",
  password: "lll190",
});

// 登录表单校验规则
const formRules = {
  username: [
    {
      required: true,
      message: "请输入用户名",
      trigger: "blur",
    },
  ],
  password: [
    {
      required: true,
      message: "请输入密码",
      trigger: "blur",
    },
  ],
};

// 处理登录逻辑
async function handleLogin() {
  await formRef.value?.validate();
  loading.value = true;

  try {
    await fetchCsrfTokenApi({ silentError: true });
    const result = await loginApi(formData);
    userStore.setAuthPayload(result.data);
    ElMessage.success(result.message || "登录成功");

    const redirectPath = route.query.redirect;
    if (typeof redirectPath === "string" && redirectPath) {
      router.push(redirectPath);
      return;
    }

    router.push(userStore.isAdmin ? "/app/admin" : "/app/recommendation");
  } catch (error) {
    if (!error?.response) {
      ElMessage.error("无法连接后端服务，请检查 Django 服务是否已启动");
    }
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  background:
    linear-gradient(135deg, rgba(31, 64, 55, 0.92), rgba(107, 144, 128, 0.86)),
    linear-gradient(45deg, rgba(217, 175, 107, 0.15), transparent);
}

.login-card {
  width: 100%;
  max-width: 420px;
  padding: 32px;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.96);
  box-shadow: 0 18px 48px rgba(18, 31, 27, 0.18);
}

.card-header h2 {
  margin: 0 0 10px;
  color: #1f4037;
}

.card-header p {
  margin: 0 0 24px;
  color: #62736d;
  line-height: 1.6;
}

.login-tip {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  margin-top: 8px;
  color: #6f7d78;
  font-size: 13px;
}

@media (max-width: 520px) {
  .login-tip {
    flex-direction: column;
  }
}
</style>
