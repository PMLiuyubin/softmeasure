<script setup lang="ts">
import { onMounted } from "vue";
import { useFoundation } from "../store/foundation";

const store = useFoundation();
onMounted(() => store.load());
</script>

<template>
  <template v-if="store.body">
    <p>{{ store.body.evaluate.window }}，{{ store.body.evaluate.grain || "5 min" }}，{{ store.body.evaluate.n }} 点。{{ store.body.evaluate.ruler }}</p>
    <el-table :data="store.body.evaluate.lines" border>
      <el-table-column prop="name" label="线" />
      <el-table-column prop="pool" label="归属" width="100" />
      <el-table-column prop="kind" label="权重" />
      <el-table-column prop="R2" label="决定系数" />
      <el-table-column prop="RMSE" label="均方根" />
      <el-table-column prop="n" label="点数" width="90" />
    </el-table>
  </template>
</template>
