import { beforeEach, describe, expect, it } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useSessionStore } from '../session'
import { useBudgetStore } from '../budget'

beforeEach(() => {
  localStorage.clear()
  setActivePinia(createPinia())
})

describe('session store', () => {
  it('persists and restores the logged-in user', () => {
    const session = useSessionStore()
    session.setUser({ user_id: 7, username: 'alice' })

    expect(session.isAuthenticated).toBe(true)
    expect(JSON.parse(localStorage.getItem('smart-ledger-user'))).toEqual({ user_id: 7, username: 'alice' })

    const restored = useSessionStore()
    restored.$reset()
    restored.initialize()
    expect(restored.user).toEqual({ user_id: 7, username: 'alice' })
  })

  it('clears local user data on logout', () => {
    const session = useSessionStore()
    session.setUser({ user_id: 7, username: 'alice' })
    session.logout()

    expect(session.user).toBeNull()
    expect(localStorage.getItem('smart-ledger-user')).toBeNull()
  })
})

describe('budget store', () => {
  it('stores budgets by yearMonth in local storage', () => {
    const budget = useBudgetStore()
    budget.setBudget(202606, 3000)

    expect(budget.getBudget(202606)).toBe(3000)
    expect(JSON.parse(localStorage.getItem('smart-ledger-budgets'))).toEqual({ '202606': 3000 })
  })
})
