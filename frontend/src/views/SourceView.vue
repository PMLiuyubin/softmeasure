<script setup lang="ts">
import { onMounted, ref } from "vue";
import { fetchSources } from "../api/http";

const body = ref<{ ready?: boolean; total?: number; loaded?: number; items?: Record<string, unknown>[]; note?: string }>({});
onMounted(async () => {
  body.value = await fetchSources();
});
</script>

<template>
  <el-alert v-if="!body.ready" :title="body.note || '资料库尚未生成'" type="warning" show-icon :closable="false" />
  <p v-else>已登记 {{ body.total }} 个文件，其中 {{ body.loaded }} 个已写入表。</p>
  <el-table v-if="body.items" :data="body.items" border>
    <el-table-column prop="relpath" label="资料相对路径" />
    <el-table-column prop="suffix" label="类型" width="90" />
    <el-table-column prop="bytes" label="字节" width="120" />
    <el-table-column prop="n_rows" label="行数" width="100" />
    <el-table-column prop="status" label="状态" width="100" />
  </el-table>
</template>
