<script setup>
import { nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  trend: {
    type: Object,
    default: () => ({ days: [], income: [], expense: [] })
  }
})

const chartRef = ref(null)
let chart = null

function renderChart() {
  if (!chartRef.value) {
    return
  }

  if (!chart) {
    chart = echarts.init(chartRef.value)
  }

  chart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['收入', '支出'] },
    grid: { left: 40, right: 24, top: 48, bottom: 36 },
    xAxis: { type: 'category', data: props.trend.days },
    yAxis: { type: 'value' },
    series: [
      { name: '收入', type: 'line', smooth: true, data: props.trend.income, itemStyle: { color: '#16a34a' } },
      { name: '支出', type: 'line', smooth: true, data: props.trend.expense, itemStyle: { color: '#dc2626' } }
    ]
  })
}

async function updateChart() {
  await nextTick()
  renderChart()
}

function resizeChart() {
  if (!chart) {
    renderChart()
    return
  }

  chart.resize()
}

onMounted(() => {
  updateChart()
  window.addEventListener('resize', resizeChart)
})

watch(() => props.trend, updateChart, { deep: true })

onBeforeUnmount(() => {
  window.removeEventListener('resize', resizeChart)
  chart?.dispose()
  chart = null
})
</script>

<template>
  <div ref="chartRef" class="chart-shell"></div>
</template>
