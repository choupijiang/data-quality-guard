<template>
  <div class="users-container">
    <div class="page-header">
      <h1>用户管理</h1>
      <el-button type="primary" @click="showCreateDialog = true">
        <el-icon><Plus /></el-icon>
        创建用户
      </el-button>
    </div>

    <!-- Users Table -->
    <el-card>
      <el-table :data="users" v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" />
        <el-table-column prop="email" label="邮箱" />
        <el-table-column prop="role" label="角色">
          <template #default="{ row }">
            <el-tag :type="getRoleTagType(row.role)">
              {{ getRoleLabel(row.role) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-button 
                size="small" 
                type="primary" 
                :icon="Edit"
                @click="editUser(row)"
                title="编辑用户"
              />
              <el-button 
                size="small" 
                type="danger" 
                :icon="Delete"
                @click="deleteUser(row)"
                title="删除用户"
                v-if="row.id !== currentUser?.id && row.username !== 'admin'"
              />
            </div>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- Create/Edit User Dialog -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingUser ? '编辑用户' : '创建用户'"
      :width="editingUser ? '600px' : '500px'"
    >
      <el-form
        ref="userFormRef"
        :model="userForm"
        :rules="userFormRules"
        label-width="80px"
      >
        <el-form-item label="用户名" prop="username">
          <el-input v-model="userForm.username" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="userForm.email" />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="userForm.role" style="width: 100%">
            <el-option label="系统管理员" value="SYSTEM_ADMIN" />
            <el-option label="项目管理员" value="PROJECT_ADMIN" />
            <el-option label="普通用户" value="REGULAR_USER" />
          </el-select>
        </el-form-item>
        <el-form-item label="密码" :prop="editingUser ? '' : 'password'">
          <el-input 
            v-model="userForm.password" 
            type="password" 
            :placeholder="editingUser ? '留空则不修改密码' : '请输入密码'"
          />
        </el-form-item>
        <el-form-item label="状态" prop="is_active">
          <el-switch v-model="userForm.is_active" />
        </el-form-item>
        
        <!-- 项目权限选择（仅在编辑用户时显示） -->
        <el-form-item label="项目权限" v-if="editingUser">
          <div class="project-permissions">
            <el-select
              v-model="selectedProjects"
              multiple
              placeholder="选择用户可以访问的项目"
              style="width: 100%"
              :loading="projectsLoading"
            >
              <el-option
                v-for="project in availableProjects"
                :key="project.id"
                :label="project.name"
                :value="project.id"
              />
            </el-select>
            <div class="permission-help" v-if="editingUser.role === 'SYSTEM_ADMIN'">
              <el-alert
                title="系统管理员拥有所有项目权限，无需单独分配"
                type="info"
                :closable="false"
                show-icon
              />
            </div>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="saveUser" :loading="saving">
          保存
        </el-button>
      </template>
    </el-dialog>

    </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Edit, Delete } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/utils/api'

interface User {
  id: number
  username: string
  email: string
  role: string
  is_active: boolean
  created_at: string
}

interface Project {
  id: number
  name: string
}


const authStore = useAuthStore()

const users = ref<User[]>([])
const loading = ref(false)
const saving = ref(false)
const showCreateDialog = ref(false)
const editingUser = ref<User | null>(null)

const selectedProjects = ref<number[]>([])
const projectsLoading = ref(false)
const availableProjects = ref<Project[]>([])

const userFormRef = ref()
const userForm = reactive({
  username: '',
  email: '',
  role: 'REGULAR_USER',
  password: '',
  is_active: true
})

const userFormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 50, message: '用户名长度在3-50个字符之间', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  role: [
    { required: true, message: '请选择角色', trigger: 'change' }
  ],
  password: [
    { 
      required: false, 
      validator: (rule: any, value: string, callback: any) => {
        if (!editingUser.value && !value) {
          callback(new Error('请输入密码'))
        } else if (value && value.length < 6) {
          callback(new Error('密码长度至少6位'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

const currentUser = computed(() => authStore.user)

const fetchUsers = async () => {
  loading.value = true
  try {
    console.log('[DEBUG] Starting to fetch users...')
    const response = await api.get('/api/v1/users')
    users.value = response.data
    console.log('[DEBUG] Users fetched successfully:', {
      count: users.value.length,
      users: users.value.map(u => ({ id: u.id, username: u.username, role: u.role, is_active: u.is_active }))
    })
  } catch (error: any) {
    console.error('[DEBUG] Failed to fetch users:', {
      error: error.message,
      response: error.response?.data,
      status: error.response?.status,
      config: error.config
    })
    const message = error.response?.data?.detail || error.message || '获取用户列表失败'
    ElMessage.error(`获取用户列表失败: ${message}`)
  } finally {
    loading.value = false
    console.log('[DEBUG] Fetch users completed, loading state:', loading.value)
  }
}

const fetchProjects = async () => {
  try {
    console.log('[DEBUG] Starting to fetch projects...')
    const response = await api.get('/api/v1/projects/')
    availableProjects.value = response.data
    console.log('[DEBUG] Projects fetched successfully:', {
      count: availableProjects.value.length,
      projects: availableProjects.value.map(p => ({ id: p.id, name: p.name }))
    })
  } catch (error: any) {
    console.error('[DEBUG] Failed to fetch projects:', {
      error: error.message,
      response: error.response?.data,
      status: error.response?.status
    })
    ElMessage.error('获取项目列表失败')
  }
}

const editUser = async (user: User) => {
  console.log('[DEBUG] Starting to edit user:', {
    userId: user.id,
    username: user.username,
    currentRole: user.role,
    isActive: user.is_active
  })
  
  editingUser.value = user
  userForm.username = user.username
  userForm.email = user.email
  userForm.role = user.role
  userForm.is_active = user.is_active
  userForm.password = ''
  
  console.log('[DEBUG] User form populated:', {
    username: userForm.username,
    email: userForm.email,
    role: userForm.role,
    isActive: userForm.is_active
  })
  
  // 加载用户的项目权限
  if (user.role !== 'SYSTEM_ADMIN') {
    console.log('[DEBUG] Loading user projects for non-admin user...')
    await loadUserProjects(user.id)
  } else {
    console.log('[DEBUG] User is SYSTEM_ADMIN, skipping project permissions load')
  }
  
  showCreateDialog.value = true
  console.log('[DEBUG] Edit dialog opened for user:', user.username)
}

const saveUser = async () => {
  if (!userFormRef.value) return
  
  try {
    console.log('[DEBUG] Starting to save user...')
    await userFormRef.value.validate()
    saving.value = true

    if (editingUser.value) {
      // 编辑用户 - 只有当密码不为空时才包含密码字段
      const userData: any = {
        username: userForm.username,
        email: userForm.email,
        role: userForm.role,
        is_active: userForm.is_active
      }
      
      // 如果密码字段不为空，则包含密码
      if (userForm.password) {
        userData.password = userForm.password
        console.log('[DEBUG] Including password in update (masked)')
      } else {
        console.log('[DEBUG] No password provided, skipping password update')
      }
      
      console.log('[DEBUG] Updating user:', {
        userId: editingUser.value.id,
        userData: { ...userData, password: userData.password ? '[MASKED]' : undefined },
        selectedProjects: selectedProjects.value
      })
      
      const response = await api.put(`/api/v1/users/${editingUser.value.id}`, userData)
      console.log('[DEBUG] User update response:', {
        status: response.status,
        data: response.data
      })
      
      // 更新项目权限（仅对非系统管理员）
      if (userForm.role !== 'SYSTEM_ADMIN') {
        console.log('[DEBUG] Updating project permissions for user:', editingUser.value.id)
        console.log('[DEBUG] Selected projects:', selectedProjects.value)
        await updateUserProjects(editingUser.value.id, selectedProjects.value)
        console.log('[DEBUG] Project permissions updated successfully')
      } else {
        console.log('[DEBUG] User is SYSTEM_ADMIN, skipping project permissions update')
      }
      
      ElMessage.success('用户更新成功')
    } else {
      // 创建新用户 - 必须包含密码
      const newUser = {
        username: userForm.username,
        email: userForm.email,
        role: userForm.role,
        is_active: userForm.is_active,
        password: userForm.password
      }
      
      console.log('[DEBUG] Creating new user:', {
        userData: { ...newUser, password: '[MASKED]' }
      })
      
      await api.post('/api/v1/auth/register', newUser)
      console.log('[DEBUG] New user created successfully')
      ElMessage.success('用户创建成功')
    }

    showCreateDialog.value = false
    resetForm()
    console.log('[DEBUG] Form reset, refreshing user list...')
    await fetchUsers()
  } catch (error: any) {
    console.error('[DEBUG] Failed to save user:', {
      error: error.message,
      response: error.response?.data,
      status: error.response?.status,
      config: error.config,
      userForm: userForm,
      editingUser: editingUser.value
    })
    const message = error.response?.data?.detail || '操作失败'
    ElMessage.error(message)
  } finally {
    saving.value = false
    console.log('[DEBUG] Save operation completed, saving state:', saving.value)
  }
}

const deleteUser = async (user: User) => {
  try {
    console.log('[DEBUG] Starting to delete user:', {
      userId: user.id,
      username: user.username,
      role: user.role
    })
    
    await ElMessageBox.confirm(
      `确定要删除用户 "${user.username}" 吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    console.log('[DEBUG] User confirmed deletion, sending delete request...')
    const response = await api.delete(`/api/v1/users/${user.id}`)
    console.log('[DEBUG] Delete user response:', {
      status: response.status,
      data: response.data
    })
    
    ElMessage.success('用户删除成功')
    console.log('[DEBUG] User deleted successfully, refreshing user list...')
    await fetchUsers()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('[DEBUG] Failed to delete user:', {
        userId: user.id,
        error: error.message,
        response: error.response?.data,
        status: error.response?.status
      })
      ElMessage.error('删除失败')
    } else {
      console.log('[DEBUG] User deletion cancelled by user')
    }
  }
}

// 加载用户的项目权限
const loadUserProjects = async (userId: number) => {
  console.log('[DEBUG] Starting to load user projects:', { userId })
  projectsLoading.value = true
  try {
    const response = await api.get(`/api/v1/users/${userId}/permissions`)
    selectedProjects.value = response.data.map((p: any) => p.project_id)
    console.log('[DEBUG] User projects loaded successfully:', {
      userId,
      projectCount: selectedProjects.value.length,
      projectIds: selectedProjects.value
    })
  } catch (error: any) {
    console.error('[DEBUG] Failed to load user projects:', {
      userId,
      error: error.message,
      response: error.response?.data,
      status: error.response?.status
    })
    ElMessage.error('获取用户项目权限失败')
  } finally {
    projectsLoading.value = false
    console.log('[DEBUG] Load user projects completed, loading state:', projectsLoading.value)
  }
}

// 更新用户的项目权限
const updateUserProjects = async (userId: number, projectIds: number[]) => {
  console.log('[DEBUG] Starting to update user projects:', {
    userId,
    targetProjectIds: projectIds
  })
  
  try {
    // 直接批量设置项目权限
    console.log('[DEBUG] Sending batch project permissions update:', {
      userId,
      projectIds
    })
    
    const response = await api.post(`/api/v1/users/${userId}/permissions`, {
      project_ids: projectIds
    })
    
    console.log('[DEBUG] User project permissions updated successfully:', {
      userId,
      response: response.data,
      finalProjectCount: projectIds.length
    })
  } catch (error: any) {
    console.error('[DEBUG] Failed to update user projects:', {
      userId,
      targetProjectIds: projectIds,
      error: error.message,
      response: error.response?.data,
      status: error.response?.status
    })
    ElMessage.error('更新项目权限失败')
    throw error
  }
}

const resetForm = () => {
  editingUser.value = null
  userForm.username = ''
  userForm.email = ''
  userForm.role = 'REGULAR_USER'
  userForm.password = ''
  userForm.is_active = true
  selectedProjects.value = []
}

const getRoleLabel = (role: string) => {
  const roleMap: Record<string, string> = {
    'SYSTEM_ADMIN': '系统管理员',
    'PROJECT_ADMIN': '项目管理员',
    'REGULAR_USER': '普通用户'
  }
  return roleMap[role] || role
}

const getRoleTagType = (role: string) => {
  const typeMap: Record<string, string> = {
    'SYSTEM_ADMIN': 'danger',
    'PROJECT_ADMIN': 'warning',
    'REGULAR_USER': 'success'
  }
  return typeMap[role] || 'info'
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleString()
}

// 调试工具函数
const debugTools = {
  // 打印当前组件状态
  logState: () => {
    console.log('[DEBUG] Current component state:', {
      users: users.value.map(u => ({ id: u.id, username: u.username, role: u.role })),
      loading: loading.value,
      saving: saving.value,
      showCreateDialog: showCreateDialog.value,
      editingUser: editingUser.value ? { id: editingUser.value.id, username: editingUser.value.username } : null,
      userForm: { ...userForm, password: userForm.password ? '[MASKED]' : null },
      selectedProjects: selectedProjects.value,
      availableProjects: availableProjects.value.map(p => ({ id: p.id, name: p.name })),
      projectsLoading: projectsLoading.value,
      currentUser: currentUser.value
    })
  },

  // 测试API连接
  testApiConnection: async () => {
    try {
      console.log('[DEBUG] Testing API connection...')
      const healthResponse = await api.get('/health')
      console.log('[DEBUG] API health check:', healthResponse.data)
      
      const userResponse = await api.get('/api/v1/auth/me')
      console.log('[DEBUG] Current user:', userResponse.data)
      
      return { success: true, health: healthResponse.data, user: userResponse.data }
    } catch (error: any) {
      console.error('[DEBUG] API connection test failed:', error)
      return { success: false, error: error.message }
    }
  },

  // 清空并重新加载数据
  resetAndReload: async () => {
    console.log('[DEBUG] Resetting and reloading data...')
    resetForm()
    await fetchUsers()
    await fetchProjects()
  }
}

// 全局调试函数，可以在浏览器控制台调用
;(window as any).__DEBUG_USERS_VIEW__ = debugTools

// MCP浏览器调试辅助函数
const mcpDebugTools = {
  // 启动浏览器并导航到用户管理页面
  async navigateToUsersPage() {
    console.log('[MCP DEBUG] Attempting to navigate to users page...')
    // 这个函数可以由MCP工具调用来启动浏览器调试
    return { url: 'http://localhost:5173/users' }
  },

  // 执行用户管理操作
  async performUserAction(action: string, params: any) {
    console.log('[MCP DEBUG] Performing user action:', action, params)
    // 这个函数可以由MCP工具调用来执行具体的用户操作
    return { action, params, status: 'ready' }
  },

  // 获取当前页面状态快照
  async getPageSnapshot() {
    console.log('[MCP DEBUG] Getting page snapshot...')
    // 这个函数可以由MCP工具调用来获取页面状态
    return {
      users: users.value.map(u => ({ id: u.id, username: u.username, role: u.role })),
      dialogOpen: showCreateDialog.value,
      loadingStates: {
        main: loading.value,
        saving: saving.value,
        projects: projectsLoading.value
      }
    }
  }
}

// 暴露MCP调试工具给全局
;(window as any).__MCP_USERS_DEBUG__ = mcpDebugTools

onMounted(async () => {
  console.log('[DEBUG] UsersView component mounted')
  await fetchUsers()
  await fetchProjects()
  debugTools.logState()
})
</script>

<style scoped>
.users-container {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h1 {
  margin: 0;
  color: #333;
}

.permissions-content {
  padding: 20px 0;
}

.user-info {
  margin-bottom: 20px;
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 8px;
}

.user-info h3 {
  margin: 0;
  color: #333;
}

.permissions-section {
  margin-bottom: 20px;
}

.project-permissions {
  width: 100%;
}

.permission-help {
  margin-top: 10px;
}

.action-buttons {
  display: flex;
  gap: 8px;
  align-items: center;
}

.action-buttons .el-button {
  min-width: 32px;
  padding: 6px;
}
</style>