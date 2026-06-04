<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { api } from '../services/api'
import { useSessionStore } from '../stores/session'
import { currentDateText } from '../utils/date'
import { formatMoney } from '../utils/money'
import { attachCategories, filterRecords } from '../utils/records'

const session = useSessionStore()
const loading = ref(false)
const saving = ref(false)
const dialogVisible = ref(false)
const categories = ref([])
const records = ref([])
const filters = reactive({ dateRange: [], categoryId: '', keyword: '' })
const form = reactive({ type: 'expense', category_id: '', amount: '', date: currentDateText(), remark: '' })

const enrichedRecords = computed(() => attachCategories(records.value, categories.value))
const filteredRecords = computed(() => filterRecords(enrichedRecords.value, filters))
const categoryOptions = computed(() => categories.value.filter((category) => category.type === form.type))

function resetForm() {
  form.type = 'expense'
  form.category_id = ''
  form.amount = ''
  form.date = currentDateText()
  form.remark = ''
}

async function loadData() {
  loading.value = true
  try {
    const [categoryResponse, recordResponse] = await Promise.all([
      api.getCategories(session.userId),
      api.getRecords(session.userId)
    ])
    categories.value = categoryResponse.data || []
    records.value = recordResponse.data || []
  } catch (error) {
    ElMessage.error(error.message)
  } finally {
    loading.value = false
  }
}

function openDialog() {
  resetForm()
  dialogVisible.value = true
}

async function submitRecord() {
  if (!form.category_id || !form.amount || !form.date) {
    ElMessage.warning('请填写分类、金额和日期')
    return
  }

  saving.value = true
  try {
    const response = await api.addRecord({
      user_id: session.userId,
      category_id: Number(form.category_id),
      amount: Number(Number(form.amount).toFixed(2)),
      date: form.date,
      remark: form.remark || null
    })
    ElMessage.success(response.msg || '记账成功')
    dialogVisible.value = false
    await loadData()
  } catch (error) {
    ElMessage.error(error.message)
  } finally {
    saving.value = false
  }
}

onMounted(loadData)
</script>

<template>
  <div>
    <h1 class="page-title">账单管理</h1>
    <el-card class="page-card">
      <div class="toolbar">
        <el-date-picker v-model="filters.dateRange" type="daterange" value-format="YYYY-MM-DD" start-placeholder="开始日期" end-placeholder="结束日期" />
        <el-select v-model="filters.categoryId" clearable placeholder="按分类筛选" style="width: 180px">
          <el-option v-for="category in categories" :key="category.id" :label="category.name" :value="category.id" />
        </el-select>
        <el-input v-model="filters.keyword" clearable placeholder="按备注关键词搜索" style="width: 220px" />
        <el-button type="primary" @click="openDialog">新增账单</el-button>
      </div>

      <el-table :data="filteredRecords" v-loading="loading" stripe>
        <el-table-column prop="date" label="日期" width="130" />
        <el-table-column prop="categoryName" label="分类" width="120" />
        <el-table-column label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="row.type === 'income' ? 'success' : 'danger'">{{ row.type === 'income' ? '收入' : '支出' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="金额" width="140">
          <template #default="{ row }">
            <span :class="row.type === 'income' ? 'income' : 'expense'">{{ formatMoney(row.amount) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" min-width="180" show-overflow-tooltip />
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" title="新增账单" width="480px">
      <el-form label-position="top">
        <el-form-item label="收支类型">
          <el-radio-group v-model="form.type" @change="form.category_id = ''">
            <el-radio-button label="expense">支出</el-radio-button>
            <el-radio-button label="income">收入</el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="form.category_id" placeholder="请选择分类" style="width: 100%">
            <el-option v-for="category in categoryOptions" :key="category.id" :label="category.name" :value="category.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="金额">
          <el-input-number v-model="form.amount" :precision="2" :min="0.01" style="width: 100%" />
        </el-form-item>
        <el-form-item label="日期">
          <el-date-picker v-model="form.date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.remark" maxlength="255" show-word-limit placeholder="可选" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="submitRecord">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
