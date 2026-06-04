<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import ExpensePieChart from '../components/charts/ExpensePieChart.vue'
import TrendLineChart from '../components/charts/TrendLineChart.vue'
import { api } from '../services/api'
import { useBudgetStore } from '../stores/budget'
import { useSessionStore } from '../stores/session'
import { currentMonthText, monthLabel, toYearMonth } from '../utils/date'
import { formatMoney, formatPercent } from '../utils/money'
import { summarizeRecords } from '../utils/records'

const session = useSessionStore()
const budgetStore = useBudgetStore()
const loading = ref(false)
const todayStats = ref({ income: 0, expense: 0 })
const records = ref([])
const categories = ref([])
const yearMonth = ref(toYearMonth(currentMonthText()))
const selectedMonth = ref(currentMonthText())

const budgetAmount = computed(() => budgetStore.getBudget(yearMonth.value))
const summary = computed(() => summarizeRecords(records.value, categories.value, yearMonth.value, budgetAmount.value))

watch(selectedMonth, (newVal) => {
  yearMonth.value = toYearMonth(newVal)
})

async function loadDashboard() {
  loading.value = true
  try {
    const [categoryResponse, recordResponse, todayResponse] = await Promise.all([
      api.getCategories(session.userId),
      api.getRecords(session.userId),
      api.getTodayStats(session.userId)
    ])

    categories.value = categoryResponse.data || []
    records.value = recordResponse.data || []
    todayStats.value = todayResponse.data || { income: 0, expense: 0 }
  } catch (error) {
    ElMessage.error(error.message)
  } finally {
    loading.value = false
  }
}

onMounted(loadDashboard)
</script>

<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">首页</h1>
      <el-date-picker
        v-model="selectedMonth"
        type="month"
        value-format="YYYY-MM"
        placeholder="选择月份"
        style="width: 200px"
      />
    </div>
    <el-row :gutter="16" v-loading="loading">
      <el-col :xs="24" :sm="12" :lg="6">
        <el-card class="metric-card">
          <div class="metric-label">当日总收入</div>
          <div class="metric-value income">{{ formatMoney(todayStats.income) }}</div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <el-card class="metric-card">
          <div class="metric-label">当日总支出</div>
          <div class="metric-value expense">{{ formatMoney(todayStats.expense) }}</div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <el-card class="metric-card">
          <div class="metric-label">{{ monthLabel(yearMonth) }}总收入</div>
          <div class="metric-value income">{{ formatMoney(summary.monthIncome) }}</div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <el-card class="metric-card">
          <div class="metric-label">{{ monthLabel(yearMonth) }}总消费</div>
          <div class="metric-value expense">{{ formatMoney(summary.monthExpense) }}</div>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="page-card" style="margin-top: 16px">
      <template #header>预算概览</template>
      <div v-if="summary.budget.hasBudget">
        <p>预算金额：{{ formatMoney(summary.budget.amount) }}</p>
        <p>剩余额度：{{ formatMoney(summary.budget.remaining) }}</p>
        <el-progress :percentage="Number((summary.budget.percent * 100).toFixed(1))" :status="summary.budget.percent >= 1 ? 'exception' : 'success'" />
        <p>使用率：{{ formatPercent(summary.budget.percent) }}</p>
      </div>
      <div v-else class="empty-state">本月尚未设置预算，请到"预算设置"保存。</div>
    </el-card>

    <el-row :gutter="16" style="margin-top: 16px">
      <el-col :xs="24" :lg="10">
        <el-card class="page-card chart-card">
          <template #header>{{ monthLabel(yearMonth) }}消费结构</template>
          <ExpensePieChart :data="summary.categoryExpenses" />
        </el-card>
      </el-col>
      <el-col :xs="24" :lg="14">
        <el-card class="page-card chart-card">
          <template #header>{{ monthLabel(yearMonth) }}每日收支趋势</template>
          <TrendLineChart :trend="summary.trend" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>
