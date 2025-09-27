<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ArrowLeft, Plus, Check } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import api from '@/utils/api'

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
const loading = ref(false)
const selectedDbType = ref<DatabaseType | null>(null)
const showDatabaseSelection = ref(true)
const showConfigForm = ref(false)

const configForm = ref<Record<string, string>>({
  name: '',
  host: '',
  port: '',
  database: '',
  username: '',
  password: ''
})

const databaseTypes = ref<DatabaseType[]>([
  {
    id: 'mysql',
    name: 'MySQL',
    icon: '🐬',
    color: '#4479A1',
    description: '最流行的开源关系型数据库',
    defaultPort: 3306,
    configFields: [
      { name: 'name', label: '数据源名称', type: 'text', required: true, placeholder: '请输入数据源名称' },
      { name: 'host', label: '主机地址', type: 'text', required: true, placeholder: 'localhost' },
      { name: 'port', label: '端口', type: 'number', required: true, placeholder: '3306' },
      { name: 'database', label: '数据库名', type: 'text', required: true, placeholder: '请输入数据库名称' },
      { name: 'username', label: '用户名', type: 'text', required: true, placeholder: '请输入用户名' },
      { name: 'password', label: '密码', type: 'password', required: true, placeholder: '请输入密码' }
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
      { name: 'name', label: '数据源名称', type: 'text', required: true, placeholder: '请输入数据源名称' },
      { name: 'host', label: '主机地址', type: 'text', required: true, placeholder: 'localhost' },
      { name: 'port', label: '端口', type: 'number', required: true, placeholder: '8123' },
      { name: 'database', label: '数据库名', type: 'text', required: true, placeholder: '请输入数据库名称' },
      { name: 'username', label: '用户名', type: 'text', required: true, placeholder: '请输入用户名' },
      { name: 'password', label: '密码', type: 'password', required: true, placeholder: '请输入密码' }
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
      { name: 'name', label: '数据源名称', type: 'text', required: true, placeholder: '请输入数据源名称' },
      { name: 'host', label: '主机地址', type: 'text', required: true, placeholder: 'localhost' },
      { name: 'port', label: '端口', type: 'number', required: true, placeholder: '5432' },
      { name: 'database', label: '数据库名', type: 'text', required: true, placeholder: '请输入数据库名称' },
      { name: 'username', label: '用户名', type: 'text', required: true, placeholder: '请输入用户名' },
      { name: 'password', label: '密码', type: 'password', required: true, placeholder: '请输入密码' }
    ]
  },
  {
    id: 'starrocks',
    name: 'StarRocks',
    icon: '⭐',
    color: '#0067C1',
    description: '新一代极速全场景分析型数据库',
    defaultPort: 9030,
    configFields: [
      { name: 'name', label: '数据源名称', type: 'text', required: true, placeholder: '请输入数据源名称' },
      { name: 'host', label: '主机地址', type: 'text', required: true, placeholder: 'localhost' },
      { name: 'port', label: '端口', type: 'number', required: true, placeholder: '9030' },
      { name: 'database', label: '数据库名', type: 'text', required: true, placeholder: '请输入数据库名称' },
      { name: 'username', label: '用户名', type: 'text', required: true, placeholder: '请输入用户名' },
      { name: 'password', label: '密码', type: 'password', required: true, placeholder: '请输入密码' }
    ]
  }
])

const selectDatabaseType = (dbType: DatabaseType) => {
  selectedDbType.value = dbType
  showDatabaseSelection.value = false
  showConfigForm.value = true
  
  // Reset form with default values
  configForm.value = {
    name: '',
    host: 'localhost',
    port: dbType.defaultPort.toString(),
    database: '',
    username: '',
    password: ''
  }
}

const testConnection = async () => {
  if (!selectedDbType.value) return
  
  try {
    loading.value = true
    await api.post('/api/v1/data-sources/test-connection', {
      type: selectedDbType.value.id,
      ...configForm.value
    })
    ElMessage.success('连接测试成功')
  } catch (error) {
    ElMessage.error('连接测试失败')
  } finally {
    loading.value = false
  }
}

const createDataSource = async () => {
  if (!selectedDbType.value) return
  
  try {
    loading.value = true
    await api.post('/api/v1/data-sources/', {
      type: selectedDbType.value.id,
      ...configForm.value
    })
    
    ElMessage.success('数据源创建成功')
    router.push('/data-sources')
  } catch (error) {
    if (error.response) {
      ElMessage.error(error.response.data.detail || '创建数据源失败')
    } else {
      ElMessage.error('创建数据源失败')
    }
  } finally {
    loading.value = false
  }
}

const cancelCreate = () => {
  router.push('/data-sources')
}

