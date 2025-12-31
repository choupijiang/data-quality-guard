<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
import { onMounted, onUnmounted, ref, computed } from 'vue'
import { DataAnalysis, Cpu, Monitor, Connection, Setting, ArrowDown, User, SwitchButton } from '@element-plus/icons-vue'
import api from '@/utils/api'
import { useAuthStore } from '@/stores/auth'

interface NavStats {
  dataSources: number
  tasks: number
  projects: number
}

const authStore = useAuthStore()

const navStats = ref<NavStats>({
  dataSources: 0,
  tasks: 0,
  projects: 0
})

const showSettingsDropdown = ref(false)
const showUserDropdown = ref(false)

// 生成随机头像
const generateUserAvatar = (username: string) => {
  // 基于用户名生成一致的随机颜色
  const colors = [
    '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57',
    '#FF9FF3', '#54A0FF', '#5F27CD', '#00D2D3', '#FF9F43',
    '#10AC84', '#EE5A24', '#0652DD', '#9C88FF', '#FFC312'
  ]
  
  // 使用用户名的hash来选择颜色
  let hash = 0
  for (let i = 0; i < username.length; i++) {
    hash = username.charCodeAt(i) + ((hash << 5) - hash)
  }
  
  const colorIndex = Math.abs(hash) % colors.length
  const backgroundColor = colors[colorIndex]
  
  // 获取用户名首字母
  const initial = username.charAt(0).toUpperCase()
  
  return {
    backgroundColor,
    initial,
    hasImage: false
  }
}

// 获取当前用户头像信息
const currentUserAvatar = computed(() => {
  if (authStore.user?.username) {
    return generateUserAvatar(authStore.user.username)
  }
  return {
    backgroundColor: '#E0E0E0',
    initial: 'U',
    hasImage: false
  }
})

// Computed properties for access control
const canAccessUserManagement = computed(() => authStore.isSystemAdmin)
const isLoggedIn = computed(() => authStore.isAuthenticated)

const loadNavStats = async () => {
  try {
    // 只有在用户已认证时才加载导航统计
    if (!authStore.isAuthenticated) {
      return
    }
    
    const [sources, tasks, projects] = await Promise.all([
      api.get('/api/v1/data-sources/'),
      api.get('/api/v1/inspection-tasks/'),
      api.get('/api/v1/projects/')
    ])
    
    navStats.value = {
      dataSources: sources.data?.length || 0,
      tasks: tasks.data?.length || 0,
      projects: projects.data?.length || 0
    }
    
    updateNavBadges()
  } catch {
    console.log('Failed to load navigation stats')
  }
}

const updateNavBadges = () => {
  const dataSourcesBadge = document.getElementById('data-sources-count')
  const tasksBadge = document.getElementById('tasks-count')
  const projectsBadge = document.getElementById('projects-count')
  
  if (dataSourcesBadge) {
    if (navStats.value.dataSources > 0) {
      dataSourcesBadge.textContent = navStats.value.dataSources.toString()
      dataSourcesBadge.classList.add('has-count')
    } else {
      dataSourcesBadge.classList.remove('has-count')
    }
  }
  
  if (tasksBadge) {
    if (navStats.value.tasks > 0) {
      tasksBadge.textContent = navStats.value.tasks.toString()
      tasksBadge.classList.add('has-count')
    } else {
      tasksBadge.classList.remove('has-count')
    }
  }
  
  if (projectsBadge) {
    if (navStats.value.projects > 0) {
      projectsBadge.textContent = navStats.value.projects.toString()
      projectsBadge.classList.add('has-count')
    } else {
      projectsBadge.classList.remove('has-count')
    }
  }
}

// 暴露方法给全局调用
if (typeof window !== 'undefined') {
  ;(window as any).updateNavigationStats = loadNavStats
}

// 点击外部关闭下拉菜单
const handleClickOutside = (event: MouseEvent) => {
  const dropdowns = document.querySelectorAll('.nav-dropdown')
  dropdowns.forEach(dropdown => {
    if (!dropdown.contains(event.target as Node)) {
      if (dropdown.querySelector('.settings-toggle')) {
        showSettingsDropdown.value = false
      }
      if (dropdown.querySelector('.user-toggle')) {
        showUserDropdown.value = false
      }
    }
  })
}

// 用户退出登录
const handleLogout = () => {
  authStore.logout()
  showUserDropdown.value = false
}

// 获取角色标签
const getRoleLabel = (role?: string) => {
  const roleMap: Record<string, string> = {
    'SYSTEM_ADMIN': '系统管理员',
    'PROJECT_ADMIN': '项目管理员',
    'REGULAR_USER': '普通用户'
  }
  return roleMap[role || ''] || '未知角色'
}

