<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { Connection, Cpu, Refresh } from '@element-plus/icons-vue'
import { DashboardService, type GlobalStatistics, type ProjectStatistics } from '@/services/dashboard'
import ProjectStatsCard from '@/components/ProjectStatsCard.vue'
import GlobalStats from '@/components/GlobalStats.vue'
import api from '@/utils/api'

const router = useRouter()
const isConnected = ref(false)
const loading = ref(false)
const globalStats = ref<GlobalStatistics>({
  total_projects: 0,
  total_tasks: 0,
  successful_tasks: 0,
  failed_tasks: 0,
  overall_success_rate: 0
})
const projectStats = ref<ProjectStatistics[]>([])
const lastRefreshTime = ref<Date>(new Date())
let refreshTimer: NodeJS.Timeout | null = null

const getSuccessColor = (rate: number) => {
  if (rate >= 80) return 'var(--apple-green)'
  if (rate >= 60) return 'var(--apple-orange)'
  return 'var(--apple-red)'
}

const getSuccessStatus = (rate: number) => {
  if (rate >= 80) return '优秀'
  if (rate >= 60) return '一般'
  return '需关注'
}

const formatRefreshTime = () => {
  const now = new Date(lastRefreshTime.value)
  const hours = now.getHours().toString().padStart(2, '0')
  const minutes = now.getMinutes().toString().padStart(2, '0')
  const seconds = now.getSeconds().toString().padStart(2, '0')
  return `${hours}:${minutes}:${seconds}`
}

const startAutoRefresh = () => {
  // 清除可能存在的旧定时器
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
  
  // 设置新的定时器，每5秒刷新一次
  refreshTimer = setInterval(() => {
    checkConnection()
    loadDashboardData()
    lastRefreshTime.value = new Date()
  }, 5000)
}

const stopAutoRefresh = () => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = null
  }
}

onMounted(() => {
  checkConnection()
  loadDashboardData()
  startAutoRefresh()
})

onUnmounted(() => {
  stopAutoRefresh()
})

const checkConnection = async () => {
  try {
    await api.get('/health')
    isConnected.value = true
  } catch {
    isConnected.value = false
  }
}

const loadDashboardData = async () => {
  loading.value = true
  try {
    const [globalData, projectData] = await Promise.all([
      DashboardService.getGlobalStatistics(),
      DashboardService.getProjectStatistics()
    ])
    
    globalStats.value = globalData
    projectStats.value = projectData
  } catch (error) {
    console.error('Failed to load dashboard data:', error)
  } finally {
    loading.value = false
  }
}

</script>

<template>
  <div class="home-container">
    <!-- Compact Hero Section -->
    <section class="hero-section">
      <div class="apple-container">
        <div class="hero-content">
          <div class="hero-header">
            <div class="title-section"> 
              <h1 class="hero-title">
                 <span class="gradient-text">数据质量巡检</span>
              </h1>
            </div>
            <div class="hero-actions">
              <div class="auto-refresh-info">
                <el-icon class="refresh-icon"><Refresh /></el-icon>
                <span>最后刷新: {{ formatRefreshTime() }}</span>
              </div>
            </div>
          </div>
          
          </div>
      </div>
    </section>

    <!-- Compact Global Statistics -->
    <section class="global-stats-section">
      <div class="apple-container">
        <div class="section-header">
          <div class="section-info">
            <h2 class="section-title">系统概览</h2>
            <p class="section-subtitle">整体运行状态监控</p>
          </div>
        </div>
        
        <GlobalStats :statistics="globalStats" />
      </div>
    </section>

    <!-- Project Statistics Section -->
    <section class="project-stats-section">
      <div class="apple-container">
        <div class="section-header">
          <div class="section-info">
            <h2 class="section-title">项目监控</h2>
            <p class="section-subtitle">各项目执行情况</p>
          </div> 
        </div>
        
        <div v-if="loading" class="loading-container">
          <el-icon class="loading-icon"><Refresh /></el-icon>
          <p>加载统计数据...</p>
        </div>
        
        <div v-else-if="projectStats.length === 0" class="empty-state">
          <div class="empty-icon">
            <el-icon><Connection /></el-icon>
          </div>
          <h3 class="empty-title">暂无项目统计</h3>
          <p class="empty-description">创建您的第一个数据库质量巡检项目</p>
          <button class="apple-button apple-button-primary" @click="router.push('/projects')">
            <el-icon><Connection /></el-icon>
            创建项目
          </button>
        </div>
        
        <div v-else class="project-grid">
          <ProjectStatsCard 
            v-for="stats in projectStats" 
            :key="stats.project_id"
            :statistics="stats"
          />
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
/* Hero Section */
.hero-section {
  padding: var(--spacing-3xl) 0 var(--spacing-xl) 0;
  background: linear-gradient(135deg, var(--gray-9) 0%, var(--gray-8) 100%);
  text-align: center;
}

.hero-content {
  max-width: 1000px;
  margin: 0 auto;
  padding: 0 var(--spacing-lg);
}

.hero-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-xl);
  gap: var(--spacing-lg);
}

