import { defineStore } from 'pinia'
import { ref } from 'vue'
import myAxios from '@/request'

export const useUserStore = defineStore('user', () => {
  const userId = ref<string>(loadFromStorage('userId'))
  const username = ref<string>(loadFromStorage('username'))
  const userRole = ref<string>(loadFromStorage('userRole'))
  const isLoggedIn = ref(!!loadFromStorage('userId'))

  const login = async (userAccount: string, password: string) => {
    const res = await myAxios.post('/user/login', {
      username: userAccount,
      userPassword: password,
    })
    const raw = res.data
    const data = raw?.data ?? raw
    if (data && data.userId) {
      userId.value = data.userId ?? ''
      username.value = data.username ?? ''
      userRole.value = data.userRole ?? ''
      isLoggedIn.value = true
      saveToStorage(data)
      return data
    }
    throw new Error(raw?.message || '登录失败，请检查账号或密码')
  }

  const logout = async () => {
    try {
      await myAxios.post('/user/logout')
    } finally {
      userId.value = ''
      username.value = ''
      userRole.value = ''
      isLoggedIn.value = false
      clearStorage()
    }
  }

  const fetchCurrentUser = async () => {
    try {
      const res = await myAxios.get('/user/get/login')
      const data = res.data?.data ?? res.data
      if (data) {
        userId.value = data.userId ?? ''
        username.value = data.username ?? ''
        userRole.value = data.userRole ?? ''
        isLoggedIn.value = true
        saveToStorage(data)
      }
    } catch {
      isLoggedIn.value = false
      clearStorage()
    }
  }

  return { userId, username, userRole, isLoggedIn, login, logout, fetchCurrentUser }
})

function saveToStorage(data: any) {
  try {
    localStorage.setItem('clouddesk_user', JSON.stringify({
      userId: data.userId ?? '',
      username: data.username ?? '',
      userRole: data.userRole ?? '',
    }))
  } catch {}
}

function loadFromStorage(key: string): string {
  try {
    const stored = localStorage.getItem('clouddesk_user')
    if (stored) {
      return JSON.parse(stored)[key] || ''
    }
  } catch {}
  return ''
}

function clearStorage() {
  try {
    localStorage.removeItem('clouddesk_user')
  } catch {}
}

export function getStoredUserId(): string {
  return loadFromStorage('userId')
}
