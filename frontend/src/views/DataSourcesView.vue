<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { Connection, Plus, Edit, Refresh, Check, Setting, Delete, Search } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/utils/api'

interface DataSource {
  id: number
  name: string
  type: string
  host: string
  port: number
  database: string
  username: string
  status: string
  created_at: string
}

interface DatabaseType {
  id: string
  name: string
  icon: string
  color: string
  description: string
  defaultPort: number
  configFields: ConfigField[]
}

interface ConfigField {
  name: string
  label: string
  type: 'text' | 'password' | 'number'
  required: boolean
  placeholder: string
}

const router = useRouter()
const dataSources = ref<DataSource[]>([])
const loading = ref(false)
const searchQuery = ref('')
const typeFilter = ref('')
const statusFilter = ref('')
const sortBy = ref('created_at')
const showConfigModal = ref(false)
const selectedDbType = ref<DatabaseType | null>(null)
const isEditing = ref(false)
const editingSource = ref<DataSource | null>(null)

const configForm = ref<Record<string, string>>({
  name: '',
  host: '',
  port: '',
  database: '',
  username: '',
  password: ''
})

const databaseTypes: DatabaseType[] = [
  {
    id: 'mysql',
    name: 'MySQL',
    icon: '🐬',
    color: '#4479A1',
    description: '最流行的开源关系型数据库',
    defaultPort: 3306,
    configFields: [
      { name: 'name', label: '连接名称', type: 'text', required: true, placeholder: '输入连接名称' },
      { name: 'host', label: '主机地址', type: 'text', required: true, placeholder: 'localhost' },
      { name: 'port', label: '端口号', type: 'number', required: true, placeholder: '3306' },
      { name: 'database', label: '数据库名', type: 'text', required: true, placeholder: 'mysql' },
      { name: 'username', label: '用户名', type: 'text', required: true, placeholder: 'root' },
      { name: 'password', label: '密码', type: 'password', required: true, placeholder: '••••••••' }
    ]
  },
  {
    id: 'clickhouse',
    name: 'ClickHouse',
    icon: '🚀',
    color: '#FFCC00',
    description: '面向列的开源OLAP数据库系统',
    defaultPort: 8123,
    configFields: [
      { name: 'name', label: '连接名称', type: 'text', required: true, placeholder: '输入连接名称' },
      { name: 'host', label: '主机地址', type: 'text', required: true, placeholder: 'localhost' },
      { name: 'port', label: '端口号', type: 'number', required: true, placeholder: '8123' },
      { name: 'database', label: '数据库名', type: 'text', required: true, placeholder: 'default' },
      { name: 'username', label: '用户名', type: 'text', required: false, placeholder: 'default' },
      { name: 'password', label: '密码', type: 'password', required: false, placeholder: '••••••••' }
    ]
  },
  {
    id: 'postgresql',
    name: 'PostgreSQL',
    icon: '🐘',
    color: '#336791',
    description: '强大的开源对象关系型数据库系统',
    defaultPort: 5432,
    configFields: [
      { name: 'name', label: '连接名称', type: 'text', required: true, placeholder: '输入连接名称' },
      { name: 'host', label: '主机地址', type: 'text', required: true, placeholder: 'localhost' },
      { name: 'port', label: '端口号', type: 'number', required: true, placeholder: '5432' },
      { name: 'database', label: '数据库名', type: 'text', required: true, placeholder: 'postgres' },
      { name: 'username', label: '用户名', type: 'text', required: true, placeholder: 'postgres' },
      { name: 'password', label: '密码', type: 'password', required: true, placeholder: '••••••••' }
    ]
  },
  {
    id: 'starrocks',
    name: 'StarRocks',
    icon: '⭐',
    color: '#0066CC',
    description: '新一代极速全场景分析型数据库',
    defaultPort: 9030,
    configFields: [
      { name: 'name', label: '连接名称', type: 'text', required: true, placeholder: '输入连接名称' },
      { name: 'host', label: '主机地址', type: 'text', required: true, placeholder: 'localhost' },
      { name: 'port', label: '端口号', type: 'number', required: true, placeholder: '9030' },
      { name: 'database', label: '数据库名', type: 'text', required: true, placeholder: '数据库名称' },
      { name: 'username', label: '用户名', type: 'text', required: true, placeholder: 'root' },
      { name: 'password', label: '密码', type: 'password', required: true, placeholder: '••••••••' }
    ]
  }
]

onMounted(() => {
  fetchDataSources()
})

