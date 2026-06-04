import { defineStore } from 'pinia'

const STORAGE_KEY = 'smart-ledger-user'

export const useSessionStore = defineStore('session', {
  state: () => ({
    user: null,
    initialized: false
  }),
  getters: {
    isAuthenticated: (state) => Boolean(state.user?.user_id),
    userId: (state) => state.user?.user_id,
    username: (state) => state.user?.username || ''
  },
  actions: {
    initialize() {
      if (this.initialized) {
        return
      }

      const raw = localStorage.getItem(STORAGE_KEY)
      try {
        this.user = raw ? JSON.parse(raw) : null
      } catch {
        this.user = null
        localStorage.removeItem(STORAGE_KEY)
      }
      this.initialized = true
    },
    setUser(user) {
      this.user = {
        user_id: user.user_id,
        username: user.username
      }
      this.initialized = true
      localStorage.setItem(STORAGE_KEY, JSON.stringify(this.user))
    },
    logout() {
      this.user = null
      this.initialized = true
      localStorage.removeItem(STORAGE_KEY)
    }
  }
})
