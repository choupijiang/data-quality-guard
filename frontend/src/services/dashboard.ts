import api from '@/utils/api'

export interface ProjectStatistics {
  project_id: number
  project_name: string
  total_tasks: number
  successful_tasks: number
  failed_tasks: number
  success_rate: number
}

export interface GlobalStatistics {
  total_projects: number
  total_tasks: number
  successful_tasks: number
  failed_tasks: number
  overall_success_rate: number
}

export class DashboardService {
  static async getProjectStatistics(): Promise<ProjectStatistics[]> {
    try {
      const response = await api.get('/api/v1/dashboard/project-statistics')
      return response.data
    } catch (error) {
      console.error('Failed to fetch project statistics:', error)
      return []
    }
  }

  static async getGlobalStatistics(): Promise<GlobalStatistics> {
    try {
      const response = await api.get('/api/v1/dashboard/statistics')
      return response.data
    } catch (error) {
      console.error('Failed to fetch global statistics:', error)
      return {
        total_projects: 0,
        total_tasks: 0,
        successful_tasks: 0,
        failed_tasks: 0,
        overall_success_rate: 0
      }
    }
  }

  static getSuccessColor(rate: number): string {
    if (rate >= 80) return 'var(--apple-green)'
    if (rate >= 60) return 'var(--apple-orange)'
    return 'var(--apple-red)'
  }

  static getSuccessStatus(rate: number): string {
    if (rate >= 80) return '优秀'
    if (rate >= 60) return '一般'
    return '需关注'
  }

  static getProjectHealthStatus(stats: ProjectStatistics): {
    color: string
    status: string
    icon: string
  } {
    if (stats.total_tasks === 0) {
      return {
        color: 'var(--apple-orange)',
        status: '无任务',
        icon: 'warning'
      }
    }
    
    if (stats.success_rate >= 90) {
      return {
        color: 'var(--apple-green)',
        status: '健康',
        icon: 'success'
      }
    }
    
    if (stats.success_rate >= 70) {
      return {
        color: 'var(--apple-orange)',
        status: '一般',
        icon: 'warning'
      }
    }
    
    return {
      color: 'var(--apple-red)',
      status: '需关注',
      icon: 'error'
    }
  }
}