onMounted(() => {
  loadNavStats()
  // 定期刷新导航统计
  setInterval(loadNavStats, 30000) // 30秒刷新一次
  
  // 添加点击外部监听
  document.addEventListener('click', handleClickOutside)
})

// 清理监听器
onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<template>
  <div class="app-container">
    <!-- Apple-style Navigation Header -->
    <header class="apple-header">
      <div class="apple-container">
        <div class="header-content">
          <!-- Logo and Brand -->
          <div class="brand-section">
            <RouterLink to="/" class="logo-link">
              <div class="logo-container">
                <el-icon class="logo-icon"><DataAnalysis /></el-icon>
                <div class="logo-text">
                  <span class="logo-name">DQ</span>
                  <span class="logo-subtitle">Database Quality</span>
                </div>
              </div>
            </RouterLink>
          </div>

          <!-- Navigation -->
          <nav class="main-nav">
            <div class="nav-indicator"></div>
            <RouterLink to="/" class="nav-item" data-tooltip="系统概览和统计">
              <el-icon class="nav-icon"><Monitor /></el-icon>
              <span class="nav-text">概览</span>
              <span class="nav-badge" v-if="$route.path === '/'"></span>
            </RouterLink>
            <RouterLink to="/inspection-rules" class="nav-item" data-tooltip="管理巡检规则和执行历史">
              <el-icon class="nav-icon"><Cpu /></el-icon>
              <span class="nav-text">巡检中心</span>
              <span class="nav-badge" id="tasks-count"></span>
            </RouterLink>
            
            <!-- Settings Dropdown -->
            <div class="nav-dropdown" :class="{ active: showSettingsDropdown }">
              <div class="nav-item settings-toggle" @click="showSettingsDropdown = !showSettingsDropdown" data-tooltip="系统设置和管理">
                <el-icon class="nav-icon"><Setting /></el-icon>
                <span class="nav-text">设置</span>
                <el-icon class="dropdown-arrow" :class="{ rotated: showSettingsDropdown }"><ArrowDown /></el-icon>
              </div>
              <div class="dropdown-menu" v-show="showSettingsDropdown">
                <RouterLink to="/data-sources" class="dropdown-item" @click="showSettingsDropdown = false">
                  <el-icon class="dropdown-icon"><Connection /></el-icon>
                  <span class="dropdown-text">数据源管理</span>
                  <span class="dropdown-badge" id="data-sources-count"></span>
                </RouterLink>
                <RouterLink to="/projects" class="dropdown-item" @click="showSettingsDropdown = false">
                  <el-icon class="dropdown-icon"><DataAnalysis /></el-icon>
                  <span class="dropdown-text">项目管理</span>
                  <span class="dropdown-badge" id="projects-count"></span>
                </RouterLink>
                <RouterLink 
                  to="/admin/users" 
                  class="dropdown-item" 
                  @click="showSettingsDropdown = false"
                  v-if="canAccessUserManagement"
                >
                  <el-icon class="dropdown-icon"><User /></el-icon>
                  <span class="dropdown-text">用户管理</span>
                </RouterLink>
              </div>
            </div>

            <!-- User Dropdown -->
            <div class="nav-dropdown" :class="{ active: showUserDropdown }" v-if="isLoggedIn">
              <div class="nav-item user-toggle" @click="showUserDropdown = !showUserDropdown" data-tooltip="用户账户">
                <!-- 用户头像 -->
                <div class="user-avatar" :style="{ backgroundColor: currentUserAvatar.backgroundColor }">
                  {{ currentUserAvatar.initial }}
                </div>
                <span class="nav-text">{{ authStore.user?.username || '用户' }}</span>
                <el-icon class="dropdown-arrow" :class="{ rotated: showUserDropdown }"><ArrowDown /></el-icon>
              </div>
              <div class="dropdown-menu" v-show="showUserDropdown">
                <RouterLink to="/profile" class="dropdown-item user-info" @click="showUserDropdown = false">
                  <!-- 用户头像 -->
                  <div class="user-avatar dropdown-avatar" :style="{ backgroundColor: currentUserAvatar.backgroundColor }">
                    {{ currentUserAvatar.initial }}
                  </div>
                  <div class="user-details">
                    <span class="user-name">{{ authStore.user?.username }}</span>
                    <span class="user-role">{{ getRoleLabel(authStore.user?.role) }}</span>
                  </div>
                </RouterLink>
                <div class="dropdown-divider"></div>
                <div class="dropdown-item" @click="handleLogout">
                  <el-icon class="dropdown-icon"><SwitchButton /></el-icon>
                  <span class="dropdown-text">退出登录</span>
                </div>
              </div>
            </div>
            
            <!-- Login Link -->
            <RouterLink v-else to="/login" class="nav-item" data-tooltip="用户登录">
              <el-icon class="nav-icon"><User /></el-icon>
              <span class="nav-text">登录</span>
            </RouterLink>
          </nav>
        </div>
      </div>
    </header>

    <!-- Main Content Area -->
    <main class="main-content">
      <RouterView />
    </main>
  </div>
