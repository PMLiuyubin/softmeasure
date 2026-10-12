<script setup lang="ts">
import { onMounted, ref } from "vue";
import { fetchSeries } from "../api/http";
import type { SeriesRow } from "../types/api";
import LineChart from "../components/LineChart.vue";

const rows = ref<SeriesRow[]>([]);
const note = ref("曲线数值来自后端验收窗接口，页面不做含量计算。");

onMounted(async () => {
  const body = await fetchSeries();
  rows.value = body.rows;
  note.value = "15 分钟画图，共 " + body.n + " 点。验收计分仍是五分钟 2878 点。";
});
</script>

<template>
  <el-alert :title="note" type="info" show-icon :closable="false" />
  <LineChart :rows="rows" />
</template>
