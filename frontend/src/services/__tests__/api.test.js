import { beforeEach, describe, expect, it, vi } from 'vitest'
import http from '../http'
import { api } from '../api'

vi.mock('../http', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn()
  }
}))

describe('api wrapper', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('maps auth endpoints', () => {
    api.login({ username: 'alice', password: 'pw' })
    api.register({ username: 'bob', password: 'pw' })

    expect(http.post).toHaveBeenCalledWith('/user/login', { username: 'alice', password: 'pw' })
    expect(http.post).toHaveBeenCalledWith('/user/register', { username: 'bob', password: 'pw' })
  })

  it('maps finance endpoints to the existing backend contract', () => {
    api.getCategories(1)
    api.addRecord({ user_id: 1, category_id: 2, amount: 18.5, date: '2026-06-01', remark: '午餐' })
    api.getRecords(1)
    api.saveBudget({ user_id: 1, year_month: 202606, amount: 3000 })
    api.getTodayStats(1)
    api.getAiReport(1, 202606)

    expect(http.get).toHaveBeenCalledWith('/category/list/1')
    expect(http.post).toHaveBeenCalledWith('/record/add', {
      user_id: 1,
      category_id: 2,
      amount: 18.5,
      date: '2026-06-01',
      remark: '午餐'
    })
    expect(http.get).toHaveBeenCalledWith('/record/list/1')
    expect(http.post).toHaveBeenCalledWith('/budget/save', { user_id: 1, year_month: 202606, amount: 3000 })
    expect(http.get).toHaveBeenCalledWith('/record/today/1')
    expect(http.get).toHaveBeenCalledWith('/report/ai/1/202606')
  })
})