const backToSelection = () => {
  showDatabaseSelection.value = true
  showConfigForm.value = false
  selectedDbType.value = null
}
</script>

<template>
  <div class="create-data-source-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-content">
        <div class="title-section">
          <h1>创建数据源</h1>
          <p>创建一个新的数据库连接</p>
        </div>
        <button class="apple-button apple-button-secondary" @click="cancelCreate">
          <el-icon><ArrowLeft /></el-icon>
          返回数据源列表
        </button>
      </div>
    </div>

    <!-- Form Content -->
    <div class="form-content">
      <!-- Database Type Selection -->
      <div v-if="showDatabaseSelection" class="selection-card">
        <div class="selection-header">
          <h2>选择数据库类型</h2>
          <p>选择您要连接的数据库类型</p>
        </div>
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
              <el-icon><Plus /></el-icon>
            </div>
          </div>
        </div>
      </div>

      <!-- Configuration Form -->
      <div v-if="showConfigForm && selectedDbType" class="form-card">
        <div class="config-header">
          <div class="db-type-info">
            <div class="db-type-icon" :style="{ backgroundColor: selectedDbType.color }">
              <span class="icon-emoji">{{ selectedDbType.icon }}</span>
            </div>
            <div class="db-type-details">
              <h4>{{ selectedDbType.name }}</h4>
              <p>{{ selectedDbType.description }}</p>
            </div>
          </div>
          <button class="apple-button apple-button-secondary" @click="backToSelection">
            <el-icon><ArrowLeft /></el-icon>
            重新选择
          </button>
        </div>

        <el-form
          :model="configForm"
          label-width="120px"
          label-position="left"
          class="config-form"
        >
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
              size="large"
            />
          </el-form-item>

          <div class="form-actions">
            <button class="apple-button apple-button-secondary" @click="testConnection" :disabled="loading">
              测试连接
            </button>
            <button class="apple-button apple-button-primary create-data-source-btn" @click="createDataSource" :disabled="loading">
              <el-icon><Check /></el-icon>
              创建数据源
            </button>
          </div>
        </el-form>
      </div>
    </div>
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
  --gray-8: F3F4F6;
  --gray-9: #F9FAFB;
  --gray-10: #FFFFFF;
  --gray-11: rgba(255, 255, 255, 0.95);
  
  --apple-blue: #007AFF;
  --apple-blue-dark: #0051D5;
  --apple-green: #34C759;
}

/* Container */
.create-data-source-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  position: relative;
}

.create-data-source-container::before {
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

/* Page Header */
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

.title-section h1 {
  font-size: 2rem;
  font-weight: 600;
  color: var(--gray-1);
  margin: 0 0 var(--spacing-xs) 0;
  background: linear-gradient(135deg, var(--gray-1) 0%, var(--gray-3) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.title-section p {
  color: var(--gray-5);
  margin: 0;
  font-size: var(--font-size-lg);
}

/* Form Content */
.form-content {
  max-width: 800px;
  margin: var(--spacing-xl) auto;
  padding: 0 var(--spacing-xl);
  position: relative;
  z-index: 1;
}

/* Selection Card */
.selection-card {
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid var(--gray-9);
  border-radius: var(--radius-lg);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  backdrop-filter: blur(20px);
  padding: var(--spacing-xl);
}

.selection-header {
  text-align: center;
  margin-bottom: var(--spacing-xl);
}

.selection-header h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--gray-1);
  margin: 0 0 var(--spacing-sm) 0;
}

.selection-header p {
  color: var(--gray-5);
  margin: 0;
  font-size: var(--font-size-lg);
}

/* Database Grid */
.database-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
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
  width: 56px;
  height: 56px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
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

/* Form Card */
.form-card {
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid var(--gray-9);
  border-radius: var(--radius-lg);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  backdrop-filter: blur(20px);
  padding: var(--spacing-xl);
}

.config-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-xl);
  padding-bottom: var(--spacing-lg);
  border-bottom: 1px solid var(--gray-8);
}

.db-type-info {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
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
  color: var(--gray-5);
  margin: 0;
  font-size: var(--font-size-sm);
}

.config-form {
  max-width: 600px;
  margin: 0 auto;
}

.form-actions {
  display: flex;
  gap: var(--spacing-md);
  justify-content: center;
  margin-top: var(--spacing-xl);
  padding-top: var(--spacing-lg);
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

  .database-grid {
    grid-template-columns: 1fr;
  }

  .config-header {
    flex-direction: column;
    gap: var(--spacing-md);
    align-items: flex-start;
  }

  .form-actions {
    flex-direction: column;
  }

  .form-content {
    padding: 0 var(--spacing-md);
  }
}
</style>