<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { ArrowLeft, Search, Refresh, Clock, CircleCheck, Warning, DataLine, Delete } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRouter, useRoute } from 'vue-router'
import api from '@/utils/api'

interface ExecutionRecord {
  id: number
  task_id: number
  task_name: string
  data_source_name: string
  check_value: string
  expected_value: string
  check_passed: boolean
  execution_time: string
  error_message?: string
  duration: number
}

const router = useRouter()
const route = useRoute()
const executions = ref<ExecutionRecord[]>([])
const loading = ref(false)
const searchQuery = ref('')
const statusFilter = ref('')
const dataSourceFilter = ref('')
const sortBy = ref('execution_time')
const currentPage = ref(1)
const pageSize = ref(20)

// 从URL参数获取规则ID
const ruleId = computed(() => route.query.rule_id as string | null)

onMounted(() => {
  fetchExecutions()
})

const fetchExecutions = async () => {
  loading.value = true
  try {
    // 如果有规则ID过滤，只获取该规则的执行记录
    const url = ruleId.value 
      ? `/api/v1/inspection-tasks/${ruleId.value}/results`
      : '/api/v1/inspection-tasks/results/all'
    
    const response = await api.get(url)
    const results = response.data || []
    
    // API已经返回了完整的详细信息，直接使用
    executions.value = results.map((result: any) => ({
      id: result.id,
      task_id: result.task_id,
      task_name: result.task_name,
      data_source_name: result.data_source_name,
      check_value: result.check_value,
      expected_value: result.expected_value,
      check_passed: result.check_passed,
      execution_time: result.execution_time,
      error_message: result.error_message,
      duration: result.duration || 0
    }))
  } catch {
    ElMessage.error('获取执行历史失败')
  } finally {
    loading.value = false
  }
}

const refreshData = () => {
  fetchExecutions()
}

const filteredExecutions = computed(() => {
  let filtered = [...executions.value]

  // 搜索过滤
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(exec => 
      exec.task_name.toLowerCase().includes(query) ||
      exec.data_source_name.toLowerCase().includes(query)
    )
  }

  // 状态过滤
  if (statusFilter.value) {
    filtered = filtered.filter(exec => 
      statusFilter.value === 'passed' ? exec.check_passed : !exec.check_passed
    )
  }

  // 数据源过滤
  if (dataSourceFilter.value) {
    filtered = filtered.filter(exec => 
      exec.data_source_name.toLowerCase().includes(dataSourceFilter.value.toLowerCase())
    )
  }

  // 排序
  filtered.sort((a, b) => {
    switch (sortBy.value) {
      case 'execution_time':
      default:
        return new Date(b.execution_time).getTime() - new Date(a.execution_time).getTime()
      case 'duration':
        return b.duration - a.duration
      case 'task_name':
        return a.task_name.localeCompare(b.task_name)
    }
  })

  return filtered
})

const paginatedExecutions = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredExecutions.value.slice(start, end)
})

const totalPages = computed(() => {
  return Math.ceil(filteredExecutions.value.length / pageSize.value)
})

