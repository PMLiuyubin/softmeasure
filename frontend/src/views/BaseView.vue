<script setup lang="ts">
import { onMounted } from "vue";
import { useFoundation } from "../store/foundation";

const store = useFoundation();
onMounted(() => store.load());
</script>

<template>
  <el-alert v-if="store.error" :title="store.error" type="error" />
  <template v-if="store.body">
    <el-descriptions title="数据集" :column="1" border>
      <el-descriptions-item label="快照行数">{{ store.body.dataset.n_rows }}</el-descriptions-item>
      <el-descriptions-item label="时间">{{ store.body.dataset.time_min }} 至 {{ store.body.dataset.time_max }}</el-descriptions-item>
      <el-descriptions-item label="验收窗">{{ store.body.dataset.acceptance.start }} 至 {{ store.body.dataset.acceptance.end }}，快照内 {{ store.body.dataset.acceptance.rows_in_snapshot }} 行</el-descriptions-item>
    </el-descriptions>
    <el-descriptions title="机理算子" :column="1" border style="margin-top: 16px">
      <el-descriptions-item label="公式">{{ store.body.mechanism.formula }}</el-descriptions-item>
      <el-descriptions-item label="权重">{{ store.body.mechanism.weights }}</el-descriptions-item>
    </el-descriptions>
    <el-descriptions title="预测引擎" :column="1" border style="margin-top: 16px">
      <el-descriptions-item label="逐点推理">{{ store.body.predict.live_infer.enabled ? "开" : "关" }}</el-descriptions-item>
      <el-descriptions-item label="说明">{{ store.body.predict.live_infer.reason }}</el-descriptions-item>
    </el-descriptions>
    <el-descriptions title="挖掘" :column="1" border style="margin-top: 16px">
      <el-descriptions-item label="在线导入">{{ store.body.mining.imported_by_web ? "是" : "否" }}</el-descriptions-item>
      <el-descriptions-item label="说明">{{ store.body.mining.note }}</el-descriptions-item>
    </el-descriptions>
  </template>
</template>
