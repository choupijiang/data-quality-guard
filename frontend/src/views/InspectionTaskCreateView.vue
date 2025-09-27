<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ArrowLeft, Plus, Check, Connection, Clock } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import api from '@/utils/api'

interface DataSource {
  id: number
  name: string
  type: string
  host: string
  port: number
  database: string
  status: string
}

interface Project {
  id: number
  name: string
  description?: string
  status: string
}

const router = useRouter()
const loading = ref(false)
const testingConnection = ref(false)
const formValid = ref(false)

const taskForm = ref({
  name: '',
  description: '',
  data_source_id: null as number | null,
  project_id: null as number | null,
  check_sql: '',
  expected_sql: '',
  check_expression: 'check_value == expected_value',
  cron_schedule: '0 0 * * *'  // 每天午夜执行
})

const dataSources = ref<DataSource[]>([])
const projects = ref<Project[]>([])
const sqlHints = ref('')

// 常用表达式选项
const expressionOptions = [
  { label: '等于', value: 'check_value == expected_value' },
  { label: '不等于', value: 'check_value != expected_value' },
  { label: '大于', value: 'check_value > expected_value' },
  { label: '小于', value: 'check_value < expected_value' },
  { label: '大于等于', value: 'check_value >= expected_value' },
  { label: '小于等于', value: 'check_value <= expected_value' }
]

// 常用Cron表达式
const cronOptions = [
  { label: '每分钟', value: '* * * * *' },
  { label: '每小时', value: '0 * * * *' },
  { label: '每天午夜', value: '0 0 * * *' },
  { label: '每天中午', value: '0 12 * * *' },
  { label: '每周一', value: '0 0 * * 1' },
  { label: '每月1号', value: '0 0 1 * *' }
]

onMounted(async () => {
  await loadDataSources()
  await loadProjects()
})

const loadDataSources = async () => {
  try {
    const response = await api.get('/api/v1/data-sources/')
    dataSources.value = response.data || []
  } catch {
    ElMessage.error('加载数据源失败')
  }
}

const loadProjects = async () => {
  try {
    const response = await api.get('/api/v1/projects/')
    projects.value = response.data || []
  } catch {
    ElMessage.error('加载项目失败')
  }
}

const testSQL = async (type: 'check' | 'expected') => {
  const sql = type === 'check' ? taskForm.value.check_sql : taskForm.value.expected_sql
  const dataSourceId = taskForm.value.data_source_id
  
  if (!sql || !dataSourceId) {
    ElMessage.warning('请先选择数据源并输入SQL语句')
    return
  }
  
  testingConnection.value = true
  try {
    const response = await api.post('/api/v1/data-sources/test-sql', {
      data_source_id: dataSourceId,
      sql: sql
    })
    
    if (response.data.success) {
      ElMessage.success(`SQL测试成功，返回值: ${response.data.result}`)
    } else {
      ElMessage.error(`SQL测试失败: ${response.data.error}`)
    }
  } catch {
    ElMessage.error('SQL测试失败，请检查SQL语句和数据源连接')
  } finally {
    testingConnection.value = false
  }
}

const getSQLHints = async () => {
  const dataSourceId = taskForm.value.data_source_id
  if (!dataSourceId) {
    ElMessage.warning('请先选择数据源')
    return
  }
  
  try {
    const response = await api.get(`/api/v1/data-sources/${dataSourceId}/schema`)
    if (response.data.tables) {
      const tables = response.data.tables.slice(0, 5) // 显示前5个表作为示例
      sqlHints.value = `可用表示例: ${tables.join(', ')}`
      ElMessage.success('已获取SQL提示信息')
    }
  } catch {
    ElMessage.error('获取SQL提示失败')
  }
}

const validateForm = () => {
  const required = ['name', 'data_source_id', 'project_id', 'check_sql', 'expected_sql', 'check_expression', 'cron_schedule']
  formValid.value = required.every(field => {
    const value = taskForm.value[field as keyof typeof taskForm.value]
    return value !== null && value !== undefined && value !== ''
  })
  return formValid.value
}

