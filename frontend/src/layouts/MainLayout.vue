<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessageBox } from 'element-plus'
import { useSessionStore } from '../stores/session'

const route = useRoute()
const router = useRouter()
const session = useSessionStore()

const activeMenu = computed(() => route.path)

async function logout() {
  try {
    await ElMessageBox.confirm('确定要退出登录吗？', '退出确认', {
      confirmButtonText: '退出',
      cancelButtonText: '取消',
      type: 'warning'
    })
    session.logout()
    router.push({ name: 'login' })
  } catch {
    return
  }
}
</script>

<template>
  <el-container class="app-shell">
    <el-aside width="230px" class="app-aside">
      <div class="app-brand">日常记账理财系统</div>
      <el-menu :default-active="activeMenu" router background-color="#102a43" text-color="#dbeafe" active-text-color="#ffffff">
        <el-menu-item index="/app/dashboard">首页</el-menu-item>
        <el-menu-item index="/app/records">账单管理</el-menu-item>
        <el-menu-item index="/app/budget">预算设置</el-menu-item>
        <el-menu-item index="/app/ai-report">AI 财务报告</el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="app-header">
        <strong>日常记账理财管理系统</strong>
        <div>
          <span>当前用户：{{ session.username }}</span>
          <el-button type="primary" plain size="small" style="margin-left: 12px" @click="logout">退出登录</el-button>
        </div>
      </el-header>
      <el-main class="app-main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>
