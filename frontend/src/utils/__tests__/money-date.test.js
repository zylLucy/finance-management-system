import { describe, expect, it } from 'vitest'
import { formatMoney, formatPercent } from '../money'
import { toYearMonth, monthLabel, getMonthDays, getDayOfMonth } from '../date'

describe('money utilities', () => {
  it('formats currency with two decimal places', () => {
    expect(formatMoney(12)).toBe('¥12.00')
    expect(formatMoney('8.5')).toBe('¥8.50')
    expect(formatMoney(null)).toBe('¥0.00')
  })

  it('formats percent values safely', () => {
    expect(formatPercent(0)).toBe('0.0%')
    expect(formatPercent(0.456)).toBe('45.6%')
    expect(formatPercent(1.2)).toBe('100.0%')
  })
})

describe('date utilities', () => {
  it('converts date-like values into YYYYMM numbers', () => {
    expect(toYearMonth('2026-06')).toBe(202606)
    expect(toYearMonth('2026-06-15')).toBe(202606)
    expect(toYearMonth(new Date(2026, 5, 1))).toBe(202606)
  })

  it('formats month labels and month day counts', () => {
    expect(monthLabel(202606)).toBe('2026年06月')
    expect(getMonthDays(202602)).toBe(28)
    expect(getDayOfMonth('2026-06-09')).toBe(9)
  })
})
