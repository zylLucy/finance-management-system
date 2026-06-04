import { defineStore } from 'pinia'

const STORAGE_KEY = 'smart-ledger-budgets'

function loadBudgets() {
  const raw = localStorage.getItem(STORAGE_KEY)
  try {
    return raw ? JSON.parse(raw) : {}
  } catch {
    localStorage.removeItem(STORAGE_KEY)
    return {}
  }
}

export const useBudgetStore = defineStore('budget', {
  state: () => ({
    budgets: loadBudgets()
  }),
  actions: {
    setBudget(yearMonth, amount) {
      this.budgets = {
        ...this.budgets,
        [String(yearMonth)]: Number(amount)
      }
      localStorage.setItem(STORAGE_KEY, JSON.stringify(this.budgets))
    },
    getBudget(yearMonth) {
      const value = this.budgets[String(yearMonth)]
      return value === undefined ? null : Number(value)
    }
  }
})