const fetchDataSources = async () => {
  loading.value = true
  try {
    const response = await api.get('/api/v1/data-sources/')
    dataSources.value = response.data || []
  } catch {
    ElMessage.error('获取数据源失败')
  } finally {
    loading.value = false
  }
}

// Computed properties
const filteredDataSources = computed(() => {
  let filtered = [...dataSources.value]

  // 搜索过滤
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(source => 
      source.name.toLowerCase().includes(query) ||
      source.type.toLowerCase().includes(query) ||
      source.host.toLowerCase().includes(query) ||
      source.database.toLowerCase().includes(query)
    )
  }

  // 类型过滤
  if (typeFilter.value) {
    filtered = filtered.filter(source => source.type === typeFilter.value)
  }

  // 状态过滤
  if (statusFilter.value) {
    filtered = filtered.filter(source => source.status === statusFilter.value)
  }

  // 排序
  filtered.sort((a, b) => {
    switch (sortBy.value) {
      case 'name':
        return a.name.localeCompare(b.name)
      case 'type':
        return a.type.localeCompare(b.type)
      case 'created_at':
      default:
        return new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    }
  })

  return filtered
})

const hasActiveFilters = computed(() => {
  return searchQuery.value || typeFilter.value || statusFilter.value
})

const clearFilters = () => {
  searchQuery.value = ''
  typeFilter.value = ''
  statusFilter.value = ''
  sortBy.value = 'created_at'
}

const testConnection = async (id: number) => {
  try {
    const response = await api.post(`/api/v1/data-sources/${id}/test`)
    const result = response.data.connection_successful
    
    if (result) {
      ElMessage.success('连接测试成功')
      // 刷新数据源列表以更新状态
      fetchDataSources()
    } else {
      ElMessage.error('连接测试失败')
    }
  } catch (error: any) {
    // 处理HTTP错误
    if (error.response) {
      const status = error.response.status
      if (status === 404) {
        ElMessage.error('数据源不存在')
      } else {
        ElMessage.error(`连接测试失败 (${status})`)
      }
    } else {
      ElMessage.error('网络连接失败')
    }
  }
}

const testCurrentConnection = async () => {
  if (!selectedDbType.value || !editingSource.value) return
  
  try {
    loading.value = true
    
    // 使用当前表单配置测试连接（编辑模式）
    const testConfig = {
      type: selectedDbType.value.id,
      ...configForm.value,
      port: parseInt(configForm.value.port)
    }
    
    const response = await api.post('/api/v1/data-sources/test-connection', testConfig)
    const result = response.data.connection_successful
    
    if (result) {
      ElMessage.success('连接测试成功')
    } else {
      ElMessage.error('连接测试失败 - 请检查连接配置')
    }
  } catch (error: any) {
    if (error.response) {
      const status = error.response.status
      if (status === 400) {
        ElMessage.error('配置格式错误：' + (error.response.data?.detail || '请检查输入信息'))
      } else {
        ElMessage.error(`连接测试失败 (${status})`)
      }
    } else {
      ElMessage.error('网络连接失败，请检查网络设置')
    }
  } finally {
    loading.value = false
  }
}

const selectDatabaseType = (dbType: DatabaseType | null) => {
  selectedDbType.value = dbType
  if (dbType) {
    // 预填充表单
    configForm.value = {
      name: '',
      host: 'localhost',
      port: dbType.defaultPort.toString(),
      database: '',
      username: '',
      password: ''
    }
  } else {
    // 显示数据库类型选择
    showDatabaseSelection.value = true
  }
  isEditing.value = false
  editingSource.value = null
  showConfigModal.value = true
}

const editDataSource = (source: DataSource) => {
  selectedDbType.value = databaseTypes.find(db => db.id === source.type) || null
  configForm.value = {
    name: source.name,
    host: source.host,
    port: source.port.toString(),
    database: source.database,
    username: source.username,
    password: ''
  }
  isEditing.value = true
  editingSource.value = source
  showConfigModal.value = true
}

const deleteDataSource = async (id: number) => {
  try {
    await ElMessageBox.confirm('确定要删除这个数据源吗？此操作不可恢复。', '确认删除', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning',
    })
    
    await api.delete(`/api/v1/data-sources/${id}`)
    ElMessage.success('删除成功')
    fetchDataSources()
  } catch {
    // 用户取消删除
  }
}

