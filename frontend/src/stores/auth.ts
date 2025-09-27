import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/utils/api'
import { ElMessage } from 'element-plus'
import router from '@/router'

export interface User {
  id: number
  username: string
  email: string
  role: 'SYSTEM_ADMIN' | 'PROJECT_ADMIN' | 'REGULAR_USER'
  is_active: boolean
  created_at: string
}

export interface LoginForm {
  username: string
  password: string
}

export interface RegisterForm {
  username: string
  email: string
  password: string
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('token'))
  const loading = ref(false)

  // Computed properties
  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const isSystemAdmin = computed(() => user.value?.role === 'SYSTEM_ADMIN')
  const isProjectAdmin = computed(() => user.value?.role === 'PROJECT_ADMIN')
  const isRegularUser = computed(() => user.value?.role === 'REGULAR_USER')
  const userRole = computed(() => user.value?.role || 'REGULAR_USER')

  // Actions
  const login = async (loginForm: LoginForm) => {
    loading.value = true
    try {
      const formData = new FormData()
      formData.append('username', loginForm.username)
      formData.append('password', loginForm.password)

      const response = await api.post('/api/v1/auth/token', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      })

      const { access_token } = response.data
      token.value = access_token
      localStorage.setItem('token', access_token)

      // Fetch user info
      await fetchUserInfo()

      ElMessage.success('登录成功')
      
      // Redirect based on role
      if (isSystemAdmin.value) {
        router.push('/admin/users')
      } else {
        router.push('/')
      }
    } catch (error: any) {
      const message = error.response?.data?.detail || '登录失败'
      ElMessage.error(message)
      throw error
    } finally {
      loading.value = false
    }
  }

  const register = async (registerForm: RegisterForm) => {
    loading.value = true
    try {
      const response = await api.post('/api/v1/auth/register', registerForm)
      
      ElMessage.success('注册成功，请登录')
      router.push('/login')
    } catch (error: any) {
      const message = error.response?.data?.detail || '注册失败'
      ElMessage.error(message)
      throw error
    } finally {
      loading.value = false
    }
  }

  const fetchUserInfo = async () => {
    if (!token.value) return

    try {
      const response = await api.get('/api/v1/auth/me')
      user.value = response.data
    } catch (error: any) {
      console.error('Failed to fetch user info:', error)
      logout()
    }
  }

  const logout = () => {
    user.value = null
    token.value = null
    localStorage.removeItem('token')
    router.push('/login')
    ElMessage.success('已退出登录')
  }

  const setUser = (userInfo: User) => {
    user.value = userInfo
  }

  const updateUserInfo = (userInfo: User) => {
    user.value = userInfo
  }

  // Initialize auth state
  const initializeAuth = async () => {
    if (token.value) {
      await fetchUserInfo()
    }
  }

  return {
    // State
    user,
    token,
    loading,
    
    // Computed
    isAuthenticated,
    isSystemAdmin,
    isProjectAdmin,
    isRegularUser,
    userRole,
    
    // Actions
    login,
    register,
    fetchUserInfo,
    logout,
    setUser,
    updateUserInfo,
    initializeAuth,
  }
})