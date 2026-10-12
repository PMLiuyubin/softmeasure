<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from "vue";
import * as echarts from "echarts";
import type { SeriesRow } from "../types/api";

const props = defineProps<{ rows: SeriesRow[] }>();
const host = ref<HTMLDivElement | null>(null);
let chart: echarts.ECharts | null = null;

const series = [
  { key: "nir_arrival", name: "到达近红外" },
  { key: "line1", name: "近红外模型预测" },
  { key: "line3", name: "回流侧线线性关系式" },
] as const;

function paint() {
  if (!chart) return;
  chart.setOption({
    tooltip: { trigger: "axis" },
    legend: { data: series.map((item) => item.name) },
    xAxis: { type: "category", data: props.rows.map((row) => row.t) },
    yAxis: { type: "value", name: "含量 %" },
    series: series.map((item) => ({
      name: item.name,
      type: "line",
      showSymbol: false,
      data: props.rows.map((row) => row[item.key]),
    })),
  });
}

onMounted(() => {
  if (host.value) chart = echarts.init(host.value);
  paint();
});
watch(() => props.rows, paint);
onBeforeUnmount(() => chart?.dispose());
</script>

<template>
  <div ref="host" style="height: 460px"></div>
</template>