const saveDataSource = async () => {
  if (!selectedDbType.value) return

  try {
    const payload = {
      ...configForm.value,
      type: selectedDbType.value.id,
      port: parseInt(configForm.value.port)
    }

    if (isEditing.value && editingSource.value) {
      await api.put(`/api/v1/data-sources/${editingSource.value.id}`, payload)
      ElMessage.success('更新成功')
    } else {
      await api.post('/api/v1/data-sources/', payload)
      ElMessage.success('创建成功')
    }

    showConfigModal.value = false
    fetchDataSources()
  } catch (error: any) {
    // 改进的错误处理
    if (error.response) {
      // 服务器返回了错误响应
      const status = error.response.status
      const detail = error.response.data?.detail || error.response.data?.message
      
      if (status === 404) {
        ElMessage.error('数据源不存在或已被删除')
      } else if (status === 403) {
        ElMessage.error('您没有权限修改此数据源')
      } else if (status === 400) {
        ElMessage.error(detail || '请求数据格式错误')
      } else if (status === 500) {
        ElMessage.error('服务器内部错误，请稍后重试')
      } else {
        ElMessage.error(detail || `操作失败 (${status})`)
      }
    } else if (error.request) {
      // 请求已发送但没有收到响应
      ElMessage.error('网络连接失败，请检查网络设置')
    } else {
      // 请求配置错误
      ElMessage.error(error.message || '操作失败')
    }
  }
}

const resetForm = () => {
  configForm.value = {
    name: '',
    host: '',
    port: '',
    database: '',
    username: '',
    password: ''
  }
  selectedDbType.value = null
  isEditing.value = false
  editingSource.value = null
}

const handleModalClose = (done: () => void) => {
  resetForm()
  done()
}

// Helper functions
const getDbTypeIcon = (type: string) => {
  const dbType = databaseTypes.find(db => db.id === type)
  return dbType?.icon || '📊'
}

const getDbTypeColor = (type: string) => {
  const dbType = databaseTypes.find(db => db.id === type)
  return dbType?.color || '#6B7280'
}

const getTypeLabel = (type: string) => {
  const dbType = databaseTypes.find(db => db.id === type)
  return dbType?.name || type
}

const getStatusText = (status: string) => {
  switch (status) {
    case 'active': return '在线'
    case 'inactive': return '离线'
    case 'error': return '错误'
    default: return status
  }
}

const getStatusColor = (status: string) => {
  switch (status) {
    case 'active': return '#10B981'
    case 'inactive': return '#6B7280'
    case 'error': return '#EF4444'
    default: return '#6B7280'
  }
}

const getStatusTagType = (status: string) => {
  switch (status) {
    case 'active': return 'success'
    case 'inactive': return 'info'
    case 'error': return 'danger'
    default: return 'info'
  }
}

const getStatusLabel = (status: string) => {
  switch (status) {
    case 'active': return '在线'
    case 'inactive': return '离线'
    case 'error': return '错误'
    default: return status
  }
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('zh-CN')
}

const showDatabaseSelection = ref(false)
</script>

