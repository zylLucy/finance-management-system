<script setup>
import { computed, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { api } from '../services/api'
import { useSessionStore } from '../stores/session'
import { currentMonthText, monthLabel, toYearMonth } from '../utils/date'

const session = useSessionStore()
const loading = ref(false)
const reportType = ref('monthly') // 'monthly' | 'yearly'
const month = ref(currentMonthText())
const year = ref(new Date().getFullYear())
const report = ref('')
const isCached = ref(false)

const yearMonth = computed(() => toYearMonth(month.value))

async function generateReport() {
  loading.value = true
  report.value = ''
  isCached.value = false

  try {
    let response
    if (reportType.value === 'yearly') {
      response = await api.getAiYearReport(session.userId, year.value)
    } else {
      if (!month.value) {
        ElMessage.warning('请选择报告月份')
        loading.value = false
        return
      }
      response = await api.getAiReport(session.userId, yearMonth.value)
    }
    report.value = response.data || ''
    isCached.value = response.cached === true
    ElMessage.success(isCached.value ? '已加载历史报告' : 'AI 财务报告已生成')
  } catch (error) {
    ElMessage.error(error.message)
  } finally {
    loading.value = false
  }
}

// 切换月份时自动加载缓存
watch(month, async () => {
  if (!month.value || reportType.value !== 'monthly') return
  loading.value = true
  report.value = ''
  isCached.value = false
  try {
    const response = await api.getAiReport(session.userId, yearMonth.value)
    report.value = response.data || ''
    isCached.value = response.cached === true
  } catch {
    // 无缓存，静默
  } finally {
    loading.value = false
  }
})

// 切换年份时自动加载缓存
watch(year, async () => {
  if (reportType.value !== 'yearly') return
  loading.value = true
  report.value = ''
  isCached.value = false
  try {
    const response = await api.getAiYearReport(session.userId, year.value)
    report.value = response.data || ''
    isCached.value = response.cached === true
  } catch {
    // 无缓存，静默
  } finally {
    loading.value = false
  }
})

function switchType(type) {
  reportType.value = type
  report.value = ''
  isCached.value = false
  // 触发自动加载
  if (type === 'monthly' && month.value) {
    month.value = month.value // 触发 watch
  }
  if (type === 'yearly') {
    year.value = year.value // 触发 watch
  }
}

function processInline(text) {
  return text
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
}

function renderTable(lines) {
  const dataLines = lines.filter(l => !/^\|[\s\-:|]+\|$/.test(l))
  const rows = dataLines.map(l =>
    l.trim().replace(/^\|/, '').replace(/\|$/, '').split('|').map(c => c.trim())
  )
  if (rows.length === 0) return ''
  const header = rows[0]
  const body = rows.slice(1)
  const thead = '<thead><tr>' + header.map(h => `<th>${processInline(h)}</th>`).join('') + '</tr></thead>'
  const tbody = '<tbody>' + body.map(row =>
    '<tr>' + row.map(c => `<td>${processInline(c)}</td>`).join('') + '</tr>'
  ).join('') + '</tbody>'
  return '<table class="md-table">' + thead + tbody + '</table>'
}

function renderMarkdown(text) {
  if (!text) return ''

  // 按连续空行分割为段落块
  const blocks = text.split(/\n{2,}/)
  const result = blocks.map(block => {
    block = block.trim()
    if (!block) return ''
    const lines = block.split('\n')

    // 表格检测：所有非空行都以 | 开头
    if (lines.length >= 2 && lines.filter(l => l.trim()).every(l => l.trim().startsWith('|'))) {
      return renderTable(lines)
    }

    // 标题
    if (/^### (.+)$/m.test(block)) {
      return block.replace(/^### (.+)$/gm, '<h4>$1</h4>')
    }
    if (/^## (.+)$/m.test(block)) {
      return block.replace(/^## (.+)$/gm, '<h3>$1</h3>')
    }
    if (/^# (.+)$/m.test(block)) {
      return block.replace(/^# (.+)$/gm, '<h2>$1</h2>')
    }

    // 无序列表
    const nonEmptyLines = lines.filter(l => l.trim())
    if (nonEmptyLines.length > 0 && nonEmptyLines.every(l => /^\s*- /.test(l))) {
      const items = nonEmptyLines.map(l => l.replace(/^\s*- /, ''))
      return '<ul>' + items.map(i => `<li>${processInline(i)}</li>`).join('') + '</ul>'
    }

    // 引用块
    if (block.startsWith('>')) {
      return '<blockquote>' + processInline(block.replace(/^> ?/gm, '')) + '</blockquote>'
    }

    // 普通段落（合并块内换行）
    return '<p>' + processInline(block.replace(/\n/g, ' ')) + '</p>'
  }).filter(Boolean).join('\n')

  return result
}
</script>

<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">AI 财务报告</h1>
      <div class="toolbar" style="margin-bottom: 0">
        <el-radio-group v-model="reportType" @change="switchType" size="default">
          <el-radio-button value="monthly">月度报告</el-radio-button>
          <el-radio-button value="yearly">年度报告</el-radio-button>
        </el-radio-group>
        <el-date-picker
          v-if="reportType === 'monthly'"
          v-model="month"
          type="month"
          value-format="YYYY-MM"
          placeholder="选择月份"
        />
        <el-date-picker
          v-else
          v-model="year"
          type="year"
          value-format="YYYY"
          placeholder="选择年份"
        />
        <el-button type="primary" :loading="loading" @click="generateReport">
          {{ report ? '重新生成' : '一键生成报告' }}
        </el-button>
      </div>
    </div>

    <el-card class="page-card" v-loading="loading">
      <div v-if="report">
        <div style="margin-bottom: 16px; display: flex; align-items: center; gap: 12px">
          <h3 style="margin: 0">
            {{ reportType === 'yearly' ? `${year}年` : monthLabel(yearMonth) }} 财务诊断报告
          </h3>
          <el-tag v-if="isCached" type="info" size="small">已缓存</el-tag>
          <el-tag v-else type="success" size="small">新生成</el-tag>
        </div>
        <div class="report-content" v-html="renderMarkdown(report)" />
      </div>
      <div v-else class="empty-state">
        <p>选择月份/年份后自动加载历史报告，或点击「一键生成报告」生成新报告。</p>
        <p style="color: #94a3b8; font-size: 13px; margin-top: 8px">
          首次生成需调用大模型，预计耗时 5-20 秒，请耐心等待。
        </p>
      </div>
    </el-card>
  </div>
</template>