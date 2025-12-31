<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { Delete, Plus, Search, Refresh, CircleCheck, Warning, DataLine, VideoPlay, Edit, Clock } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRouter } from 'vue-router'
import api from '@/utils/api'

interface InspectionRule {
  id: number
  name: string
  description: string
  data_source_id: number
  data_source_name: string
  project_id: number
  project_name: string
  check_sql: string
  expected_sql: string
  check_expression: string
  cron_schedule: string
  status: string
  last_run_at: string
  created_at: string
  execution_count: number
  success_rate: number
}

const router = useRouter()
const rules = ref<InspectionRule[]>([])
const loading = ref(false)
const searchQuery = ref('')
const statusFilter = ref('')
const sortBy = ref('created_at')

onMounted(() => {
  fetchRules()
})

const fetchRules = async () => {
  loading.value = true
  try {
    // 并行获取任务列表、数据源列表和项目列表
    const [tasksResponse, dataSourcesResponse, projectsResponse] = await Promise.all([
      api.get('/api/v1/inspection-tasks/'),
      api.get('/api/v1/data-sources/'),
      api.get('/api/v1/projects/')
    ])
    
    const tasks = tasksResponse.data || []
    const dataSources = dataSourcesResponse.data || []
    const projects = projectsResponse.data || []
    
    // 创建ID到名称的映射
    const dataSourceMap = new Map(dataSources.map((ds: any) => [ds.id, ds.name]))
    const projectMap = new Map(projects.map((project: any) => [project.id, project.name]))
    
    // 为每个任务获取执行统计和最新执行结果
    const rulesWithStats = await Promise.all(
      tasks.map(async (task: any) => {
        try {
          const [statsResponse, resultsResponse] = await Promise.all([
            api.get(`/api/v1/inspection-tasks/${task.id}/stats`),
            api.get(`/api/v1/inspection-tasks/${task.id}/results?limit=1`)
          ])
          
          const stats = statsResponse.data || {}
          const results = resultsResponse.data || []
          
          const totalExecutions = stats.total_executions || 0
          const successRate = stats.success_rate || 0
          
          // 根据最新执行结果计算状态
          let calculatedStatus = task.status
          if (results.length > 0) {
            const latestResult = results[0]
            if (latestResult.check_passed === false) {
              calculatedStatus = 'error'  // 最新执行失败，状态为错误
            } else if (latestResult.check_passed === true) {
              calculatedStatus = 'active'  // 最新执行成功，状态为正常
            }
          }
          
          return {
            id: task.id,
            name: task.name,
            description: task.description || '',
            data_source_id: task.data_source_id,
            data_source_name: dataSourceMap.get(task.data_source_id) || `数据源 ${task.data_source_id}`,
            project_id: task.project_id,
            project_name: projectMap.get(task.project_id) || `项目 ${task.project_id}`,
            check_sql: task.check_sql,
            expected_sql: task.expected_sql,
            check_expression: task.check_expression,
            cron_schedule: task.cron_schedule,
            status: calculatedStatus,
            last_run_at: task.last_run_at,
            created_at: task.created_at,
            execution_count: totalExecutions,
            success_rate: successRate
          }
        } catch {
          // 如果获取统计信息失败，使用默认值
          return {
            id: task.id,
            name: task.name,
            description: task.description || '',
            data_source_id: task.data_source_id,
            data_source_name: dataSourceMap.get(task.data_source_id) || `数据源 ${task.data_source_id}`,
            project_id: task.project_id,
            project_name: projectMap.get(task.project_id) || `项目 ${task.project_id}`,
            check_sql: task.check_sql,
            expected_sql: task.expected_sql,
            check_expression: task.check_expression,
            cron_schedule: task.cron_schedule,
            status: task.status,
            last_run_at: task.last_run_at,
            created_at: task.created_at,
            execution_count: 0,
            success_rate: 0
          }
        }
      })
    )
    
    rules.value = rulesWithStats
  } catch {
    ElMessage.error('获取巡检规则失败')
  } finally {
    loading.value = false
  }
}

const refreshData = () => {
  fetchRules()
}

const executeRule = async (ruleId: number) => {
  try {
    await api.post(`/api/v1/inspection-tasks/${ruleId}/execute`)
    ElMessage.success('规则执行成功')
    refreshData()
  } catch (error) {
    ElMessage.error('规则执行失败')
  }
}

const editRule = (ruleId: number) => {
  router.push(`/inspection-rules/${ruleId}/edit`)
}

const viewExecutions = (ruleId: number) => {
  router.push(`/inspection-tasks?rule_id=${ruleId}`)
}