<template>
  <div class="data-sources-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-info">
          <h1 class="page-title">数据源</h1>
          <p class="page-description">管理数据库连接</p>
        </div>
        <div class="header-actions">
          <button class="apple-button apple-button-primary create-data-source-btn" @click="router.push('/data-sources/create')">
            <el-icon><Plus /></el-icon>
            创建数据源
          </button>
        </div>
      </div>
    </div>

    <!-- Filter Section -->
    <div class="filter-card">
      <div class="filter-header">
        <div class="filter-title">
          <el-icon><Search /></el-icon>
          <span>搜索与筛选</span>
        </div>
        <div class="filter-stats" v-if="hasActiveFilters">
          <span class="results-count">{{ filteredDataSources.length }} 个结果</span>
        </div>
      </div>
      <div class="filter-content">
        <div class="filter-row">
          <div class="search-container">
            <div class="search-icon">
              <el-icon><Search /></el-icon>
            </div>
            <el-input
              v-model="searchQuery"
              placeholder="搜索数据源名称或地址..."
              class="search-input"
              clearable
            />
          </div>
          
          <div class="filter-controls">
            <el-select v-model="typeFilter" placeholder="数据库类型" clearable class="filter-select">
              <el-option label="MySQL" value="mysql" />
              <el-option label="ClickHouse" value="clickhouse" />
              <el-option label="PostgreSQL" value="postgresql" />
              <el-option label="StarRocks" value="starrocks" />
            </el-select>
            
            <el-select v-model="statusFilter" placeholder="连接状态" clearable class="filter-select">
              <el-option label="在线" value="active" />
              <el-option label="离线" value="inactive" />
              <el-option label="错误" value="error" />
            </el-select>
            
            <el-select v-model="sortBy" placeholder="排序方式" class="filter-select">
              <el-option label="创建时间" value="created_at" />
              <el-option label="名称" value="name" />
              <el-option label="类型" value="type" />
            </el-select>
            
            <button class="apple-button apple-button-secondary" @click="clearFilters">
              <el-icon><Refresh /></el-icon>
              重置
            </button>
          </div>
        </div>
        
        <!-- Active Filters -->
        <div v-if="hasActiveFilters" class="active-filters">
          <div class="active-filters-title">当前筛选:</div>
          <div class="active-filter-tags">
            <el-tag 
              v-if="searchQuery" 
              type="info" 
              size="small" 
              closable 
              @close="searchQuery = ''"
            >
              搜索: {{ searchQuery }}
            </el-tag>
            <el-tag 
              v-if="typeFilter" 
              type="success" 
              size="small" 
              closable 
              @close="typeFilter = ''"
            >
              类型: {{ getTypeLabel(typeFilter) }}
            </el-tag>
            <el-tag 
              v-if="statusFilter" 
              :type="getStatusTagType(statusFilter)" 
              size="small" 
              closable 
              @close="statusFilter = ''"
            >
              状态: {{ getStatusLabel(statusFilter) }}
            </el-tag>
          </div>
        </div>
      </div>
    </div>

    <!-- Data Sources Table -->
    <div v-if="filteredDataSources.length > 0" class="data-sources-table-container">
      <el-table 
        :data="filteredDataSources" 
        class="data-sources-table"
        :header-cell-style="{ backgroundColor: 'rgba(248, 249, 250, 0.8)', fontWeight: '600' }"
        :row-style="{ backgroundColor: 'rgba(255, 255, 255, 0.9)' }"
      >
        <!-- 数据源信息列 -->
        <el-table-column label="数据源" min-width="180">
          <template #default="{ row }">
            <div class="table-source-info">
              <div class="source-icon" :style="{ backgroundColor: getDbTypeColor(row.type) }">
                <span class="icon-emoji">{{ getDbTypeIcon(row.type) }}</span>
              </div>
              <div class="source-details">
                <div class="source-name">{{ row.name }}</div>
                <div class="source-type">{{ getTypeLabel(row.type) }}</div>
              </div>
            </div>
          </template>
        </el-table-column>

        <!-- 连接地址列 -->
        <el-table-column label="连接地址" min-width="140">
          <template #default="{ row }">
            <div class="host-port">{{ row.host }}:{{ row.port }}</div>
          </template>
        </el-table-column>

        <!-- 数据库名列 -->
        <el-table-column label="数据库名" min-width="120">
          <template #default="{ row }">
            <div class="database-name">{{ row.database }}</div>
          </template>
        </el-table-column>

        <!-- 用户信息列 -->
        <el-table-column label="用户信息" width="120">
          <template #default="{ row }">
            <div class="user-info">
              <div class="username">{{ row.username }}</div>
            </div>
          </template>
        </el-table-column>

        <!-- 状态列 -->
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <div class="status-indicator">
              <div class="status-dot" :class="{
                active: row.status === 'active',
                inactive: row.status === 'inactive',
                error: row.status === 'error'
              }"></div>
              <span class="status-text" :style="{ color: getStatusColor(row.status) }">
                {{ getStatusText(row.status) }}
              </span>
            </div>
          </template>
        </el-table-column>

        <!-- 更新时间列 -->
        <el-table-column label="更新时间" width="140">
          <template #default="{ row }">
            <div class="update-time">
              {{ formatDate(row.updated_at || row.created_at) }}
            </div>
          </template>
        </el-table-column>

        <!-- 操作列 -->
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <div class="table-actions">
              <button class="apple-button apple-button-secondary table-btn" @click="testConnection(row.id)">
                <el-icon><Connection /></el-icon>
                测试连接
              </button>
              <button class="apple-button apple-button-secondary table-btn" @click="editDataSource(row)">
                <el-icon><Edit /></el-icon>
                编辑
              </button>
              <button class="action-btn delete-btn table-btn" @click="deleteDataSource(row.id)" title="删除数据源">
                <el-icon><Delete /></el-icon>
              </button>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- Empty State -->
    <div v-if="filteredDataSources.length === 0 && !loading" class="empty-state">
      <div class="empty-icon">
        <el-icon><Connection /></el-icon>
      </div>
      <h3 class="empty-title">暂无数据源</h3>
      <p class="empty-description">创建您的第一个数据库连接</p>
      <button class="apple-button apple-button-primary" @click="router.push('/data-sources/create')">
        <el-icon><Plus /></el-icon>
        创建数据源
      </button>
    </div>

    <!-- Database Type Selection Modal -->
    <el-dialog
      v-model="showDatabaseSelection"
      title="选择数据库类型"
      width="600px"
      :before-close="() => { showDatabaseSelection = false }"
      class="database-selection-modal"
    >
      <div class="database-grid">
        <div 
          v-for="dbType in databaseTypes" 
          :key="dbType.id"
          class="database-card"
          @click="selectDatabaseType(dbType)"
        >
          <div class="database-icon" :style="{ backgroundColor: dbType.color }">
            <span class="icon-emoji">{{ dbType.icon }}</span>
          </div>
          <div class="database-info">
            <h3 class="database-name">{{ dbType.name }}</h3>
            <p class="database-description">{{ dbType.description }}</p>
            <div class="database-port">默认端口: {{ dbType.defaultPort }}</div>
          </div>
          <div class="database-arrow">
            <el-icon><Setting /></el-icon>
          </div>
        </div>
      </div>
    </el-dialog>

    <!-- Configuration Modal -->
    <el-dialog
      v-model="showConfigModal"
      :title="isEditing ? '编辑数据源' : '添加数据源'"
      width="600px"
      :before-close="handleModalClose"
      class="config-modal"
    >
      <div v-if="selectedDbType" class="config-form">
        <div class="db-type-info">
          <div class="db-type-icon" :style="{ backgroundColor: selectedDbType.color }">
            <span class="icon-emoji">{{ selectedDbType.icon }}</span>
          </div>
          <div class="db-type-details">
            <h4>{{ selectedDbType.name }}</h4>
            <p>{{ selectedDbType.description }}</p>
          </div>
        </div>

        <el-form :model="configForm" label-width="120px" label-position="left">
          <el-form-item 
            v-for="field in selectedDbType.configFields" 
            :key="field.name"
            :label="field.label"
            :required="field.required"
          >
            <el-input
              v-model="configForm[field.name]"
              :type="field.type"
              :placeholder="field.placeholder"
              :show-password="field.type === 'password'"
            />
          </el-form-item>
        </el-form>

        <div class="form-actions">
          <button class="apple-button apple-button-secondary" @click="showConfigModal = false">
            取消
          </button>
          <button v-if="isEditing" class="apple-button apple-button-secondary" @click="testCurrentConnection" :disabled="loading">
            <el-icon><Connection /></el-icon>
            测试连接
          </button>
          <button class="apple-button apple-button-primary" @click="saveDataSource" :disabled="loading">
            <el-icon><Check /></el-icon>
            {{ isEditing ? '更新' : '创建' }}
          </button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<style scoped>