const submitTask = async () => {
  if (!validateForm()) {
    ElMessage.error('请填写所有必填字段')
    return
  }
  
  loading.value = true
  try {
    await api.post('/api/v1/inspection-tasks/', taskForm.value)
    ElMessage.success('巡检任务创建成功')
    router.push('/inspection-tasks')
  } catch {
    ElMessage.error('创建巡检任务失败')
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  router.push('/inspection-tasks')
}
</script>

<template>
  <div class="create-task-container">
    <div class="apple-container">
      <!-- Header -->
      <div class="page-header">
        <button class="back-button" @click="goBack">
          <el-icon><ArrowLeft /></el-icon>
          返回任务列表
        </button>
        <h1 class="page-title">创建巡检任务</h1>
        <div class="header-actions">
          <button class="apple-button apple-button-secondary" @click="goBack">
            取消
          </button>
          <button 
            class="apple-button apple-button-primary" 
            @click="submitTask"
            :disabled="loading || !formValid"
          >
            <el-icon v-if="loading" class="loading-icon"><Refresh /></el-icon>
            {{ loading ? '创建中...' : '创建任务' }}
          </button>
        </div>
      </div>

      <!-- Form Content -->
      <div class="form-content">
        <!-- Basic Information -->
        <div class="form-section">
          <h2 class="section-title">基本信息</h2>
          <div class="form-grid">
            <div class="form-item">
              <label class="form-label required">任务名称</label>
              <el-input
                v-model="taskForm.name"
                placeholder="请输入任务名称"
                maxlength="100"
                show-word-limit
                @input="validateForm"
              />
            </div>
            
            <div class="form-item">
              <label class="form-label">任务描述</label>
              <el-input
                v-model="taskForm.description"
                type="textarea"
                placeholder="请输入任务描述（可选）"
                :rows="2"
                maxlength="500"
                show-word-limit
              />
            </div>
          </div>
        </div>

        <!-- Data Source and Project -->
        <div class="form-section">
          <h2 class="section-title">数据配置</h2>
          <div class="form-grid">
            <div class="form-item">
              <label class="form-label required">数据源</label>
              <el-select
                v-model="taskForm.data_source_id"
                placeholder="请选择数据源"
                @change="validateForm"
              >
                <el-option
                  v-for="source in dataSources"
                  :key="source.id"
                  :label="`${source.name} (${source.host}:${source.port}/${source.database})`"
                  :value="source.id"
                >
                  <div class="select-option">
                    <el-icon><Connection /></el-icon>
                    <div class="option-info">
                      <div class="option-name">{{ source.name }}</div>
                      <div class="option-desc">{{ source.host }}:{{ source.port }}/{{ source.database }}</div>
                    </div>
                  </div>
                </el-option>
              </el-select>
            </div>
            
            <div class="form-item">
              <label class="form-label required">所属项目</label>
              <el-select
                v-model="taskForm.project_id"
                placeholder="请选择项目"
                @change="validateForm"
              >
                <el-option
                  v-for="project in projects"
                  :key="project.id"
                  :label="project.name"
                  :value="project.id"
                />
              </el-select>
            </div>
          </div>
        </div>

        <!-- SQL Configuration -->
        <div class="form-section">
          <h2 class="section-title">SQL配置</h2>
          
          <!-- Check SQL -->
          <div class="sql-section">
            <div class="sql-header">
              <label class="form-label required">检验SQL</label>
              <div class="sql-actions">
                <button 
                  class="apple-button apple-button-secondary small"
                  @click="getSQLHints"
                  :disabled="!taskForm.data_source_id"
                >
                  获取提示
                </button>
                <button 
                  class="apple-button apple-button-secondary small"
                  @click="testSQL('check')"
                  :disabled="!taskForm.data_source_id || !taskForm.check_sql || testingConnection"
                >
                  {{ testingConnection ? '测试中...' : '测试SQL' }}
                </button>
              </div>
            </div>
            <el-input
              v-model="taskForm.check_sql"
              type="textarea"
              placeholder="请输入检验SQL语句（必须返回单个值）"
              :rows="4"
              @input="validateForm"
            />
            <div class="hint-text" v-if="sqlHints">
              💡 {{ sqlHints }}
            </div>
          </div>

          <!-- Expected SQL -->
          <div class="sql-section">
            <div class="sql-header">
              <label class="form-label required">期望SQL</label>
              <button 
                class="apple-button apple-button-secondary small"
                @click="testSQL('expected')"
                :disabled="!taskForm.data_source_id || !taskForm.expected_sql || testingConnection"
              >
                {{ testingConnection ? '测试中...' : '测试SQL' }}
              </button>
            </div>
            <el-input
              v-model="taskForm.expected_sql"
              type="textarea"
              placeholder="请输入期望SQL语句（必须返回单个值）"
              :rows="4"
              @input="validateForm"
            />
          </div>
        </div>

        <!-- Expression and Schedule -->
        <div class="form-section">
          <h2 class="section-title">执行配置</h2>
          <div class="form-grid">
            <div class="form-item">
              <label class="form-label required">检查表达式</label>
              <el-select
                v-model="taskForm.check_expression"
                placeholder="请选择检查表达式"
                @change="validateForm"
              >
                <el-option
                  v-for="option in expressionOptions"
                  :key="option.value"
                  :label="option.label"
                  :value="option.value"
                />
              </el-select>
            </div>
            
            <div class="form-item">
              <label class="form-label required">执行计划</label>
              <el-select
                v-model="taskForm.cron_schedule"
                placeholder="请选择执行计划"
                @change="validateForm"
              >
                <el-option
                  v-for="option in cronOptions"
                  :key="option.value"
                  :label="option.label"
                  :value="option.value"
                />
              </el-select>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.create-task-container {
  min-height: 100vh;
  background: var(--gray-8);
  padding: var(--spacing-xl) 0;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--spacing-2xl);
  gap: var(--spacing-lg);
}

