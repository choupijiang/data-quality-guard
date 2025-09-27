<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { Folder, Delete, Edit, Plus, Search, Refresh } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/utils/api'

interface Project {
  id: number
  name: string
  description: string
  data_source_count: number
  task_count: number
  status: string
  created_at: string
}

const projects = ref<Project[]>([])
const loading = ref(false)
const searchQuery = ref('')
const statusFilter = ref('')
const sortBy = ref('created_at')

onMounted(() => {
  fetchProjects()
})

const fetchProjects = async () => {
  loading.value = true
  try {
    const response = await api.get('/api/v1/projects/')
    projects.value = response.data || []
  } catch {
    ElMessage.error('获取项目失败')
  } finally {
    loading.value = false
  }
}

const refreshData = () => {
  fetchProjects()
}

const hasActiveFilters = computed(() => {
  return searchQuery.value || statusFilter.value
})

const clearAllFilters = () => {
  searchQuery.value = ''
  statusFilter.value = ''
  sortBy.value = 'created_at_desc'
}


const filteredProjects = computed(() => {
  let filtered = [...projects.value]

  // 搜索过滤
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(project => 
      project.name.toLowerCase().includes(query) ||
      project.description.toLowerCase().includes(query)
    )
  }

  // 状态过滤
  if (statusFilter.value) {
    filtered = filtered.filter(project => project.status === statusFilter.value)
  }

  // 排序
  filtered.sort((a, b) => {
    switch (sortBy.value) {
      case 'name_asc':
        return a.name.localeCompare(b.name)
      case 'name_desc':
        return b.name.localeCompare(a.name)
      case 'created_at_asc':
        return new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
      case 'created_at_desc':
      default:
        return new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    }
  })

  return filtered
})

const deleteProject = async (id: number) => {
  try {
    await ElMessageBox.confirm('确定要删除这个项目吗？', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await api.delete(`/api/v1/projects/${id}`)
    ElMessage.success('项目删除成功')
    fetchProjects()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除项目失败')
    }
  }
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('zh-CN')
}
</script>