/* CSS Variables */
:root {
  --spacing-xs: 4px;
  --spacing-sm: 8px;
  --spacing-md: 12px;
  --spacing-lg: 16px;
  --spacing-xl: 24px;
  --spacing-xxl: 32px;
  
  --radius-sm: 6px;
  --radius-md: 8px;
  --radius-lg: 12px;
  
  --font-size-xs: 12px;
  --font-size-sm: 14px;
  --font-size-base: 16px;
  --font-size-lg: 18px;
  
  --transition-fast: 150ms;
  --transition-normal: 300ms;
  
  --gray-1: #111827;
  --gray-2: #1F2937;
  --gray-3: #374151;
  --gray-4: #6B7280;
  --gray-5: #9CA3AF;
  --gray-6: #D1D5DB;
  --gray-7: #E5E7EB;
  --gray-8: #F3F4F6;
  --gray-9: #F9FAFB;
  --gray-10: #FFFFFF;
  --gray-11: rgba(255, 255, 255, 0.95);
  
  --apple-blue: #007AFF;
  --apple-blue-dark: #0051D5;
  --apple-red: #FF3B30;
  --apple-red-dark: #D70015;
  --apple-green: #34C759;
  --apple-orange: #FF9500;
  
  --success-color: #10B981;
  --error-color: #EF4444;
  --warning-color: #F59E0B;
}

/* Data Sources Container - Enhanced */
.data-sources-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  position: relative;
}

.data-sources-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: 
    radial-gradient(circle at 20% 20%, rgba(0, 122, 255, 0.03) 0%, transparent 50%),
    radial-gradient(circle at 80% 80%, rgba(52, 199, 89, 0.03) 0%, transparent 50%),
    radial-gradient(circle at 40% 60%, rgba(255, 149, 0, 0.02) 0%, transparent 50%);
  pointer-events: none;
  z-index: 0;
}

