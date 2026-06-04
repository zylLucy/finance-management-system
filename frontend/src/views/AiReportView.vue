<script setup>
import { computed, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { api } from '../services/api'
import { useSessionStore } from '../stores/session'
import { currentMonthText, monthLabel, toYearMonth } from '../utils/date'

const session = useSessionStore()
const loading = ref(false)
const month = ref(currentMonthText())
const report = ref('')
const yearMonth = computed(() => toYearMonth(month.value))

async function generateReport() {
  if (!month.value) {
    ElMessage.warning('请选择报告月份')
    return
  }

  loading.value = true
  try {
    const response = await api.getAiReport(session.userId, yearMonth.value)
    report.value = response.data || ''
    ElMessage.success('AI 财务报告已生成')
  } catch (error) {
    ElMessage.error(error.message)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div>
    <h1 class="page-title">AI 财务报告</h1>
    <el-card class="page-card">
      <div class="toolbar">
        <el-date-picker v-model="month" type="month" value-format="YYYY-MM" />
        <el-button type="primary" :loading="loading" @click="generateReport">一键生成 AI 财务分析</el-button>
      </div>
      <div v-if="report">
        <h3>{{ monthLabel(yearMonth) }}财务诊断报告</h3>
        <div class="report-content">{{ report }}</div>
      </div>
      <div v-else class="empty-state">请选择月份并生成报告。</div>
    </el-card>
  </div>
</template>
