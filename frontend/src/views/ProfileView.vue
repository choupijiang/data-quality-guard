<template>
  <div class="profile-container">
    <div class="page-header">
      <el-button @click="goBack" type="text" class="back-button">
        <el-icon><ArrowLeft /></el-icon>
        返回
      </el-button>
      <h1>个人信息</h1>
    </div>

    <el-card class="profile-card">
      <div class="profile-content">
        <!-- 用户头像区域 -->
        <div class="avatar-section">
          <div class="user-avatar" :style="{ backgroundColor: userAvatar.backgroundColor }">
            {{ userAvatar.initial }}
          </div>
          <div class="avatar-info">
            <h3>{{ currentUser?.username }}</h3>
            <p>{{ getRoleLabel(currentUser?.role) }}</p>
          </div>
        </div>

        <!-- 个人信息表单 -->
        <el-form
          ref="profileFormRef"
          :model="profileForm"
          :rules="profileFormRules"
          label-width="100px"
          class="profile-form"
        >
          <el-form-item label="用户名">
            <el-input 
              v-model="profileForm.username" 
              disabled
              placeholder="用户名不可修改"
            />
            <div class="help-text">用户名创建后不可修改</div>
          </el-form-item>

          <el-form-item label="邮箱" prop="email">
            <el-input 
              v-model="profileForm.email" 
              placeholder="请输入邮箱地址"
              :prefix-icon="Message"
            />
          </el-form-item>

          <el-form-item label="角色">
            <el-input 
              :value="getRoleLabel(currentUser?.role)" 
              disabled
              placeholder="系统分配的角色"
            />
          </el-form-item>

          <el-divider>修改密码</el-divider>

          <el-form-item label="当前密码" prop="currentPassword" v-if="showPasswordFields">
            <el-input 
              v-model="profileForm.currentPassword"
              type="password"
              placeholder="请输入当前密码"
              :prefix-icon="Lock"
              show-password
            />
          </el-form-item>

          <el-form-item label="新密码" prop="newPassword" v-if="showPasswordFields">
            <el-input 
              v-model="profileForm.newPassword"
              type="password"
              placeholder="请输入新密码（留空则不修改）"
              :prefix-icon="Lock"
              show-password
            />
            <div class="help-text">密码长度至少6位</div>
          </el-form-item>

          <el-form-item label="确认密码" prop="confirmPassword" v-if="showPasswordFields">
            <el-input 
              v-model="profileForm.confirmPassword"
              type="password"
              placeholder="请再次输入新密码"
              :prefix-icon="Lock"
              show-password
            />
          </el-form-item>

          <el-form-item>
            <el-button 
              v-if="!showPasswordFields"
              @click="showPasswordFields = true"
              type="primary"
              plain
            >
              修改密码
            </el-button>
            <el-button 
              v-else
              @click="showPasswordFields = false"
              type="info"
              plain
            >
              取消修改密码
            </el-button>
          </el-form-item>
        </el-form>

        <!-- 操作按钮 -->
        <div class="form-actions">
          <el-button @click="goBack">取消</el-button>
          <el-button 
            type="primary" 
            @click="saveProfile" 
            :loading="saving"
          >
            保存更改
          </el-button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, Message, Lock } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/utils/api'

const router = useRouter()
const authStore = useAuthStore()

const profileFormRef = ref()
const saving = ref(false)
const showPasswordFields = ref(false)

const currentUser = computed(() => authStore.user)

// 生成用户头像
const generateUserAvatar = (username: string) => {
  const colors = [
    '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57',
    '#FF9FF3', '#54A0FF', '#5F27CD', '#00D2D3', '#FF9F43',
    '#10AC84', '#EE5A24', '#0652DD', '#9C88FF', '#FFC312'
  ]
  
  let hash = 0
  for (let i = 0; i < username.length; i++) {
    hash = username.charCodeAt(i) + ((hash << 5) - hash)
  }
  
  const colorIndex = Math.abs(hash) % colors.length
  const backgroundColor = colors[colorIndex]
  const initial = username.charAt(0).toUpperCase()
  
  return { backgroundColor, initial }
}

const userAvatar = computed(() => {
  if (currentUser.value?.username) {
    return generateUserAvatar(currentUser.value.username)
  }
  return { backgroundColor: '#E0E0E0', initial: 'U' }
})