/* Page Header - Enhanced */
.page-header {
  padding: var(--spacing-xl) 0;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(248, 248, 248, 0.95) 100%);
  border-bottom: 1px solid var(--gray-9);
  backdrop-filter: blur(20px);
  position: relative;
  z-index: 1;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 var(--spacing-xl);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-info h1 {
  font-size: 2rem;
  font-weight: 600;
  color: var(--gray-1);
  margin: 0 0 var(--spacing-xs) 0;
  background: linear-gradient(135deg, var(--gray-1) 0%, var(--gray-3) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.header-info p {
  color: var(--gray-5);
  margin: 0;
  font-size: var(--font-size-lg);
}

.header-actions {
  display: flex;
  gap: var(--spacing-md);
  align-items: center;
}

/* Enhanced button styling for better visibility */
.header-actions .apple-button {
  font-weight: 700;
  padding: 12px 24px;
  font-size: 16px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 122, 255, 0.4);
  transition: all 0.3s ease;
  border: 2px solid #0051d5;
  text-transform: none;
  letter-spacing: 0.5px;
}

.header-actions .apple-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 122, 255, 0.6);
  background: #0051d5;
}

/* Specific styling for create data source button */
.create-data-source-btn {
  background: #007aff !important;
  color: white !important;
  border: 2px solid #0051d5 !important;
  font-weight: 700 !important;
  font-size: 16px !important;
  padding: 12px 24px !important;
  border-radius: 8px !important;
  box-shadow: 0 4px 12px rgba(0, 122, 255, 0.4) !important;
  min-width: 140px;
  height: 44px;
}

.create-data-source-btn:hover {
  background: #0051d5 !important;
  transform: translateY(-2px) !important;
  box-shadow: 0 6px 20px rgba(0, 122, 255, 0.6) !important;
}

/* Filter Card - Enhanced */
.filter-card {
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid var(--gray-9);
  border-radius: var(--radius-lg);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  backdrop-filter: blur(20px);
  position: relative;
  z-index: 1;
  margin: var(--spacing-xl) auto;
  max-width: 1200px;
  padding: var(--spacing-lg);
}

.filter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-lg);
  padding-bottom: var(--spacing-md);
  border-bottom: 1px solid var(--gray-8);
}

.filter-title {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  font-weight: 600;
  color: var(--gray-2);
  font-size: var(--font-size-lg);
}

.filter-stats {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.results-count {
  background: linear-gradient(135deg, var(--apple-blue) 0%, var(--apple-blue-dark) 100%);
  color: white;
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--radius-md);
  font-size: var(--font-size-sm);
  font-weight: 500;
}

