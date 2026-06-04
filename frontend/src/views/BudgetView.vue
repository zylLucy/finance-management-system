<script setup>
import { computed, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { api } from '../services/api'
import { useBudgetStore } from '../stores/budget'
import { useSessionStore } from '../stores/session'
import { currentMonthText, monthLabel, toYearMonth } from '../utils/date'
import { formatMoney } from '../utils/money'

const session = useSessionStore()
const budgetStore = useBudgetStore()
const saving = ref(false)
const form = reactive({ month: currentMonthText(), amount: 3000 })
const yearMonth = computed(() => toYearMonth(form.month))
const savedBudget = computed(() => budgetStore.getBudget(yearMonth.value))

async function saveBudget() {
  if (!form.month || !form.amount || Number(form.amount) <= 0) {
    ElMessage.warning('请选择月份并输入大于 0 的预算金额')
    return
  }

  saving.value = true
  try {
    const response = await api.saveBudget({
      user_id: session.userId,
      year_month: yearMonth.value,
      amount: Number(Number(form.amount).toFixed(2))
    })
    budgetStore.setBudget(yearMonth.value, Number(Number(form.amount).toFixed(2)))
    ElMessage.success(response.msg || '预算保存成功')
  } catch (error) {
    ElMessage.error(error.message)
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div>
    <h1 class="page-title">预算设置</h1>
    <el-row :gutter="16">
      <el-col :xs="24" :lg="12">
        <el-card class="page-card">
          <template #header>设置月度预算</template>
          <el-form label-position="top">
            <el-form-item label="预算月份">
              <el-date-picker v-model="form.month" type="month" value-format="YYYY-MM" style="width: 100%" />
            </el-form-item>
            <el-form-item label="预算金额">
              <el-input-number v-model="form.amount" :precision="2" :min="0.01" style="width: 100%" />
            </el-form-item>
            <el-button type="primary" :loading="saving" @click="saveBudget">保存预算</el-button>
          </el-form>
        </el-card>
      </el-col>
      <el-col :xs="24" :lg="12">
        <el-card class="page-card">
          <template #header>当前预算</template>
          <div v-if="savedBudget !== null">
            <p>{{ monthLabel(yearMonth) }}预算：</p>
            <div class="metric-value">{{ formatMoney(savedBudget) }}</div>
          </div>
          <div v-else class="empty-state">当前月份尚未设置预算。</div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>
