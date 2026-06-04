import { describe, expect, it } from 'vitest'
import { attachCategories, filterRecords, summarizeRecords } from '../records'

const categories = [
  { id: 1, name: '餐饮', type: 'expense' },
  { id: 2, name: '购物', type: 'expense' },
  { id: 6, name: '工资', type: 'income' }
]

const records = [
  { id: 1, category_id: 1, amount: 20, date: '2026-06-01', remark: '午餐' },
  { id: 2, category_id: 6, amount: 5000, date: '2026-06-02', remark: '六月工资' },
  { id: 3, category_id: 2, amount: 100, date: '2026-06-02', remark: '衣服' },
  { id: 4, category_id: 1, amount: 30, date: '2026-05-31', remark: '五月晚餐' }
]

describe('record utilities', () => {
  it('attaches category names and types to records', () => {
    const result = attachCategories(records, categories)

    expect(result[0]).toMatchObject({ categoryName: '餐饮', type: 'expense' })
    expect(result[1]).toMatchObject({ categoryName: '工资', type: 'income' })
  })

  it('filters records by date range, category, and keyword', () => {
    const enriched = attachCategories(records, categories)
    const result = filterRecords(enriched, {
      dateRange: ['2026-06-01', '2026-06-30'],
      categoryId: 1,
      keyword: '午餐'
    })

    expect(result).toHaveLength(1)
    expect(result[0].id).toBe(1)
  })

  it('summarizes monthly totals, category expenses, trend data, and budget usage', () => {
    const summary = summarizeRecords(records, categories, 202606, 200)

    expect(summary.monthIncome).toBe(5000)
    expect(summary.monthExpense).toBe(120)
    expect(summary.budget.remaining).toBe(80)
    expect(summary.budget.percent).toBe(0.6)
    expect(summary.categoryExpenses).toEqual([
      { name: '购物', value: 100 },
      { name: '餐饮', value: 20 }
    ])
    expect(summary.trend.days).toHaveLength(30)
    expect(summary.trend.income[1]).toBe(5000)
    expect(summary.trend.expense[1]).toBe(100)
  })

  it('handles missing filters, invalid budget values, and invalid trend dates safely', () => {
    const enriched = attachCategories([
      { id: 5, category_id: 99, amount: 'abc', date: '2026-06-03', remark: null },
      { id: 6, category_id: 1, amount: 50, date: '2026-06', remark: '缺少日期' }
    ], categories)

    expect(enriched[0]).toMatchObject({ amount: 0, categoryName: '未分类', type: 'expense' })
    expect(filterRecords(enriched)).toHaveLength(2)

    const summary = summarizeRecords(enriched, categories, 202606, undefined)
    expect(summary.budget).toEqual({ hasBudget: false, amount: 0, remaining: 0, percent: 0 })
    expect(summary.monthExpense).toBe(50)
    expect(summary.trend.expense).toHaveLength(30)
    expect(summary.trend.expense.every(Number.isFinite)).toBe(true)
  })
})
