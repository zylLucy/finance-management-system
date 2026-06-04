import { beforeEach, describe, expect, it } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import router from '../index'
import { useSessionStore } from '../../stores/session'

beforeEach(async () => {
  localStorage.clear()
  setActivePinia(createPinia())
  await router.push('/login')
  await router.isReady()
})

describe('router auth guard', () => {
  it('redirects anonymous users from protected pages to login', async () => {
    await router.push('/app/dashboard')
    expect(router.currentRoute.value.name).toBe('login')
  })

  it('allows authenticated users into dashboard', async () => {
    const session = useSessionStore()
    session.setUser({ user_id: 1, username: 'alice' })

    await router.push('/app/dashboard')
    expect(router.currentRoute.value.name).toBe('dashboard')
  })
})
