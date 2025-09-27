<script setup lang="ts">
import { computed } from 'vue'
import { 
  Connection, 
  Cpu, 
  Histogram, 
  DataAnalysis, 
  TrendCharts,
  Monitor,
  Check,
  Close
} from '@element-plus/icons-vue'
import { DashboardService, type GlobalStatistics } from '@/services/dashboard'

interface Props {
  statistics: GlobalStatistics
}

const props = defineProps<Props>()

const successColor = computed(() => 
  DashboardService.getSuccessColor(props.statistics.overall_success_rate)
)

const successStatus = computed(() => 
  DashboardService.getSuccessStatus(props.statistics.overall_success_rate)
)
</script>

<template>
  <div class="global-stats-container">
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon-wrapper">
          <el-icon class="stat-icon"><Connection /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ statistics.total_projects }}</div>
          <div class="stat-label">项目总数</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon-wrapper">
          <el-icon class="stat-icon"><Cpu /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ statistics.total_tasks }}</div>
          <div class="stat-label">任务总数</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon-wrapper">
          <el-icon class="stat-icon success"><Check /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value success">{{ statistics.successful_tasks }}</div>
          <div class="stat-label">成功任务</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon-wrapper">
          <el-icon class="stat-icon danger"><Close /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value danger">{{ statistics.failed_tasks }}</div>
          <div class="stat-label">失败任务</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon-wrapper">
          <el-icon class="stat-icon" :style="{ color: successColor }">
            <DataAnalysis />
          </el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value" :style="{ color: successColor }">
            {{ statistics.overall_success_rate.toFixed(1) }}%
          </div>
          <div class="stat-label">总体成功率</div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.global-stats-container {
  background: var(--gray-9);
  border: 1px solid var(--gray-5);
  border-radius: var(--radius-lg);
  padding: var(--spacing-md);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: var(--spacing-md);
}

.stat-card {
  background: var(--gray-8);
  border: 1px solid var(--gray-5);
  border-radius: var(--radius-lg);
  padding: var(--spacing-md);
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  transition: all var(--transition-normal);
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
  border-color: var(--gray-4);
}

.stat-icon-wrapper {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-md);
  background: rgba(0, 122, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-icon {
  width: 20px;
  height: 20px;
  color: var(--apple-blue);
}

.stat-icon.success {
  color: var(--apple-green);
}

.stat-icon.danger {
  color: var(--apple-red);
}

.stat-content {
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

/* Responsive Design */
@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: var(--spacing-sm);
  }
}

@media (max-width: 480px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .stat-icon-wrapper {
    width: 36px;
    height: 36px;
  }
  
  .stat-icon {
    width: 18px;
    height: 18px;
  }
}

/* Animations */
.stat-card {
  animation: apple-fade-in 0.5s ease-out;
}

.stat-card:nth-child(1) { animation-delay: 0.1s; }
.stat-card:nth-child(2) { animation-delay: 0.2s; }
.stat-card:nth-child(3) { animation-delay: 0.3s; }
.stat-card:nth-child(4) { animation-delay: 0.4s; }
.stat-card:nth-child(5) { animation-delay: 0.5s; }
</style>