</template>

<style scoped>
/* Apple-style App Container */
.app-container {
  min-height: 100vh;
  background: var(--gray-9);
  display: flex;
  flex-direction: column;
}

/* Apple-style Header */
.apple-header {
  position: sticky;
  top: 0;
  z-index: var(--z-sticky);
  background: rgba(255, 255, 255, 0.72);
  backdrop-filter: saturate(180%) blur(20px);
  border-bottom: 1px solid var(--gray-5);
  transition: all var(--transition-normal);
}

.apple-header:hover {
  background: rgba(255, 255, 255, 0.85);
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 48px;
  padding: 0 var(--spacing-md);
}

/* Brand Section */
.brand-section {
  display: flex;
  align-items: center;
}

.logo-link {
  text-decoration: none;
  color: inherit;
  display: flex;
  align-items: center;
  transition: opacity var(--transition-fast);
}

.logo-link:hover {
  opacity: 0.8;
}

.logo-container {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.logo-icon {
  width: 24px;
  height: 24px;
  color: var(--apple-blue);
  flex-shrink: 0;
}

.logo-text {
  display: flex;
  flex-direction: column;
  line-height: 1.2;
}

.logo-name {
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--gray-1);
  letter-spacing: -0.5px;
}

.logo-subtitle {
  font-size: var(--font-size-xs);
  color: var(--gray-3);
  font-weight: 400;
  letter-spacing: 0.1px;
}

/* Navigation */
.main-nav {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  position: relative;
}

.nav-indicator {
  position: absolute;
  height: 2px;
  background: var(--apple-blue);
  border-radius: var(--radius-full);
  bottom: -2px;
  transition: all var(--transition-normal);
  opacity: 0;
}

.nav-indicator.active {
  opacity: 1;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  padding: 8px 16px;
  border-radius: var(--radius-lg);
  text-decoration: none;
  color: var(--gray-2);
  font-size: var(--font-size-sm);
  font-weight: 500;
  transition: all var(--transition-fast);
  position: relative;
  overflow: hidden;
  border: 1px solid transparent;
}

.nav-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, var(--apple-blue), var(--apple-purple));
  opacity: 0;
  transition: opacity var(--transition-fast);
  border-radius: var(--radius-lg);
}

.nav-item::after {
  content: attr(data-tooltip);
  position: absolute;
  bottom: -35px;
  left: 50%;
  transform: translateX(-50%);
  background: var(--gray-1);
  color: var(--gray-8);
  padding: 4px 8px;
  border-radius: var(--radius-sm);
  font-size: var(--font-size-xs);
  white-space: nowrap;
  opacity: 0;
  pointer-events: none;
  transition: all var(--transition-fast);
  z-index: 10;
}

.nav-item:hover {
  color: var(--gray-1);
  border-color: var(--gray-4);
  transform: translateY(-1px);
}

.nav-item:hover::before {
  opacity: 0.1;
}

.nav-item:hover::after {
  opacity: 1;
  bottom: -30px;
}

.nav-item.router-link-exact-active {
  color: var(--apple-blue);
  background: rgba(0, 122, 255, 0.08);
  border-color: rgba(0, 122, 255, 0.2);
}

.nav-item.router-link-exact-active::before {
  opacity: 0.15;
}

.nav-icon {
  width: 18px;
  height: 18px;
  position: relative;
  z-index: 1;
  transition: transform var(--transition-fast);
}

.nav-item:hover .nav-icon {
  transform: scale(1.1);
}

.nav-text {
  position: relative;
  z-index: 1;
  font-weight: 600;
}

.nav-badge {
  position: absolute;
  top: 4px;
  right: 4px;
  min-width: 18px;
  height: 18px;
  background: var(--apple-red);
  color: white;
  border-radius: var(--radius-full);
  font-size: var(--font-size-xs);
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 4px;
  opacity: 0;
  transform: scale(0);
  transition: all var(--transition-fast);
  z-index: 2;
}

.nav-badge.has-count {
  opacity: 1;
  transform: scale(1);
}

/* Main Content */
.main-content {
  flex: 1;
  background: var(--gray-8);
  min-height: calc(100vh - 48px);
}

