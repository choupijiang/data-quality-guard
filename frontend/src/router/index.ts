import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
      meta: { requiresAuth: true }
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue'),
      meta: { guest: true }
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('../views/RegisterView.vue'),
      meta: { guest: true }
    },
    {
      path: '/admin/users',
      name: 'admin-users',
      component: () => import('../views/UsersView.vue'),
      meta: { requiresAuth: true, requiresSystemAdmin: true }
    },
    {
      path: '/data-sources',
      name: 'data-sources',
      component: () => import('../views/DataSourcesView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/data-sources/create',
      name: 'data-source-create',
      component: () => import('../views/DataSourceCreateView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/inspection-rules',
      name: 'inspection-rules',
      component: () => import('../views/InspectionRulesView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/inspection-rules/create',
      name: 'inspection-rule-create',
      component: () => import('../views/InspectionRuleCreateView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/inspection-rules/:id/edit',
      name: 'inspection-rule-edit',
      component: () => import('../views/InspectionRuleEditView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/inspection-tasks',
      name: 'inspection-tasks',
      component: () => import('../views/InspectionTasksView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/projects',
      name: 'projects',
      component: () => import('../views/ProjectsView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/projects/create',
      name: 'project-create',
      component: () => import('../views/ProjectCreateView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/projects/:id/edit',
      name: 'project-edit',
      component: () => import('../views/ProjectEditView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/about',
      name: 'about',
      component: () => import('../views/AboutView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/profile',
      name: 'profile',
      component: () => import('../views/ProfileView.vue'),
      meta: { requiresAuth: true }
    },
  ],
})

// Navigation guard
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  // Initialize auth store
  await authStore.initializeAuth()
  
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  const requiresSystemAdmin = to.matched.some(record => record.meta.requiresSystemAdmin)
  const guestOnly = to.matched.some(record => record.meta.guest)
  
  if (requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else if (guestOnly && authStore.isAuthenticated) {
    next('/')
  } else if (requiresSystemAdmin && !authStore.isSystemAdmin) {
    next('/')
  } else {
    next()
  }
})

export default router