const formatDuration = (ms: number) => {
  if (ms < 1000) return `${ms}ms`
  if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`
  return `${(ms / 60000).toFixed(1)}min`
}

const formatTime = (time: string) => {
  return new Date(time).toLocaleString()
}

const goBack = () => {
  if (ruleId.value) {
    router.push('/inspection-rules')
  } else {
    router.push('/inspection-rules')
  }
}

const viewTaskDetails = (taskId: number) => {
  router.push(`/inspection-rules/${taskId}/edit`)
}

const deleteExecution = async (resultId: number) => {
  try {
    console.log('删除执行记录开始, resultId:', resultId)
    await ElMessageBox.confirm('确定要删除这条执行记录吗？此操作不可恢复。', '确认删除', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    console.log('用户确认删除, 发送API请求:', `/api/v1/inspection-tasks/results/${resultId}`)
    const response = await api.delete(`/api/v1/inspection-tasks/results/${resultId}`)
    console.log('API响应:', response)
    
    ElMessage.success('执行记录删除成功')
    refreshData()
  } catch (error: any) {
    console.error('删除执行记录失败, 详细错误:', error)
    if (error !== 'cancel') {
      console.error('错误类型:', typeof error)
      console.error('错误消息:', error.message)
      console.error('错误响应:', error.response)
      ElMessage.error('执行记录删除失败')
    }
  }
}
</script>

<template>
  <div class="execution-history-container">
    <div class="apple-container">
      <!-- Header -->
      <div class="page-header">
        <div class="header-content">
          <div class="title-section">
            <button class="back-button" @click="goBack">
              <el-icon><ArrowLeft /></el-icon>
              返回
            </button>
            <div>
              <h1 class="page-title">执行历史</h1>
              <p class="page-description">
                {{ ruleId ? '单个规则' : '所有规则' }}的巡检执行记录和历史数据
              </p>
            </div>
          </div>
          <div class="header-actions">
            <button class="apple-button apple-button-secondary" @click="refreshData" :disabled="loading">
              <el-icon><Refresh /></el-icon>
              刷新
            </button>
          </div>
        </div>
      </div>

      <!-- Statistics Summary -->
      <div class="stats-section">
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-icon total">
              <el-icon><DataLine /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ filteredExecutions.length }}</div>
              <div class="stat-label">总执行次数</div>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon success">
              <el-icon><CircleCheck /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ filteredExecutions.filter(e => e.check_passed).length }}</div>
              <div class="stat-label">成功次数</div>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon warning">
              <el-icon><Warning /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ filteredExecutions.filter(e => !e.check_passed).length }}</div>
              <div class="stat-label">失败次数</div>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon average">
              <el-icon><Clock /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">
                {{ filteredExecutions.length > 0 ? Math.round(filteredExecutions.reduce((sum, e) => sum + e.duration, 0) / filteredExecutions.length) : 0 }}ms
              </div>
              <div class="stat-label">平均耗时</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Filters -->
      <div class="filters-section">
        <div class="filters-left">
          <div class="search-box">
            <el-input
              v-model="searchQuery"
              placeholder="搜索任务名称或数据源..."
              class="search-input"
              :prefix-icon="Search"
              clearable
            />
          </div>
          <el-select v-model="statusFilter" placeholder="状态筛选" clearable class="filter-select">
            <el-option label="成功" value="passed" />
            <el-option label="失败" value="failed" />
          </el-select>
          <el-input
            v-model="dataSourceFilter"
            placeholder="数据源筛选"
            class="filter-select"
            clearable
          />
        </div>
        <div class="filters-right">
          <el-select v-model="sortBy" class="sort-select">
            <el-option label="执行时间" value="execution_time" />
            <el-option label="执行耗时" value="duration" />
            <el-option label="任务名称" value="task_name" />
          </el-select>
        </div>
      </div>

      <!-- Execution History Table -->
      <div class="table-section">
        <div class="table-container">
          <el-table
            :data="paginatedExecutions"
            :loading="loading"
            class="apple-table"
            row-class-name="apple-table-row"
            header-row-class-name="apple-table-header"
          >
            <el-table-column label="任务信息" min-width="200">
              <template #default="{ row }">
                <div class="task-info">
                  <div class="task-name">{{ row.task_name }}</div>
                  <div class="task-meta">任务ID: {{ row.task_id }}</div>
                </div>
              </template>
            </el-table-column>

            <el-table-column label="数据源" width="150">
              <template #default="{ row }">
                <div class="data-source-info">
                  {{ row.data_source_name }}
                </div>
              </template>
            </el-table-column>

            <el-table-column label="执行结果" width="150">
              <template #default="{ row }">
                <div class="execution-result">
                  <el-tag :type="row.check_passed ? 'success' : 'danger'" size="small">
                    {{ row.check_passed ? '成功' : '失败' }}
                  </el-tag>
                  <div class="duration">{{ formatDuration(row.duration) }}</div>
                </div>
              </template>
            </el-table-column>

            <el-table-column label="检查值" width="120">
              <template #default="{ row }">
                <div class="value-info">
                  <div class="check-value">实际: {{ row.check_value || 'N/A' }}</div>
                  <div class="expected-value">期望: {{ row.expected_value }}</div>
                </div>
              </template>
            </el-table-column>

            <el-table-column label="执行时间" width="180">
              <template #default="{ row }">
                <div class="execution-time">
                  {{ formatTime(row.execution_time) }}
                </div>
              </template>
            </el-table-column>

            <el-table-column label="错误信息" min-width="200">
              <template #default="{ row }">
                <div class="error-info" v-if="row.error_message">
                  <el-text type="danger" size="small">
                    {{ row.error_message }}
                  </el-text>
                </div>
                <div class="error-info" v-else>
                  <el-text type="success" size="small">执行正常</el-text>
                </div>
              </template>
            </el-table-column>

            <el-table-column label="操作" width="80">
              <template #default="{ row }">
                <div class="action-buttons">
                  <button 
                    class="action-btn danger" 
                    @click="deleteExecution(row.id)"
                    title="删除执行记录"
                  >
                    <el-icon><Delete /></el-icon>
                  </button>
                </div>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <!-- Pagination -->
        <div v-if="totalPages > 1" class="pagination-section">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50, 100]"
            :total="filteredExecutions.length"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="currentPage = 1"
          />
        </div>

        <!-- Empty State -->
        <div v-if="filteredExecutions.length === 0 && !loading" class="empty-state">
          <el-icon class="empty-icon"><Clock /></el-icon>
          <h3>暂无执行记录</h3>
          <p>{{ ruleId ? '该规则还没有执行记录' : '还没有任何巡检执行记录' }}</p>
          <button class="apple-button apple-button-primary" @click="goBack">
            <el-icon><ArrowLeft /></el-icon>
            返回规则列表
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.execution-history-container {
  min-height: 100vh;
  background: var(--gray-8);
  padding: var(--spacing-xl) 0;
}

.page-header {
  margin-bottom: var(--spacing-2xl);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title-section {
  display: flex;
  align-items: center;
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
  margin: 0 0 var(--spacing-sm) 0;
}

.page-description {
  color: var(--gray-4);
  margin: 0;
  font-size: var(--font-size-lg);
}

.header-actions {
  display: flex;
  gap: var(--spacing-sm);
}

/* Statistics Section */
.stats-section {
  margin-bottom: var(--spacing-2xl);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: var(--spacing-lg);
}

.stat-card {
  background: var(--gray-9);
  border: 1px solid var(--gray-5);
  border-radius: var(--radius-lg);
  padding: var(--spacing-xl);
  display: flex;
  align-items: center;
  gap: var(--spacing-lg);
  transition: all var(--transition-normal);
}

.stat-card:hover {
  border-color: var(--gray-4);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  flex-shrink: 0;
}

.stat-icon.total {
  background: rgba(0, 122, 255, 0.1);
  color: var(--apple-blue);
}

.stat-icon.success {
  background: rgba(52, 199, 89, 0.1);
  color: var(--apple-green);
}

.stat-icon.warning {
  background: rgba(255, 149, 0, 0.1);
  color: var(--apple-orange);
}

.stat-icon.average {
  background: rgba(175, 82, 222, 0.1);
  color: var(--apple-purple);
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: var(--font-size-2xl);
  font-weight: 600;
  color: var(--gray-1);
  line-height: 1;
}

.stat-label {
  color: var(--gray-4);
  font-size: var(--font-size-sm);
  margin-top: var(--spacing-xs);
}

/* Filters Section */
.filters-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-lg);
  gap: var(--spacing-lg);
}

.filters-left {
  display: flex;
  gap: var(--spacing-md);
  align-items: center;
  flex: 1;
}

.search-box {
  flex: 1;
  max-width: 400px;
}

.filter-select {
  width: 140px;
}

.filters-right {
  display: flex;
  gap: var(--spacing-md);
}

.sort-select {
  width: 140px;
}

/* Table Section */
.table-section {
  background: var(--gray-9);
  border: 1px solid var(--gray-5);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.table-container {
  overflow-x: auto;
}

.task-info {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.task-name {
  font-weight: 600;
  color: var(--gray-1);
  font-size: var(--font-size-base);
}

.task-meta {
  color: var(--gray-4);
  font-size: var(--font-size-xs);
}

.data-source-info {
  color: var(--gray-2);
  font-size: var(--font-size-sm);
  font-weight: 500;
}

.execution-result {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
  align-items: flex-start;
}

.duration {
  color: var(--gray-4);
  font-size: var(--font-size-xs);
}

.value-info {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.check-value {
  color: var(--gray-2);
  font-size: var(--font-size-sm);
}

.expected-value {
  color: var(--gray-4);
  font-size: var(--font-size-xs);
}

.execution-time {
  color: var(--gray-2);
  font-size: var(--font-size-sm);
}

.error-info {
  max-width: 200px;
  word-break: break-word;
}

.action-buttons {
  display: flex;
  gap: var(--spacing-xs);
  align-items: center;
}

.action-btn {
  width: 32px;
  height: 32px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--gray-6);
  background: var(--gray-8);
  color: var(--gray-3);
  cursor: pointer;
  transition: all var(--transition-fast);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
}

.action-btn:hover {
  background: var(--gray-7);
  color: var(--gray-2);
  border-color: var(--gray-5);
}

.action-btn.secondary:hover {
  background: var(--apple-blue);
  color: white;
  border-color: var(--apple-blue);
}

.action-btn.danger:hover {
  background: var(--apple-red);
  color: white;
  border-color: var(--apple-red);
}

/* Pagination */
.pagination-section {
  padding: var(--spacing-lg);
  border-top: 1px solid var(--gray-5);
  display: flex;
  justify-content: center;
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: var(--spacing-3xl) var(--spacing-xl);
  color: var(--gray-4);
}

.empty-icon {
  font-size: 64px;
  color: var(--gray-5);
  margin-bottom: var(--spacing-lg);
}

.empty-state h3 {
  font-size: var(--font-size-xl);
  font-weight: 600;
  color: var(--gray-2);
  margin: 0 0 var(--spacing-sm) 0;
}

.empty-state p {
  margin: 0 0 var(--spacing-xl) 0;
  font-size: var(--font-size-base);
}

/* Responsive Design */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-lg);
  }
  
  .title-section {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-md);
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .filters-section {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filters-left {
    flex-direction: column;
  }
  
  .search-box {
    max-width: none;
  }
}
</style>