<template>
  <div class="projects-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-content">
        <div class="title-section">
          <h1>项目</h1>
          <p>管理数据库质量巡检项目</p>
        </div>
        <button class="apple-button apple-button-primary compact" @click="$router.push('/projects/create')">
          <el-icon><Plus /></el-icon>
          创建项目
        </button>
      </div>
    </div>

    <!-- Search and Filter Section -->
    <div class="filter-section">
      <div class="filter-card">
        <div class="filter-header">
          <div class="filter-title">
            <el-icon><Search /></el-icon>
            <span>搜索与筛选</span>
          </div>
          <div class="filter-stats" v-if="hasActiveFilters">
            <span class="results-count">{{ filteredProjects.length }} 个结果</span>
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
                placeholder="搜索项目名称或描述..."
                class="search-input"
                clearable
              />
            </div>
            
            <div class="filter-group">
              <div class="filter-item">
                <el-select v-model="statusFilter" placeholder="项目状态" clearable class="filter-select">
                  <el-option label="全部状态" value="" />
                  <el-option label="启用" value="active" />
                  <el-option label="禁用" value="inactive" />
                </el-select>
              </div>
              
              <div class="filter-item">
                <el-select v-model="sortBy" placeholder="排序方式" class="filter-select">
                  <el-option label="最新创建" value="created_at_desc" />
                  <el-option label="最早创建" value="created_at_asc" />
                  <el-option label="名称 A-Z" value="name_asc" />
                  <el-option label="名称 Z-A" value="name_desc" />
                </el-select>
              </div>
              
              <div class="filter-actions">
                <button class="refresh-btn" @click="refreshData" title="刷新数据">
                  <el-icon><Refresh /></el-icon>
                </button>
              </div>
            </div>
          </div>
          
          <!-- Active Filters Display -->
          <div class="active-filters" v-if="hasActiveFilters">
            <div class="active-filters-header">
              <span class="active-filters-label">已应用的筛选条件</span>
              <button class="clear-all-btn" @click="clearAllFilters">
                <el-icon><Delete /></el-icon>
                清除全部
              </button>
            </div>
            <div class="filter-tags">
              <el-tag 
                v-if="searchQuery" 
                closable 
                @close="searchQuery = ''"
                class="filter-tag search-tag"
              >
                <el-icon><Search /></el-icon>
                搜索: {{ searchQuery }}
              </el-tag>
              <el-tag 
                v-if="statusFilter" 
                closable 
                @close="statusFilter = ''"
                class="filter-tag status-tag"
                :type="statusFilter === 'active' ? 'success' : 'info'"
              >
                <el-icon><Folder /></el-icon>
                状态: {{ statusFilter === 'active' ? '启用' : '禁用' }}
              </el-tag>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="projects-grid">
      <div 
        v-for="project in filteredProjects" 
        :key="project.id"
        class="project-card"
      >
        <div class="card-header">
          <div class="project-info">
            <h3 class="project-name">{{ project.name }}</h3>
            <p class="project-description">{{ project.description }}</p>
          </div>
          <div class="project-status">
            <el-tag 
              :type="project.status === 'active' ? 'success' : 'info'"
              size="small"
            >
              {{ project.status === 'active' ? '启用中' : '已禁用' }}
            </el-tag>
          </div>
        </div>

        <div class="card-content">
          <div class="project-stats">
            <div class="stat-item">
              <div class="stat-value">{{ project.data_source_count }}</div>
              <div class="stat-label">数据源</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ project.task_count }}</div>
              <div class="stat-label">任务</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">100%</div>
              <div class="stat-label">成功率</div>
            </div>
          </div>
          
          <div class="project-meta">
            <span class="meta-value">{{ formatDate(project.created_at) }}</span>
          </div>
        </div>

        <div class="card-actions">
          <button class="action-btn edit-btn" @click="$router.push(`/projects/${project.id}/edit`)" title="编辑项目">
            <el-icon><Edit /></el-icon>
          </button>
          <button class="action-btn delete-btn" @click="deleteProject(project.id)" title="删除项目">
            <el-icon><Delete /></el-icon>
          </button>
        </div>
      </div>

      <!-- Empty State -->
      <div v-if="projects.length === 0 && !loading" class="empty-state">
        <div class="empty-icon">
          <el-icon><Folder /></el-icon>
        </div>
        <h3 class="empty-title">暂无项目</h3>
        <p class="empty-description">创建您的第一个数据库质量巡检项目</p>
        <button class="apple-button apple-button-primary" @click="$router.push('/projects/create')">
          <el-icon><Plus /></el-icon>
          创建项目
        </button>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="loading-state">
        <el-icon class="loading-icon"><Folder /></el-icon>
        <p>加载中...</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Apple-style Projects Container */
.projects-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  position: relative;
}

.projects-container::before {
  content: '';
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: 
    radial-gradient(circle at 20% 80%, rgba(0, 122, 255, 0.03) 0%, transparent 50%),
    radial-gradient(circle at 80% 20%, rgba(52, 199, 89, 0.03) 0%, transparent 50%),
    radial-gradient(circle at 40% 40%, rgba(255, 149, 0, 0.02) 0%, transparent 50%);
  pointer-events: none;
  z-index: 0;
}

/* Page Header */
.page-header {
  padding: var(--spacing-2xl) 0;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(248, 248, 248, 0.95) 100%);
  border-bottom: 1px solid var(--gray-9);
  backdrop-filter: blur(20px);
  position: relative;
  z-index: 1;
}

/* Search and Filter Section */
.search-filter-section {
  background: var(--gray-8);
  border-bottom: 1px solid var(--gray-5);
  padding: var(--spacing-lg) 0;
}

.search-filter-content {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.search-bar {
  max-width: 500px;
}

.search-input {
  width: 100%;
}

.filter-controls {
  display: flex;
  gap: var(--spacing-md);
  align-items: center;
  flex-wrap: wrap;
}

.filter-select,
.sort-select {
  min-width: 150px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 var(--spacing-lg);
}

.title-section h1 {
  font-size: var(--font-size-3xl);
  font-weight: 700;
  color: var(--gray-1);
  margin: 0 0 var(--spacing-sm) 0;
}

.title-section p {
  font-size: var(--font-size-lg);
  color: var(--gray-3);
  margin: 0;
}

/* Projects Grid */
.projects-grid {
  max-width: 1200px;
  margin: 0 auto;
  padding: var(--spacing-xl);
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: var(--spacing-lg);
}

/* Project Card */
/* Project Card - Redesigned Compact */
.project-card {
  background: rgba(255, 255, 255, 0.98);
  border: 1px solid var(--gray-9);
  border-radius: var(--radius-lg);
  padding: var(--spacing-md);
  transition: all var(--transition-normal);
  display: flex;
  flex-direction: column;
  height: 220px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  position: relative;
  overflow: hidden;
  z-index: 1;
}

.project-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, 
    transparent 0%, 
    rgba(0, 122, 255, 0.3) 50%, 
    transparent 100%);
  opacity: 0;
  transition: opacity var(--transition-normal);
}

