<template>
  <div class="register-container">
    <div class="register-card">
      <h1>数据库质量巡检系统</h1>
      <h2>用户注册</h2>
      
      <el-form
        ref="registerFormRef"
        :model="registerForm"
        :rules="registerRules"
        label-width="0"
        class="register-form"
      >
        <el-form-item prop="username">
          <el-input
            v-model="registerForm.username"
            placeholder="请输入用户名"
            size="large"
            prefix-icon="User"
          />
        </el-form-item>
        
        <el-form-item prop="email">
          <el-input
            v-model="registerForm.email"
            placeholder="请输入邮箱"
            size="large"
            prefix-icon="Message"
          />
        </el-form-item>
        
        <el-form-item prop="password">
          <el-input
            v-model="registerForm.password"
            type="password"
            placeholder="请输入密码"
            size="large"
            prefix-icon="Lock"
          />
        </el-form-item>
        
        <el-form-item prop="confirmPassword">
          <el-input
            v-model="registerForm.confirmPassword"
            type="password"
            placeholder="请确认密码"
            size="large"
            prefix-icon="Lock"
            @keyup.enter="handleRegister"
          />
        </el-form-item>
        
        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="authStore.loading"
            @click="handleRegister"
            class="register-button"
          >
            注册
          </el-button>
        </el-form-item>
        
        <div class="form-actions">
          <router-link to="/login" class="login-link">
            已有账号？立即登录
          </router-link>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useAuthStore } from '@/stores/auth'
import type { FormInstance, FormRules } from 'element-plus'

const authStore = useAuthStore()
const registerFormRef = ref<FormInstance>()

const registerForm = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
})

const validatePassword = (rule: any, value: any, callback: any) => {
  if (value === '') {
    callback(new Error('请输入密码'))
  } else if (value.length < 6) {
    callback(new Error('密码长度至少6位'))
  } else {
    if (registerForm.confirmPassword !== '') {
      registerFormRef.value?.validateField('confirmPassword')
    }
    callback()
  }
}

const validateConfirmPassword = (rule: any, value: any, callback: any) => {
  if (value === '') {
    callback(new Error('请再次输入密码'))
  } else if (value !== registerForm.password) {
    callback(new Error('两次输入密码不一致'))
  } else {
    callback()
  }
}

const registerRules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 50, message: '用户名长度在3-50个字符之间', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  password: [
    { validator: validatePassword, trigger: 'blur' }
  ],
  confirmPassword: [
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

const handleRegister = async () => {
  if (!registerFormRef.value) return
  
  try {
    await registerFormRef.value.validate()
    const { confirmPassword, ...registerData } = registerForm
    await authStore.register(registerData)
  } catch (error) {
    console.error('Register failed:', error)
  }
}
</script>

<style scoped>
.register-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.register-card {
  background: white;
  padding: 40px;
  border-radius: 16px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
  text-align: center;
}

.register-card h1 {
  color: #333;
  margin-bottom: 10px;
  font-size: 24px;
}

.register-card h2 {
  color: #666;
  margin-bottom: 30px;
  font-size: 18px;
  font-weight: normal;
}

.register-form {
  text-align: left;
}

.register-button {
  width: 100%;
  height: 44px;
  font-size: 16px;
}

.form-actions {
  text-align: center;
  margin-top: 20px;
}

.login-link {
  color: #667eea;
  text-decoration: none;
  font-size: 14px;
}

.login-link:hover {
  text-decoration: underline;
}
</style>