const deleteRule = async (ruleId: number) => {
  try {
    await ElMessageBox.confirm('确定要删除这个巡检规则吗？此操作不可恢复。', '确认删除', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await api.delete(`/api/v1/inspection-tasks/${ruleId}`)
    ElMessage.success('规则删除成功')
    refreshData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('规则删除失败')
    }
  }
}

const createRule = () => {
  router.push('/inspection-rules/create')
}

const filteredRules = computed(() => {
  let filtered = rules.value

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(rule => 
      rule.name.toLowerCase().includes(query) ||
      rule.description.toLowerCase().includes(query) ||
      rule.data_source_name.toLowerCase().includes(query)
    )
  }

  if (statusFilter.value) {
    filtered = filtered.filter(rule => rule.status === statusFilter.value)
  }

  return filtered.sort((a, b) => {
    if (sortBy.value === 'created_at') {
      return new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    } else if (sortBy.value === 'name') {
      return a.name.localeCompare(b.name)
    } else if (sortBy.value === 'last_run') {
      if (!a.last_run_at) return 1
      if (!b.last_run_at) return -1
      return new Date(b.last_run_at).getTime() - new Date(a.last_run_at).getTime()
    }
    return 0
  })
})

const getStatusColor = (status: string) => {
  switch (status) {
    case 'active': return 'success'
    case 'inactive': return 'info'
    case 'error': return 'danger'
    default: return 'info'
  }
}

const getStatusText = (status: string) => {
  switch (status) {
    case 'active': return '运行中'
    case 'inactive': return '已停止'
    case 'error': return '错误'
    default: return '未知'
  }
}

const formatCron = (cron: string) => {
  const cronMap: Record<string, string> = {
    '0 0 * * *': '每天午夜',
    '0 12 * * *': '每天中午',
    '0 * * * *': '每小时',
    '* * * * *': '每分钟',
    '0 9 * * 1': '每周一上午9点'
  }
  return cronMap[cron] || cron
}

const getSuccessRateColor = (rate: number) => {
  if (rate >= 90) return 'success'
  if (rate >= 70) return 'warning'
  return 'danger'
}
</script>