.project-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
  border-color: var(--gray-7);
}

.project-card:hover::before {
  opacity: 1;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--spacing-sm);
}

.project-info h3 {
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--gray-1);
  margin: 0 0 var(--spacing-xs) 0;
  line-height: 1.3;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.project-description {
  font-size: var(--font-size-xs);
  color: var(--gray-4);
  margin: 0;
  line-height: 1.3;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.project-status {
  flex-shrink: 0;
  margin-left: var(--spacing-sm);
}

.project-status .el-tag {
  font-weight: 500;
  border-radius: var(--radius-md);
}

/* Card Content */
.card-content {
  flex: 1;
  margin-bottom: var(--spacing-sm);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

/* Project Status */
.project-status {
  margin-bottom: var(--spacing-md);
}

.project-status .el-tag {
  font-weight: 500;
  border-radius: var(--radius-md);
}

/* Project Stats - Compact */
.project-stats {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--radius-md);
  background: linear-gradient(135deg, var(--gray-11) 0%, var(--gray-10) 100%);
  margin-bottom: var(--spacing-sm);
  border: 1px solid var(--gray-9);
  position: relative;
  overflow: hidden;
}

.project-stats::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, 
    rgba(0, 122, 255, 0.05) 0%, 
    rgba(52, 199, 89, 0.03) 50%,
    rgba(255, 149, 0, 0.05) 100%);
  pointer-events: none;
}

.stat-item {
  text-align: center;
  flex: 1;
  min-width: 0;
}

.stat-value {
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--gray-1);
  line-height: 1.2;
}

.stat-label {
  font-size: var(--font-size-xs);
  color: var(--gray-4);
  margin-top: var(--spacing-xs);
  line-height: 1.2;
}


/* Project Meta - Compact */
.project-meta {
  text-align: center;
}

.meta-value {
  font-size: var(--font-size-xs);
  color: var(--gray-6);
  background: linear-gradient(135deg, var(--gray-11) 0%, var(--gray-10) 100%);
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--radius-md);
  display: inline-block;
  border: 1px solid var(--gray-9);
  font-weight: 500;
}



/* Card Actions - Compact */
.card-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--spacing-sm);
  padding-top: var(--spacing-sm);
  border-top: 1px solid var(--gray-5);
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

/* Edit Button - Blue Theme */
.edit-btn {
  border-color: var(--apple-blue);
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(0, 122, 255, 0.1) 100%);
  color: var(--apple-blue);
}

.edit-btn:hover {
  background: linear-gradient(135deg, var(--apple-blue) 0%, #0051D5 100%);
  color: white;
  border-color: var(--apple-blue);
  box-shadow: 0 4px 16px rgba(0, 122, 255, 0.25);
}

/* Delete Button - Red Theme */
.delete-btn {
  border-color: var(--apple-red);
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(255, 59, 48, 0.1) 100%);
  color: var(--apple-red);
}

.delete-btn:hover {
  background: linear-gradient(135deg, var(--apple-red) 0%, #D70015 100%);
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

/* Compact button style */
.apple-button.compact {
  flex: none;
  min-width: 120px;
  padding: var(--spacing-md) var(--spacing-lg);
  font-size: var(--font-size-sm);
}

/* Page header optimizations */
.page-header {
  padding: var(--spacing-xl) 0;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(248, 248, 248, 0.95) 100%);
  border-bottom: 1px solid var(--gray-9);
  backdrop-filter: blur(20px);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 var(--spacing-lg);
}

.title-section h1 {
  font-size: var(--font-size-2xl);
  font-weight: 700;
  color: var(--gray-1);
  margin: 0 0 var(--spacing-xs) 0;
}

.title-section p {
  font-size: var(--font-size-base);
  color: var(--gray-3);
  margin: 0;
}

/* Filter Section - Enhanced Design */
.filter-section {
  max-width: 1200px;
  margin: 0 auto;
  padding: var(--spacing-lg);
}

.filter-card {
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid var(--gray-9);
  border-radius: var(--radius-lg);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  transition: all var(--transition-normal);
  overflow: hidden;
  backdrop-filter: blur(20px);
  position: relative;
  z-index: 1;
}

.filter-card:hover {
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
  border-color: var(--gray-8);
  transform: translateY(-2px);
}

/* Filter Header */
.filter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-lg) var(--spacing-lg) 0;
  margin-bottom: var(--spacing-lg);
}

