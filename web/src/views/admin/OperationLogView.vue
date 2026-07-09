<template>
  <div class="log-page">
    <section class="log-header">
      <div>
        <p class="header-tag">Audit Log</p>
        <h2>操作日志</h2>
      </div>
      <el-button type="primary" :icon="Refresh" :loading="loading" @click="loadLogs">
        刷新
      </el-button>
    </section>

    <section class="filter-panel">
      <el-form :model="filterForm" class="filter-form" label-width="76px">
        <el-form-item label="用户名">
          <el-input
            v-model="filterForm.username"
            clearable
            placeholder="输入用户名"
            @keyup.enter="handleSearch"
          />
        </el-form-item>

        <el-form-item label="操作类型">
          <el-select
            v-model="filterForm.operation_type"
            clearable
            placeholder="全部类型"
          >
            <el-option
              v-for="item in operationTypeOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="时间">
          <el-date-picker
            v-model="filterForm.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>

        <div class="filter-actions">
          <el-button type="primary" :icon="Search" @click="handleSearch">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </div>
      </el-form>
    </section>

    <section class="table-panel">
      <div class="table-header">
        <h3>日志列表</h3>
        <el-tag type="info">共 {{ pagination.total }} 条</el-tag>
      </div>

      <el-table
        :data="logRows"
        border
        stripe
        v-loading="loading"
        empty-text="暂无操作日志"
        style="width: 100%"
      >
        <el-table-column prop="username" label="操作用户" min-width="130" />
        <el-table-column prop="operation_type_display" label="操作类型" min-width="140">
          <template #default="scope">
            <el-tag :type="getOperationTagType(scope.row.operation_type)">
              {{ scope.row.operation_type_display || scope.row.operation_type }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column
          prop="operation_object"
          label="操作对象"
          min-width="180"
          show-overflow-tooltip
        />
        <el-table-column prop="created_at" label="操作时间" min-width="180">
          <template #default="scope">
            {{ formatDate(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="ip_address" label="IP 地址" min-width="140">
          <template #default="scope">
            {{ scope.row.ip_address || "--" }}
          </template>
        </el-table-column>
        <el-table-column prop="operation_result_display" label="操作结果" min-width="110" align="center">
          <template #default="scope">
            <el-tag :type="scope.row.operation_result === 'success' ? 'success' : 'danger'">
              {{ scope.row.operation_result_display || scope.row.operation_result }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="detail" label="详情" min-width="260" show-overflow-tooltip>
          <template #default="scope">
            {{ scope.row.detail || "--" }}
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-row">
        <el-pagination
          background
          layout="total, prev, pager, next"
          :current-page="pagination.page"
          :page-size="pagination.pageSize"
          :total="pagination.total"
          @current-change="handlePageChange"
        />
      </div>
    </section>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from "vue";
import { Refresh, Search } from "@element-plus/icons-vue";
import { ElMessage } from "element-plus";

import { getOperationLogListApi } from "@/api";

const loading = ref(false);
const logRows = ref([]);

const filterForm = reactive({
  username: "",
  operation_type: "",
  dateRange: [],
});

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0,
});

const operationTypeOptions = [
  { label: "管理员登录", value: "admin_login" },
  { label: "添加国家数据", value: "country_create" },
  { label: "修改国家数据", value: "country_update" },
  { label: "删除国家数据", value: "country_delete" },
  { label: "导入 Excel", value: "excel_import" },
  { label: "导出 Excel", value: "excel_export" },
];

function buildQueryParams() {
  const params = {
    page: pagination.page,
  };

  if (filterForm.username.trim()) {
    params.username = filterForm.username.trim();
  }
  if (filterForm.operation_type) {
    params.operation_type = filterForm.operation_type;
  }
  if (filterForm.dateRange?.length === 2) {
    params.start_date = filterForm.dateRange[0];
    params.end_date = filterForm.dateRange[1];
  }

  return params;
}

function formatDate(value) {
  if (!value) {
    return "--";
  }
  return new Date(value).toLocaleString("zh-CN", { hour12: false });
}

function getOperationTagType(operationType) {
  const typeMap = {
    admin_login: "warning",
    country_create: "success",
    country_update: "primary",
    country_delete: "danger",
    excel_import: "info",
    excel_export: "",
  };
  return typeMap[operationType] || "";
}

async function loadLogs() {
  loading.value = true;
  try {
    const result = await getOperationLogListApi(buildQueryParams(), { silentError: true });
    const payload = result.data || {};
    logRows.value = payload.results || [];
    pagination.total = payload.count || 0;
  } catch (error) {
    ElMessage.error("操作日志加载失败，请检查后端服务或管理员权限");
  } finally {
    loading.value = false;
  }
}

function handleSearch() {
  pagination.page = 1;
  loadLogs();
}

function handleReset() {
  filterForm.username = "";
  filterForm.operation_type = "";
  filterForm.dateRange = [];
  pagination.page = 1;
  loadLogs();
}

function handlePageChange(page) {
  pagination.page = page;
  loadLogs();
}

onMounted(() => {
  loadLogs();
});
</script>

<style scoped>
.log-page {
  display: grid;
  gap: 18px;
}

.log-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 24px 26px;
  border-radius: 16px;
  background: linear-gradient(135deg, #244f47 0%, #587a6f 100%);
  color: #ffffff;
  box-shadow: 0 14px 34px rgba(35, 72, 64, 0.16);
}

.header-tag {
  margin: 0 0 8px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 12px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.log-header h2,
.table-header h3 {
  margin: 0;
}

.filter-panel,
.table-panel {
  padding: 20px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.94);
  box-shadow: 0 12px 30px rgba(31, 64, 55, 0.08);
}

.filter-form {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 4px 14px;
}

.filter-form :deep(.el-form-item) {
  margin-bottom: 0;
}

.filter-form :deep(.el-input),
.filter-form :deep(.el-select) {
  width: 220px;
}

.filter-form :deep(.el-date-editor) {
  width: 320px;
}

.filter-actions {
  display: flex;
  gap: 10px;
}

.table-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.pagination-row {
  display: flex;
  justify-content: flex-end;
  margin-top: 18px;
}

@media (max-width: 900px) {
  .log-header,
  .table-header {
    align-items: flex-start;
    flex-direction: column;
  }

  .filter-form,
  .filter-actions {
    width: 100%;
  }

  .filter-form :deep(.el-form-item),
  .filter-form :deep(.el-input),
  .filter-form :deep(.el-select),
  .filter-form :deep(.el-date-editor) {
    width: 100%;
  }
}
</style>
