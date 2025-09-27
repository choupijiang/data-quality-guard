<script setup lang="ts">
import { computed } from 'vue'
import { Folder, Check, Close, Warning } from '@element-plus/icons-vue'
import { DashboardService, type ProjectStatistics } from '@/services/dashboard'

interface Props {
  statistics: ProjectStatistics
}

const props = defineProps<Props>()

const healthStatus = computed(() => 
  DashboardService.getProjectHealthStatus(props.statistics)
)

const successColor = computed(() => 
  DashboardService.getSuccessColor(props.statistics.success_rate)
)

const successStatus = computed(() => 
  DashboardService.getSuccessStatus(props.statistics.success_rate)
)

const getHealthIcon = (icon: string) => {
  switch (icon) {
    case 'success':
      return Check
    case 'warning':
      return Warning
    case 'error':
      return Close
    default:
      return Folder
  }
}
</script>

<template>
  <div class="project-stats-card">
    <div class="card-header">
      <div class="project-info">
        <h3 class="project-name">{{ statistics.project_name }}</h3>
        <div class="project-health">
          <div 
            class="health-indicator"
            :style="{ backgroundColor: healthStatus.color }"
          ></div>
          <span class="health-status" :style="{ color: healthStatus.color }">
            {{ healthStatus.status }}
          </span>
        </div>
      </div>
      <div class="project-icon">
        <el-icon><component :is="getHealthIcon(healthStatus.icon)" /></el-icon>
      </div>
    </div>

    <div class="card-content">
      <div class="stats-grid">
        <div class="stat-item">
          <div class="stat-value">{{ statistics.total_tasks }}</div>
          <div class="stat-label">总任务</div>
        </div>
        <div class="stat-divider"></div>
        <div class="stat-item">
          <div class="stat-value success">{{ statistics.successful_tasks }}</div>
          <div class="stat-label">通过</div>
        </div>
        <div class="stat-divider"></div>
        <div class="stat-item">
          <div class="stat-value danger">{{ statistics.failed_tasks }}</div>
          <div class="stat-label">失败</div>
        </div>
      </div>

      <div class="success-rate-section">
        <div class="rate-header">
          <span class="rate-label">成功率</span>
          <span class="rate-value" :style="{ color: successColor }">
            {{ statistics.success_rate.toFixed(1) }}%
          </span>
        </div>
        <div class="progress-bar">
          <div 
            class="progress-fill"
            :style="{ 
              width: statistics.success_rate + '%',
              backgroundColor: successColor 
            }"
          ></div>
        </div>
        <div class="rate-status">{{ successStatus }}</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.project-stats-card {
  background: var(--gray-9);
  border: 1px solid var(--gray-5);
  border-radius: var(--radius-lg);
  padding: var(--spacing-md);
  transition: all var(--transition-normal);
  display: flex;
  flex-direction: column;
  height: 100%;
}

.project-stats-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
  border-color: var(--gray-4);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-md);
}

.project-info {
  flex: 1;
}

.project-name {
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--gray-1);
  margin: 0;
  line-height: 1.2;
}

.project-health {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.health-indicator {
  width: 8px;
  height: 8px;
  border-radius: var(--radius-full);
  transition: all var(--transition-fast);
}

.health-status {
  font-size: var(--font-size-sm);
  font-weight: 500;
}

.project-icon {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-md);
  background: rgba(0, 122, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.project-icon .el-icon {
  width: 20px;
  height: 20px;
  color: var(--apple-blue);
}

.card-content {
  flex: 1;
  margin-bottom: var(--spacing-md);
}

.stats-grid {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-md);
}

.stat-item {
  text-align: center;
  flex: 1;
}

.stat-value {
  font-size: var(--font-size-xl);
  font-weight: 600;
  color: var(--gray-1);
  line-height: 1.1;
}

.stat-value.success {
  color: var(--apple-green);
}

.stat-value.danger {
  color: var(--apple-red);
}

.stat-label {
  font-size: var(--font-size-xs);
  color: var(--gray-3);
  margin-top: 2px;
}

.stat-divider {
  width: 1px;
  height: 32px;
  background: var(--gray-5);
}

.success-rate-section {
  background: var(--gray-8);
  border-radius: var(--radius-md);
  padding: var(--spacing-sm);
}

.rate-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-xs);
}

.rate-label {
  font-size: var(--font-size-sm);
  color: var(--gray-3);
  font-weight: 500;
}

.rate-value {
  font-size: var(--font-size-base);
  font-weight: 600;
}

.progress-bar {
  height: 4px;
  background: var(--gray-6);
  border-radius: var(--radius-full);
  overflow: hidden;
  margin-bottom: var(--spacing-xs);
}

.progress-fill {
  height: 100%;
  border-radius: var(--radius-full);
  transition: width var(--transition-normal);
}

.rate-status {
  font-size: var(--font-size-xs);
  color: var(--gray-3);
  text-align: center;
}

.card-actions {
  display: flex;
  gap: var(--spacing-xs);
}

.apple-button {
  flex: 1;
  justify-content: center;
}

/* Responsive Design */
@media (max-width: 768px) {
  .stats-grid {
    gap: var(--spacing-sm);
  }
  
  .card-actions {
    flex-direction: column;
  }
  
  .apple-button {
    width: 100%;
  }
}

/* Animations */
.project-stats-card {
  animation: apple-fade-in 0.5s ease-out;
}
</style>