.title-section {
  flex: 1;
  text-align: left;
}

.apple-badge {
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-sm);
  background: rgba(0, 122, 255, 0.1);
  border: 1px solid rgba(0, 122, 255, 0.2);
  border-radius: var(--radius-full);
  padding: var(--spacing-sm) var(--spacing-md);
  color: var(--apple-blue);
  font-size: var(--font-size-sm);
  font-weight: 500;
  margin-bottom: var(--spacing-md);
}

.hero-title {
  font-size: var(--font-size-4xl);
  font-weight: 700;
  line-height: 1.1;
  margin: 0;
  color: var(--gray-1);
}

.gradient-text {
  background: linear-gradient(135deg, var(--apple-blue) 0%, var(--apple-purple) 100%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

.hero-actions {
  display: flex;
  gap: var(--spacing-sm);
  flex-shrink: 0;
}

.auto-refresh-info {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: var(--radius-full);
  padding: var(--spacing-sm) var(--spacing-md);
  color: var(--gray-2);
  font-size: var(--font-size-sm);
  font-weight: 500;
}

.refresh-icon {
  width: 14px;
  height: 14px;
  color: var(--apple-blue);
  animation: apple-spin 2s linear infinite;
}

@keyframes apple-spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Quick Stats Row */
.quick-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--spacing-lg);
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--gray-5);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
  margin-top: var(--spacing-lg);
}

.quick-stat-item {
  text-align: center;
}

.quick-stat-value {
  font-size: var(--font-size-2xl);
  font-weight: 600;
  color: var(--gray-1);
  line-height: 1.2;
  margin-bottom: var(--spacing-xs);
}

.quick-stat-label {
  font-size: var(--font-size-sm);
  color: var(--gray-3);
  font-weight: 500;
}

.status-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-sm);
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: var(--radius-full);
  background: var(--apple-red);
  transition: all var(--transition-fast);
}

.status-dot.active {
  background: var(--apple-green);
}

.status-text {
  font-size: var(--font-size-sm);
  color: var(--gray-3);
  font-weight: 500;
}


/* Global Statistics Section */
.global-stats-section {
  padding: var(--spacing-2xl) 0;
  background: var(--gray-9);
}

.global-stats-section .apple-container {
  max-width: 1000px;
}

.global-stats-section .section-header {
  margin-bottom: var(--spacing-lg);
}

/* Project Statistics Section */
.project-stats-section {
  padding: var(--spacing-2xl) 0 var(--spacing-3xl) 0;
  background: var(--gray-9);
}

.project-stats-section .apple-container {
  max-width: 1000px;
}

.project-stats-section .section-header {
  margin-bottom: var(--spacing-lg);
}

.project-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: var(--spacing-lg);
}

.loading-container {
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

.empty-state {
  grid-column: 1 / -1;
  text-align: center;
  padding: var(--spacing-3xl);
  background: var(--gray-8);
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

/* Common Section Styles */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-lg);
}

.section-actions {
  display: flex;
  gap: var(--spacing-md);
}

.section-title {
  font-size: var(--font-size-2xl);
  font-weight: 700;
  margin-bottom: var(--spacing-xs);
  color: var(--gray-1);
}

.section-subtitle {
  font-size: var(--font-size-base);
  color: var(--gray-3);
  max-width: 500px;
  margin: 0;
}

.section-info {
  flex: 1;
}



/* Responsive Design */
@media (max-width: 768px) {
  .hero-header {
    flex-direction: column;
    gap: var(--spacing-lg);
    text-align: center;
  }
  
  .title-section {
    text-align: center;
  }
  
  .hero-title {
    font-size: var(--font-size-3xl);
  }
  
  .quick-stats {
    grid-template-columns: repeat(2, 1fr);
    gap: var(--spacing-md);
  }
  
  .hero-actions {
    flex-direction: column;
    width: 100%;
  }
  
  .apple-button {
    width: 100%;
  }
  
  .section-header {
    flex-direction: column;
    gap: var(--spacing-md);
    text-align: center;
  }
  
  .section-actions {
    justify-content: center;
    flex-direction: column;
    width: 100%;
  }
  
  .project-grid {
    grid-template-columns: 1fr;
    gap: var(--spacing-md);
  }
  
  .apple-container {
    padding: 0 var(--spacing-md);
  }
}

@media (max-width: 480px) {
  .hero-title {
    font-size: var(--font-size-2xl);
  }
  
  .quick-stats {
    grid-template-columns: 1fr;
    gap: var(--spacing-sm);
  }
  
  .section-title {
    font-size: var(--font-size-xl);
  }
  
  .apple-button {
    width: 100%;
  }
  
  .apple-container {
    padding: 0 var(--spacing-sm);
  }
  
  .hero-section {
    padding: var(--spacing-2xl) 0 var(--spacing-lg) 0;
  }
  
  .global-stats-section,
  .project-stats-section {
    padding: var(--spacing-lg) 0;
  }
}

/* Animations */
.hero-section {
  animation: apple-fade-in 0.6s ease-out;
}

.project-stats-section {
  animation: apple-slide-up 0.6s ease-out 0.2s both;
}
</style>