.filter-title {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--gray-1);
}

.filter-title .el-icon {
  color: var(--apple-blue);
  font-size: 18px;
}

.filter-stats {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.results-count {
  font-size: var(--font-size-sm);
  color: var(--gray-3);
  background: var(--gray-8);
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--radius-md);
  border: 1px solid var(--gray-5);
}

/* Filter Content */
.filter-content {
  padding: 0 var(--spacing-lg) var(--spacing-lg);
}

.filter-row {
  display: flex;
  align-items: center;
  gap: var(--spacing-lg);
  width: 100%;
}

/* Search Container - Enhanced */
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

.search-input .el-input__inner::placeholder {
  color: var(--gray-4);
}

/* Filter Group - Enhanced */
.filter-group {
  display: flex;
  gap: var(--spacing-md);
  align-items: center;
  flex-shrink: 0;
  flex: 1;
}

.filter-item {
  min-width: 140px;
  flex: 1;
}

.filter-select {
  width: 100%;
}

.filter-select .el-select__wrapper {
  background: var(--gray-8);
  border: 2px solid var(--gray-5);
  border-radius: var(--radius-lg);
  padding: var(--spacing-sm) var(--spacing-md);
  transition: all var(--transition-normal);
  height: 44px;
}

.filter-select .el-select__wrapper:hover {
  border-color: var(--gray-4);
  background: var(--gray-7);
}

.filter-select .el-select__wrapper.is-focus {
  border-color: var(--apple-blue);
  box-shadow: 0 0 0 3px rgba(0, 122, 255, 0.15);
  background: var(--gray-7);
}

/* Filter Actions - Enhanced */
.filter-actions {
  display: flex;
  align-items: center;
  flex-shrink: 0;
}

.refresh-btn {
  width: 44px;
  height: 44px;
  border: 2px solid var(--gray-5);
  border-radius: var(--radius-lg);
  background: var(--gray-8);
  color: var(--gray-3);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all var(--transition-normal);
}

.refresh-btn:hover {
  background: var(--gray-7);
  border-color: var(--apple-blue);
  color: var(--apple-blue);
  transform: rotate(180deg);
  box-shadow: 0 2px 8px rgba(0, 122, 255, 0.2);
}

.refresh-btn:active {
  transform: rotate(180deg) scale(0.95);
}

/* Active Filters - Enhanced */
.active-filters {
  margin-top: var(--spacing-lg);
  padding-top: var(--spacing-lg);
  border-top: 1px solid var(--gray-5);
}

.active-filters-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-md);
}

.active-filters-label {
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--gray-2);
  white-space: nowrap;
}

.clear-all-btn {
  font-size: var(--font-size-sm);
  color: var(--apple-red);
  background: none;
  border: 1px solid var(--gray-5);
  cursor: pointer;
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--radius-md);
  transition: all var(--transition-normal);
  white-space: nowrap;
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
}

.clear-all-btn:hover {
  background: rgba(255, 59, 48, 0.1);
  border-color: var(--apple-red);
  transform: translateY(-1px);
}

.clear-all-btn .el-icon {
  font-size: 14px;
}

.filter-tags {
  display: flex;
  gap: var(--spacing-sm);
  flex-wrap: wrap;
}

.filter-tag {
  font-size: var(--font-size-sm);
  border-radius: var(--radius-lg);
  padding: var(--spacing-xs) var(--spacing-sm);
  border: 1px solid var(--gray-5);
  background: var(--gray-8);
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  transition: all var(--transition-normal);
}

.filter-tag:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}

.filter-tag.search-tag {
  border-color: var(--apple-blue);
  background: rgba(0, 122, 255, 0.05);
}

.filter-tag.status-tag {
  border-color: var(--apple-green);
  background: rgba(52, 199, 89, 0.05);
}