.filter-content {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.filter-row {
  display: flex;
  gap: var(--spacing-lg);
  align-items: center;
  flex-wrap: wrap;
}

.search-container {
  position: relative;
  display: flex;
  align-items: center;
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid var(--gray-8);
  border-radius: var(--radius-lg);
  padding: var(--spacing-sm) var(--spacing-md);
  transition: all var(--transition-normal);
  min-width: 300px;
  max-width: 450px;
  flex: 2;
  height: 42px;
  backdrop-filter: blur(10px);
}

.search-container:focus-within {
  border-color: var(--apple-blue);
  box-shadow: 0 0 0 3px rgba(0, 122, 255, 0.1);
  background: rgba(255, 255, 255, 0.95);
}

.search-icon {
  color: var(--gray-4);
  margin-right: var(--spacing-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  transition: color var(--transition-normal);
  z-index: 1;
}

.search-container:focus-within .search-icon {
  color: var(--apple-blue);
}

.search-input {
  flex: 1;
  border: none;
  background: transparent;
}

.search-input .el-input__wrapper {
  box-shadow: none !important;
  background: transparent !important;
  padding: 0;
  border: none !important;
}

.search-input .el-input__inner {
  color: var(--gray-1);
  font-size: var(--font-size-base);
  height: auto;
  line-height: 1.5;
  font-weight: 400;
  background: transparent !important;
}

.filter-controls {
  display: flex;
  gap: var(--spacing-md);
  align-items: center;
  flex: 1;
}

.filter-select {
  min-width: 140px;
}

.active-filters {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  flex-wrap: wrap;
}

.active-filters-title {
  font-weight: 500;
  color: var(--gray-4);
  font-size: var(--font-size-sm);
}

.active-filter-tags {
  display: flex;
  gap: var(--spacing-sm);
  flex-wrap: wrap;
}

/* Data Sources Table - Enhanced */
.data-sources-table-container {
  max-width: 1200px;
  margin: 0 auto var(--spacing-xl);
  padding: 0 var(--spacing-xl);
  position: relative;
  z-index: 1;
}

.data-sources-table {
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid var(--gray-9);
  border-radius: var(--radius-lg);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  backdrop-filter: blur(20px);
  overflow: hidden;
}

.data-sources-table :deep(.el-table__header-wrapper) {
  background: rgba(248, 249, 250, 0.8);
}

.data-sources-table :deep(.el-table__body-wrapper) {
  background: rgba(255, 255, 255, 0.9);
}

.data-sources-table :deep(.el-table__row) {
  transition: all var(--transition-normal);
}

.data-sources-table :deep(.el-table__row:hover) {
  background: rgba(0, 122, 255, 0.02) !important;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* Table Source Info */
.table-source-info {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.table-source-info .source-icon {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  flex-shrink: 0;
}

.table-source-info .source-details {
  flex: 1;
  min-width: 0;
}

.table-source-info .source-name {
  font-size: var(--font-size-base);
  font-weight: 600;
  color: var(--gray-1);
  margin: 0 0 var(--spacing-xs) 0;
  line-height: 1.2;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.table-source-info .source-type {
  font-size: var(--font-size-sm);
  color: var(--gray-5);
  font-weight: 500;
}

/* Host Port */
.host-port {
  font-size: var(--font-size-base);
  font-weight: 500;
  color: var(--gray-2);
}

/* Database Name */
.database-name {
  font-size: var(--font-size-sm);
  color: var(--gray-5);
}

/* User Info */
.user-info {
  display: flex;
  flex-direction: column;
}

.username {
  font-size: var(--font-size-base);
  font-weight: 500;
  color: var(--gray-2);
}

/* Update Time */
.update-time {
  font-size: var(--font-size-sm);
  color: var(--gray-5);
  font-weight: 500;
}

/* Status Indicator */
.status-indicator {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  flex-shrink: 0;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  transition: all var(--transition-fast);
}

.status-dot.active {
  background: var(--success-color);
  box-shadow: 0 0 0 2px rgba(52, 199, 89, 0.2);
}

.status-dot.inactive {
  background: var(--gray-4);
}

.status-dot.error {
  background: var(--error-color);
  box-shadow: 0 0 0 2px rgba(255, 59, 48, 0.2);
}

.status-text {
  font-size: var(--font-size-xs);
  font-weight: 500;
}

/* Table Actions */
.table-actions {
  display: flex;
  gap: var(--spacing-xs);
  align-items: center;
  flex-wrap: nowrap;
  white-space: nowrap;
}

.table-btn {
  font-size: var(--font-size-xs) !important;
  padding: var(--spacing-xs) var(--spacing-sm) !important;
  height: 28px !important;
  min-height: 28px !important;
  border-radius: var(--radius-md) !important;
  flex-shrink: 0;
}

.table-btn .el-icon {
  font-size: 14px !important;
}

/* Responsive Design */
@media (max-width: 768px) {
  .data-sources-table-container {
    padding: 0 var(--spacing-md);
  }
  
  .data-sources-table :deep(.el-table__body) {
    font-size: var(--font-size-sm);
  }
  
  .table-actions {
    flex-direction: column;
    gap: var(--spacing-xs);
  }
  
  .table-btn {
    width: 100%;
  }
}

/* Action Buttons - Enhanced */
.action-btn {
  width: 32px;
  height: 32px;
  border-radius: var(--radius-md);
  border: 1px solid var(--gray-8);
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(248, 248, 248, 0.9) 100%);
  color: var(--gray-6);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all var(--transition-fast);
  flex-shrink: 0;
  position: relative;
  overflow: hidden;
  backdrop-filter: blur(10px);
}

.action-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(circle at center, rgba(255, 255, 255, 0.8) 0%, rgba(255, 255, 255, 0.2) 100%);
  opacity: 0;
  transition: opacity var(--transition-fast);
}

.action-btn:hover {
  transform: translateY(-1px) scale(1.02);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
  border-color: var(--gray-7);
}

.action-btn:hover::before {
  opacity: 1;
}

.action-btn:active {
  transform: translateY(0) scale(0.98);
}

/* Delete Button - Red Theme */
.delete-btn {
  border-color: var(--apple-red);
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(255, 59, 48, 0.1) 100%);
  color: var(--apple-red);
}

.delete-btn:hover {
  background: linear-gradient(135deg, var(--apple-red) 0%, var(--apple-red-dark) 100%);
  color: white;
  border-color: var(--apple-red);
  box-shadow: 0 4px 16px rgba(255, 59, 48, 0.25);
}

/* Icon Styling */
.action-btn .el-icon {
  width: 20px;
  height: 20px;
  font-size: 20px;
  transition: all var(--transition-fast);
  font-weight: 500;
}

.action-btn:hover .el-icon {
  transform: scale(1.1);
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: var(--spacing-xxl) var(--spacing-xl);
  max-width: 600px;
  margin: 0 auto;
}

.empty-icon {
  font-size: 4rem;
  color: var(--gray-4);
  margin-bottom: var(--spacing-lg);
}

.empty-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--gray-2);
  margin: 0 0 var(--spacing-md) 0;
}