<template>
  <div class="rules-container">
    <div class="apple-container">
      <!-- Header -->
      <div class="page-header">
        <div class="header-content">
          <div class="title-section">
            <h1 class="page-title">巡检规则管理</h1>
            <p class="page-description">管理数据库质量巡检规则，查看执行历史和状态</p>
          </div>
          <div class="header-actions">
            <button class="apple-button apple-button-secondary" @click="refreshData" :disabled="loading">
              <el-icon><Refresh /></el-icon>
              刷新
            </button>
            <button class="apple-button apple-button-primary" @click="createRule">
              <el-icon><Plus /></el-icon>
              创建规则
            </button>
          </div>
        </div>
      </div>

      <!-- Statistics Cards -->
      <div class="stats-section">
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-icon active">
              <el-icon><CircleCheck /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ filteredRules.filter(r => r.status === 'active').length }}</div>
              <div class="stat-label">运行中规则</div>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon total">
              <el-icon><DataLine /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ filteredRules.length }}</div>
              <div class="stat-label">总规则数</div>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon success">
              <el-icon><CircleCheck /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ Math.round(filteredRules.reduce((sum, r) => sum + r.success_rate, 0) / (filteredRules.length || 1)) }}%</div>
              <div class="stat-label">平均成功率</div>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon warning">
              <el-icon><Warning /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ filteredRules.filter(r => r.success_rate < 80).length }}</div>
              <div class="stat-label">需关注规则</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Filters and Search -->
      <div class="filters-section">
        <div class="filters-left">
          <div class="search-box">
            <el-input
              v-model="searchQuery"
              placeholder="搜索规则名称、描述或数据源..."
              class="search-input"
              :prefix-icon="Search"
              clearable
            />
          </div>
          <el-select v-model="statusFilter" placeholder="状态筛选" clearable class="filter-select">
            <el-option label="运行中" value="active" />
            <el-option label="已停止" value="inactive" />
            <el-option label="错误" value="error" />
          </el-select>
        </div>
        <div class="filters-right">
          <el-select v-model="sortBy" class="sort-select">
            <el-option label="创建时间" value="created_at" />
            <el-option label="规则名称" value="name" />
            <el-option label="最后执行" value="last_run" />
          </el-select>
        </div>
      </div>

      <!-- Rules Table -->
      <div class="table-section">
        <div class="table-container">
          <el-table
            :data="filteredRules"
            :loading="loading"
            class="apple-table"
            row-class-name="apple-table-row"
            header-row-class-name="apple-table-header"
          >
            <el-table-column prop="name" label="规则名称" min-width="180">
              <template #default="{ row }">
                <div class="rule-name-cell">
                  <div class="rule-name">{{ row.name }}</div>
                  <div class="rule-description">{{ row.description }}</div>
                </div>
              </template>
            </el-table-column>
            
            <el-table-column label="配置信息" min-width="200">
              <template #default="{ row }">
                <div class="config-info">
                  <div class="config-row">
                    <span class="label">数据源:</span>
                    <span class="value">{{ row.data_source_name }}</span>
                  </div>
                  <div class="config-row">
                    <span class="label">项目:</span>
                    <span class="value">{{ row.project_name }}</span>
                  </div>
                  <div class="config-row">
                    <span class="label">调度:</span>
                    <span class="value">{{ formatCron(row.cron_schedule) }}</span>
                  </div>
                </div>
              </template>
            </el-table-column>

            <el-table-column label="执行状态" width="120">
              <template #default="{ row }">
                <div class="execution-status">
                  <el-tag :type="getStatusColor(row.status)" size="small">
                    {{ getStatusText(row.status) }}
                  </el-tag>
                  <div class="last-run" v-if="row.last_run_at">
                    {{ new Date(row.last_run_at).toLocaleString() }}
                  </div>
                </div>
              </template>
            </el-table-column>

            <el-table-column label="统计信息" width="120">
              <template #default="{ row }">
                <div class="stats-info">
                  <div class="execution-count">
                    执行 {{ row.execution_count }} 次
                  </div>
                  <div class="success-rate">
                    成功率:
                    <span :class="getSuccessRateColor(row.success_rate)">
                      {{ row.success_rate }}%
                    </span>
                  </div>
                </div>
              </template>
            </el-table-column>

            <el-table-column label="操作" width="200">
              <template #default="{ row }">
                <div class="action-buttons">
                  <button class="action-btn primary" @click="executeRule(row.id)" title="执行规则">
                    <el-icon><VideoPlay /></el-icon>
                  </button>
                  <button class="action-btn secondary" @click="viewExecutions(row.id)" title="查看执行历史">
                    <el-icon><Clock /></el-icon>
                  </button>
                  <button class="action-btn secondary" @click="editRule(row.id)" title="编辑规则">
                    <el-icon><Edit /></el-icon>
                  </button>
                  <button class="action-btn danger" @click="deleteRule(row.id)" title="删除规则">
                    <el-icon><Delete /></el-icon>
                  </button>
                </div>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <div v-if="filteredRules.length === 0 && !loading" class="empty-state">
          <el-icon class="empty-icon"><DataLine /></el-icon>
          <h3>暂无巡检规则</h3>
          <p>创建第一个巡检规则来开始监控你的数据质量</p>
          <button class="apple-button apple-button-primary" @click="createRule">
            <el-icon><Plus /></el-icon>
            创建规则
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.rules-container {
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

.title-section h1 {
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

.stat-icon.active {
  background: rgba(52, 199, 89, 0.1);
  color: var(--apple-green);
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

.rule-name-cell {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.rule-name {
  font-weight: 600;
  color: var(--gray-1);
  font-size: var(--font-size-base);
}

.rule-description {
  color: var(--gray-4);
  font-size: var(--font-size-sm);
  line-height: 1.4;
}

.config-info {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.config-row {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
}

.config-row .label {
  color: var(--gray-4);
  font-size: var(--font-size-xs);
  min-width: 50px;
}

.config-row .value {
  color: var(--gray-2);
  font-size: var(--font-size-sm);
  font-weight: 500;
}

.execution-status {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
  align-items: flex-start;
}

.last-run {
  color: var(--gray-4);
  font-size: var(--font-size-xs);
  text-align: left;
}

.stats-info {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.execution-count {
  color: var(--gray-4);
  font-size: var(--font-size-xs);
}

.success-rate {
  color: var(--gray-4);
  font-size: var(--font-size-xs);
}

.success-rate .success {
  color: var(--apple-green);
  font-weight: 600;
}

.success-rate .warning {
  color: var(--apple-orange);
  font-weight: 600;
}

.success-rate .danger {
  color: var(--apple-red);
  font-weight: 600;
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

.action-btn.primary:hover {
  background: var(--apple-blue);
  color: white;
  border-color: var(--apple-blue);
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
  
  .action-buttons {
    flex-wrap: wrap;
  }
}
</style>