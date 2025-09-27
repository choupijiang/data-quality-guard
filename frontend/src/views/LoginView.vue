<template>
  <div class="login-container">
    <div class="login-card">
      <h1>数据库质量巡检系统</h1>
      <h2>用户登录</h2>
      
      <el-form
        ref="loginFormRef"
        :model="loginForm"
        :rules="loginRules"
        label-width="0"
        class="login-form"
      >
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="请输入用户名"
            size="large"
            prefix-icon="User"
          />
        </el-form-item>
        
        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            size="large"
            prefix-icon="Lock"
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        
        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="authStore.loading"
            @click="handleLogin"
            class="login-button"
          >
            登录
          </el-button>
        </el-form-item>
        
        <div class="form-actions">
          <router-link to="/register" class="register-link">
            还没有账号？立即注册
          </router-link>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import type { FormInstance, FormRules } from 'element-plus'

const authStore = useAuthStore()
const loginFormRef = ref<FormInstance>()

const loginForm = reactive({
  username: '',
  password: ''
})

const loginRules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6位', trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  try {
    await loginFormRef.value.validate()
    await authStore.login(loginForm)
  } catch (error) {
    console.error('Login failed:', error)
  }
}

onMounted(() => {
  // Check if already logged in
  if (authStore.isAuthenticated) {
    authStore.logout()
  }
})
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.login-card {
  background: white;
  padding: 40px;
  border-radius: 16px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
  text-align: center;
}

.login-card h1 {
  color: #333;
  margin-bottom: 10px;
  font-size: 24px;
}

.login-card h2 {
  color: #666;
  margin-bottom: 30px;
  font-size: 18px;
  font-weight: normal;
}

.login-form {
  text-align: left;
}

.login-button {
  width: 100%;
  height: 44px;
  font-size: 16px;
}

.form-actions {
  text-align: center;
  margin-top: 20px;
}

.register-link {
  color: #667eea;
  text-decoration: none;
  font-size: 14px;
}

.register-link:hover {
  text-decoration: underline;
}
</style>