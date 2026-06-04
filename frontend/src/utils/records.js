import { getDayOfMonth, getMonthDays, toYearMonth } from './date'

function amountOf(record) {
  const value = Number(record.amount)
  return Number.isFinite(value) ? value : 0
}

export function attachCategories(records, categories) {
  const categoryMap = new Map(categories.map((category) => [category.id, category]))

  return records.map((record) => {
    const category = categoryMap.get(record.category_id)
    return {
      ...record,
      amount: amountOf(record),
      categoryName: category?.name || '未分类',
      type: category?.type || 'expense'
    }
  })
}

export function filterRecords(records, filters = {}) {
  const keyword = String(filters.keyword || '').trim()
  const categoryId = filters.categoryId ? Number(filters.categoryId) : null
  const [startDate, endDate] = filters.dateRange || []

  return records.filter((record) => {
    if (categoryId && record.category_id !== categoryId) {
      return false
    }

    if (startDate && record.date < startDate) {
      return false
    }

    if (endDate && record.date > endDate) {
      return false
    }

    if (keyword && !String(record.remark || '').includes(keyword)) {
      return false
    }

    return true
  })
}

export function summarizeRecords(records, categories, yearMonth, budgetAmount = null) {
  const enriched = attachCategories(records, categories)
  const monthlyRecords = enriched.filter((record) => toYearMonth(record.date) === Number(yearMonth))
  const monthDays = getMonthDays(yearMonth)
  const trend = {
    days: Array.from({ length: monthDays }, (_, index) => String(index + 1)),
    income: Array.from({ length: monthDays }, () => 0),
    expense: Array.from({ length: monthDays }, () => 0)
  }
  const categoryExpenseMap = new Map()

  let monthIncome = 0
  let monthExpense = 0

  monthlyRecords.forEach((record) => {
    const amount = amountOf(record)
    const dayIndex = getDayOfMonth(record.date) - 1

    const hasValidDay = dayIndex >= 0 && dayIndex < monthDays

    if (record.type === 'income') {
      monthIncome += amount
      if (hasValidDay) {
        trend.income[dayIndex] += amount
      }
      return
    }

    monthExpense += amount
    if (hasValidDay) {
      trend.expense[dayIndex] += amount
    }
    categoryExpenseMap.set(record.categoryName, (categoryExpenseMap.get(record.categoryName) || 0) + amount)
  })

  const budgetValue = Number(budgetAmount)
  const hasBudget = budgetAmount !== null && budgetAmount !== undefined && Number.isFinite(budgetValue)
  const budget = !hasBudget
    ? { hasBudget: false, amount: 0, remaining: 0, percent: 0 }
    : {
        hasBudget: true,
        amount: budgetValue,
        remaining: Math.max(budgetValue - monthExpense, 0),
        percent: budgetValue > 0 ? Math.min(monthExpense / budgetValue, 1) : 0
      }

  return {
    monthIncome,
    monthExpense,
    budget,
    categoryExpenses: Array.from(categoryExpenseMap.entries())
      .map(([name, value]) => ({ name, value }))
      .sort((a, b) => b.value - a.value),
    trend
  }
}