/* Responsive Design */
@media (max-width: 768px) {
  .header-content {
    height: 44px;
    padding: 0 var(--spacing-sm);
  }
  
  .logo-subtitle {
    display: none;
  }
  
  .nav-text {
    display: none;
  }
  
  .nav-item {
    padding: 8px;
    border-radius: var(--radius-full);
  }
  
  .nav-icon {
    width: 18px;
    height: 18px;
  }
}

@media (max-width: 480px) {
  .header-content {
    height: 40px;
  }
  
  .logo-name {
    font-size: var(--font-size-base);
  }
  
  .nav-item {
    padding: 6px;
  }
  
  .nav-icon {
    width: 16px;
    height: 16px;
  }
}

/* Smooth scrolling */
html {
  scroll-behavior: smooth;
}

/* Animation for page transitions */
.main-content {
  animation: apple-fade-in 0.3s ease-out;
}

/* Dropdown Menu Styles */
.nav-dropdown {
  position: relative;
}

.settings-toggle {
  cursor: pointer;
  user-select: none;
}

.dropdown-arrow {
  width: 14px;
  height: 14px;
  margin-left: var(--spacing-xs);
  transition: transform var(--transition-fast);
  color: var(--gray-4);
}

.dropdown-arrow.rotated {
  transform: rotate(180deg);
}

.dropdown-menu {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(20px);
  border: 1px solid var(--gray-5);
  border-radius: var(--radius-lg);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
  min-width: 200px;
  z-index: 1000;
  opacity: 0;
  transform: translateY(-8px);
  transition: all var(--transition-normal);
  pointer-events: none;
}

.nav-dropdown.active .dropdown-menu {
  opacity: 1;
  transform: translateY(0);
  pointer-events: auto;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-md) var(--spacing-lg);
  text-decoration: none;
  color: var(--gray-2);
  font-size: var(--font-size-sm);
  font-weight: 500;
  transition: all var(--transition-fast);
  position: relative;
  border-radius: var(--radius-md);
  margin: var(--spacing-xs);
}

.dropdown-item:hover {
  background: rgba(0, 122, 255, 0.08);
  color: var(--apple-blue);
  transform: translateX(2px);
}

.dropdown-item.router-link-exact-active {
  background: rgba(0, 122, 255, 0.12);
  color: var(--apple-blue);
  font-weight: 600;
}

.dropdown-icon {
  width: 16px;
  height: 16px;
  flex-shrink: 0;
}

.dropdown-text {
  flex: 1;
}

.dropdown-badge {
  min-width: 18px;
  height: 18px;
  background: var(--apple-red);
  color: white;
  border-radius: var(--radius-full);
  font-size: var(--font-size-xs);
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 4px;
  opacity: 0;
  transform: scale(0);
  transition: all var(--transition-fast);
}

.dropdown-badge.has-count {
  opacity: 1;
  transform: scale(1);
}

/* User Info Styles */
.user-info {
  background: transparent !important;
  cursor: pointer !important;
  text-decoration: none !important;
  color: inherit !important;
}

.user-info:hover {
  background: var(--gray-6) !important;
}

.user-details {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.user-name {
  font-weight: 600;
  color: var(--gray-1);
}

.user-role {
  font-size: var(--font-size-xs);
  color: var(--gray-4);
  font-weight: 400;
}

.dropdown-divider {
  height: 1px;
  background: var(--gray-5);
  margin: var(--spacing-sm) var(--spacing-md);
}

/* User Avatar Styles */
.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  font-size: 14px;
  text-transform: uppercase;
  flex-shrink: 0;
  transition: all var(--transition-fast);
  border: 2px solid transparent;
}

.user-avatar:hover {
  transform: scale(1.05);
  border-color: var(--gray-3);
}

.user-toggle .user-avatar {
  margin-right: var(--spacing-sm);
}

.dropdown-avatar {
  width: 40px;
  height: 40px;
  font-size: 16px;
  margin-right: var(--spacing-md);
}

/* Update user-toggle to accommodate avatar */
.user-toggle {
  display: flex;
  align-items: center;
  padding: var(--spacing-sm) var(--spacing-md) !important;
}

.user-toggle .nav-text {
  margin-right: var(--spacing-xs);
}

/* Close dropdown when clicking outside */
@media (max-width: 768px) {
  .dropdown-menu {
    right: -8px;
    min-width: 180px;
  }
  
  .dropdown-item {
    padding: var(--spacing-sm) var(--spacing-md);
  }
  
  .dropdown-text {
    font-size: var(--font-size-xs);
  }
  
  .user-avatar {
    width: 28px;
    height: 28px;
    font-size: 12px;
  }
  
  .dropdown-avatar {
    width: 32px;
    height: 32px;
    font-size: 14px;
  }
}
</style>