.back-button {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  background: none;
  border: none;
  color: var(--gray-2);
  font-size: var(--font-size-base);
  cursor: pointer;
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
}

.back-button:hover {
  background: var(--gray-7);
  color: var(--gray-1);
}

.page-title {
  font-size: var(--font-size-3xl);
  font-weight: 700;
  color: var(--gray-1);
  margin: 0;
}

.header-actions {
  display: flex;
  gap: var(--spacing-sm);
}

.form-content {
  background: var(--gray-9);
  border: 1px solid var(--gray-5);
  border-radius: var(--radius-lg);
  padding: var(--spacing-2xl);
}

.form-section {
  margin-bottom: var(--spacing-2xl);
}

.form-section:last-child {
  margin-bottom: 0;
}

.section-title {
  font-size: var(--font-size-xl);
  font-weight: 600;
  color: var(--gray-1);
  margin-bottom: var(--spacing-lg);
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: var(--spacing-lg);
}

.form-item {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.form-label {
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--gray-2);
}

.form-label.required::after {
  content: ' *';
  color: var(--apple-red);
}

.sql-section {
  margin-bottom: var(--spacing-xl);
}

.sql-section:last-child {
  margin-bottom: 0;
}

.sql-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-sm);
}

.sql-actions {
  display: flex;
  gap: var(--spacing-sm);
}

.select-option {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.option-info {
  display: flex;
  flex-direction: column;
}

.option-name {
  font-size: var(--font-size-base);
  font-weight: 500;
  color: var(--gray-1);
}

.option-desc {
  font-size: var(--font-size-xs);
  color: var(--gray-3);
}

.hint-text {
  margin-top: var(--spacing-sm);
  font-size: var(--font-size-sm);
  color: var(--gray-3);
  font-style: italic;
}

.apple-button.small {
  padding: var(--spacing-xs) var(--spacing-sm);
  font-size: var(--font-size-sm);
}

.loading-icon {
  animation: apple-spin 1s linear infinite;
}

@keyframes apple-spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Responsive Design */
@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-md);
  }
  
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .sql-header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-sm);
  }
  
  .sql-actions {
    width: 100%;
    justify-content: flex-end;
  }
}
</style>