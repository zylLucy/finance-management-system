<script setup>
import { nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  data: {
    type: Array,
    default: () => []
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
    tooltip: { trigger: 'item', formatter: '{b}: ¥{c} ({d}%)' },
    legend: { bottom: 0 },
    series: [
      {
        name: '消费结构',
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['50%', '45%'],
        data: props.data,
        label: { formatter: '{b}\n{d}%' }
      }
    ]
  })
}

async function updateChart() {
  await nextTick()

  if (!props.data.length) {
    chart?.dispose()
    chart = null
    return
  }

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

watch(() => props.data, updateChart, { deep: true })

onBeforeUnmount(() => {
  window.removeEventListener('resize', resizeChart)
  chart?.dispose()
  chart = null
})
</script>

<template>
  <div v-if="data.length" ref="chartRef" class="chart-shell"></div>
  <div v-else class="empty-state">本月暂无支出数据</div>
</template>