.empty-description {
  color: var(--gray-5);
  margin: 0 0 var(--spacing-xl) 0;
  font-size: var(--font-size-lg);
}

/* Database Selection Modal */
.database-selection-modal .database-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: var(--spacing-lg);
}

.database-card {
  background: rgba(255, 255, 255, 0.98);
  border: 1px solid var(--gray-9);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
  cursor: pointer;
  transition: all var(--transition-normal);
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.database-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
  border-color: var(--gray-7);
}

.database-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  flex-shrink: 0;
}

.database-info {
  flex: 1;
}

.database-name {
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--gray-1);
  margin: 0 0 var(--spacing-xs) 0;
}

.database-description {
  font-size: var(--font-size-sm);
  color: var(--gray-5);
  margin: 0 0 var(--spacing-xs) 0;
  line-height: 1.4;
}

.database-port {
  font-size: var(--font-size-xs);
  color: var(--gray-4);
  font-weight: 500;
}

.database-arrow {
  color: var(--gray-4);
  transition: color var(--transition-normal);
}

.database-card:hover .database-arrow {
  color: var(--apple-blue);
}

/* Configuration Modal */
.config-form {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.db-type-info {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-md);
  background: linear-gradient(135deg, var(--gray-11) 0%, var(--gray-10) 100%);
  border-radius: var(--radius-md);
  border: 1px solid var(--gray-9);
}

.db-type-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  flex-shrink: 0;
}

.db-type-details h4 {
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--gray-1);
  margin: 0 0 var(--spacing-xs) 0;
}

.db-type-details p {
  font-size: var(--font-size-sm);
  color: var(--gray-5);
  margin: 0;
}

.form-actions {
  display: flex;
  gap: var(--spacing-md);
  justify-content: flex-end;
  padding-top: var(--spacing-md);
  border-top: 1px solid var(--gray-8);
}

/* Apple Button Styles */
.apple-button {
  border-radius: var(--radius-lg);
  border: none;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-sm);
  text-decoration: none;
  position: relative;
  overflow: hidden;
  font-size: var(--font-size-base);
  padding: var(--spacing-md) var(--spacing-lg);
  height: 44px;
  min-height: 44px;
  line-height: 1.2;
}

.apple-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.2) 0%, rgba(255, 255, 255, 0.1) 100%);
  border-radius: inherit;
  opacity: 0;
  transition: opacity var(--transition-fast);
}

.apple-button:hover::before {
  opacity: 1;
}

.apple-button:active {
  transform: scale(0.98);
}

.apple-button-primary {
  background: linear-gradient(135deg, var(--apple-blue) 0%, var(--apple-blue-dark) 100%);
  color: white;
  box-shadow: 0 4px 16px rgba(0, 122, 255, 0.3);
}

.apple-button-primary:hover {
  background: linear-gradient(135deg, var(--apple-blue-dark) 0%, #0051D5 100%);
  box-shadow: 0 6px 20px rgba(0, 122, 255, 0.4);
}

.apple-button-secondary {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(248, 248, 248, 0.9) 100%);
  color: var(--gray-1);
  border: 1px solid var(--gray-8);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.apple-button-secondary:hover {
  background: linear-gradient(135deg, rgba(255, 255, 255, 1) 0%, rgba(248, 248, 248, 1) 100%);
  border-color: var(--gray-7);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

/* Responsive Design */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: var(--spacing-lg);
    text-align: center;
  }

  .filter-row {
    flex-direction: column;
    align-items: stretch;
  }

  .search-container {
    min-width: unset;
    max-width: unset;
  }

  .filter-controls {
    flex-wrap: wrap;
  }

  .data-sources-list {
    grid-template-columns: 1fr;
    padding: 0 var(--spacing-md);
  }

  .filter-card {
    margin: var(--spacing-lg) var(--spacing-md);
    padding: var(--spacing-md);
  }

  .database-selection-modal .database-grid {
    grid-template-columns: 1fr;
  }
}
</style>