<template>
  <el-container style="min-height: 100vh">
    <el-header style="display: flex; align-items: center; gap: 24px">
      <strong>侧线甲基萘软测量</strong>
      <el-menu mode="horizontal" :router="true" :ellipsis="false" :default-active="$route.path">
        <el-menu-item index="/predict">侧线预测</el-menu-item>
        <el-menu-item index="/base">底座总览</el-menu-item>
        <el-menu-item index="/score">验收指标</el-menu-item>
        <el-menu-item index="/sources">工厂资料</el-menu-item>
      </el-menu>
    </el-header>
    <el-main>
      <router-view />
    </el-main>
  </el-container>
</template>
