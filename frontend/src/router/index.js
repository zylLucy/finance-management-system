import { createRouter, createWebHistory } from 'vue-router'
import MainLayout from '../layouts/MainLayout.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import DashboardView from '../views/DashboardView.vue'
import RecordsView from '../views/RecordsView.vue'
import BudgetView from '../views/BudgetView.vue'
import AiReportView from '../views/AiReportView.vue'
import { useSessionStore } from '../stores/session'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/app/dashboard' },
    { path: '/login', name: 'login', component: LoginView, meta: { guestOnly: true } },
    { path: '/register', name: 'register', component: RegisterView, meta: { guestOnly: true } },
    {
      path: '/app',
      component: MainLayout,
      meta: { requiresAuth: true },
      children: [
        { path: '', redirect: '/app/dashboard' },
        { path: 'dashboard', name: 'dashboard', component: DashboardView },
        { path: 'records', name: 'records', component: RecordsView },
        { path: 'budget', name: 'budget', component: BudgetView },
        { path: 'ai-report', name: 'ai-report', component: AiReportView }
      ]
    }
  ]
})

router.beforeEach((to) => {
  const session = useSessionStore()
  session.initialize()

  if (to.matched.some((route) => route.meta.requiresAuth) && !session.isAuthenticated) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }

  if (to.meta.guestOnly && session.isAuthenticated) {
    return { name: 'dashboard' }
  }

  return true
})

export default router