.filter-tag .el-icon {
  font-size: 12px;
}

.projects-grid {
  max-width: 1200px;
  margin: 0 auto;
  padding: var(--spacing-lg);
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: var(--spacing-md);
}

/* Empty State */
.empty-state {
  grid-column: 1 / -1;
  text-align: center;
  padding: var(--spacing-3xl);
  background: var(--gray-9);
  border: 1px solid var(--gray-5);
  border-radius: var(--radius-lg);
  border-style: dashed;
}

.empty-icon {
  width: 64px;
  height: 64px;
  margin: 0 auto var(--spacing-lg);
  background: rgba(0, 122, 255, 0.1);
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-icon .el-icon {
  width: 32px;
  height: 32px;
  color: var(--apple-blue);
}

.empty-title {
  font-size: var(--font-size-xl);
  font-weight: 600;
  color: var(--gray-1);
  margin: 0 0 var(--spacing-sm) 0;
}

.empty-description {
  font-size: var(--font-size-base);
  color: var(--gray-3);
  margin: 0 0 var(--spacing-xl) 0;
}

/* Loading State */
.loading-state {
  grid-column: 1 / -1;
  text-align: center;
  padding: var(--spacing-3xl);
  color: var(--gray-3);
}

.loading-icon {
  width: 48px;
  height: 48px;
  margin: 0 auto var(--spacing-md);
  color: var(--apple-blue);
  animation: apple-spin 1s linear infinite;
}

/* Responsive Design - Enhanced */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: var(--spacing-lg);
    text-align: center;
  }
  
  .filter-section {
    padding: var(--spacing-md);
  }
  
  .filter-card {
    padding: var(--spacing-md);
  }
  
  .filter-header {
    flex-direction: column;
    gap: var(--spacing-sm);
    align-items: flex-start;
    padding: var(--spacing-md) var(--spacing-md) 0;
  }
  
  .filter-content {
    padding: 0 var(--spacing-md) var(--spacing-md);
  }
  
  .filter-row {
    flex-direction: column;
    gap: var(--spacing-md);
    align-items: stretch;
  }
  
  .search-container {
    min-width: 100%;
    max-width: 100%;
    height: 40px;
    flex: none;
  }
  
  .filter-group {
    flex-direction: column;
    gap: var(--spacing-sm);
    flex: none;
  }
  
  .filter-item {
    min-width: 100%;
    flex: none;
  }
  
  .filter-select .el-select__wrapper {
    height: 40px;
  }
  
  .refresh-btn {
    width: 40px;
    height: 40px;
  }
  
  .filter-actions {
    justify-content: flex-end;
    width: 100%;
  }
  
  .active-filters-header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-sm);
  }
  
  .filter-tags {
    width: 100%;
  }
  
  .clear-all-btn {
    align-self: flex-end;
  }
  
  .projects-grid {
    grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
    padding: var(--spacing-md);
  }
  
  .project-card {
    height: 160px;
  }
  
  .project-info h3 {
    font-size: var(--font-size-base);
  }
  
  .project-description {
    font-size: var(--font-size-xs);
  }
  
  .stat-value {
    font-size: var(--font-size-base);
  }
  
  .stat-label {
    font-size: var(--font-size-xs);
  }
  
  .card-actions {
    gap: var(--spacing-xs);
  }
  
  .action-btn {
    width: 32px;
    height: 32px;
  }
  
  .action-btn .el-icon {
    width: 16px;
    height: 16px;
    font-size: 16px;
  }
}

@media (max-width: 480px) {
  .page-header {
    padding: var(--spacing-xl) 0;
  }
  
  .filter-group {
    flex-direction: column;
    gap: var(--spacing-sm);
  }
  
  .filter-item {
    min-width: 100%;
  }
  
  .filter-actions {
    justify-content: flex-end;
  }
  
  .title-section h1 {
    font-size: var(--font-size-2xl);
  }
  
  .projects-grid {
    padding: var(--spacing-sm);
  }
}

/* Animations */
.project-card {
  animation: apple-fade-in 0.5s ease-out;
}

.project-card:nth-child(1) { animation-delay: 0.1s; }
.project-card:nth-child(2) { animation-delay: 0.2s; }
.project-card:nth-child(3) { animation-delay: 0.3s; }
.project-card:nth-child(4) { animation-delay: 0.4s; }
</style>