const profileForm = reactive({
  username: '',
  email: '',
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const profileFormRules = {
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  currentPassword: [
    { 
      required: false, 
      validator: (rule: any, value: string, callback: any) => {
        if (showPasswordFields.value && profileForm.newPassword && !value) {
          callback(new Error('请输入当前密码以修改密码'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
  newPassword: [
    { 
      required: false, 
      validator: (rule: any, value: string, callback: any) => {
        if (showPasswordFields.value && value) {
          if (value.length < 6) {
            callback(new Error('密码长度至少6位'))
          } else {
            callback()
          }
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
  confirmPassword: [
    { 
      required: false, 
      validator: (rule: any, value: string, callback: any) => {
        if (showPasswordFields.value && profileForm.newPassword) {
          if (!value) {
            callback(new Error('请确认密码'))
          } else if (value !== profileForm.newPassword) {
            callback(new Error('两次输入的密码不一致'))
          } else {
            callback()
          }
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

const loadUserProfile = () => {
  if (currentUser.value) {
    profileForm.username = currentUser.value.username
    profileForm.email = currentUser.value.email
  }
}

const getRoleLabel = (role?: string) => {
  const roleMap: Record<string, string> = {
    'SYSTEM_ADMIN': '系统管理员',
    'PROJECT_ADMIN': '项目管理员',
    'REGULAR_USER': '普通用户'
  }
  return roleMap[role || ''] || '未知角色'
}

const saveProfile = async () => {
  if (!profileFormRef.value) return
  
  try {
    await profileFormRef.value.validate()
    saving.value = true

    const updateData: any = {
      email: profileForm.email
    }

    // 如果填写了新密码，则包含密码更新（需要当前密码验证）
    if (showPasswordFields.value && profileForm.newPassword) {
      if (!profileForm.currentPassword) {
        throw new Error('请输入当前密码以修改密码')
      }
      updateData.password = profileForm.newPassword
    }

    console.log('Updating user profile:', {
      userId: currentUser.value?.id,
      updateData: { ...updateData, password: updateData.password ? '[MASKED]' : undefined }
    })

    const response = await api.put('/api/v1/users/me', updateData)
    
    console.log('Profile update response:', response.data)

    // 更新本地存储的用户信息
    if (response.data) {
      authStore.setUser(response.data)
    }

    ElMessage.success('个人信息更新成功')
    
    // 重置密码字段
    profileForm.currentPassword = ''
    profileForm.newPassword = ''
    profileForm.confirmPassword = ''
    showPasswordFields.value = false

    // 返回上一页
    goBack()
  } catch (error: unknown) {
    console.error('Failed to update profile:', error)
    
    const errorMessage = error instanceof Error ? error.message : '更新失败，请检查输入信息'
    ElMessage.error(errorMessage)
  } finally {
    saving.value = false
  }
}

const goBack = () => {
  router.back()
}

onMounted(() => {
  loadUserProfile()
})
</script>

<style scoped>
.profile-container {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  align-items: center;
  margin-bottom: 30px;
}

.page-header h1 {
  margin: 0;
  margin-left: 20px;
  color: #333;
}

.back-button {
  padding: 8px;
  font-size: 14px;
}

.profile-card {
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.profile-content {
  padding: 20px;
}

.avatar-section {
  display: flex;
  align-items: center;
  margin-bottom: 40px;
  padding-bottom: 20px;
  border-bottom: 1px solid #eee;
}

.user-avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  font-size: 32px;
  text-transform: uppercase;
  flex-shrink: 0;
  margin-right: 20px;
  border: 3px solid #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.avatar-info h3 {
  margin: 0 0 5px 0;
  font-size: 24px;
  color: #333;
}

.avatar-info p {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.profile-form {
  max-width: 500px;
  margin: 0 auto;
}

.help-text {
  font-size: 12px;
  color: #999;
  margin-top: 4px;
  line-height: 1.4;
}

.form-actions {
  display: flex;
  justify-content: center;
  gap: 12px;
  margin-top: 40px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .profile-container {
    padding: 16px;
  }
  
  .avatar-section {
    flex-direction: column;
    text-align: center;
    margin-bottom: 30px;
  }
  
  .user-avatar {
    margin-right: 0;
    margin-bottom: 15px;
  }
  
  .profile-form {
    padding: 0 10px;
  }
  
  .form-actions {
    flex-direction: column;
  }
  
  .form-actions .el-button {
    width: 100%;
  }
}
</style>