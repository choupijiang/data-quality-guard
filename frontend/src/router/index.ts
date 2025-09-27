import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/data-sources',
      name: 'data-sources',
      component: () => import('../views/DataSourcesView.vue'),
    },
    {
      path: '/data-sources/create',
      name: 'data-source-create',
      component: () => import('../views/DataSourceCreateView.vue'),
    },
    {
      path: '/inspection-rules',
      name: 'inspection-rules',
      component: () => import('../views/InspectionRulesView.vue'),
    },
    {
      path: '/inspection-rules/create',
      name: 'inspection-rule-create',
      component: () => import('../views/InspectionRuleCreateView.vue'),
    },
    {
      path: '/inspection-rules/:id/edit',
      name: 'inspection-rule-edit',
      component: () => import('../views/InspectionRuleEditView.vue'),
    },
    {
      path: '/inspection-tasks',
      name: 'inspection-tasks',
      component: () => import('../views/InspectionTasksView.vue'),
    },
    {
      path: '/projects',
      name: 'projects',
      component: () => import('../views/ProjectsView.vue'),
    },
    {
      path: '/projects/create',
      name: 'project-create',
      component: () => import('../views/ProjectCreateView.vue'),
    },
    {
      path: '/projects/:id/edit',
      name: 'project-edit',
      component: () => import('../views/ProjectEditView.vue'),
    },
    {
      path: '/about',
      name: 'about',
      component: () => import('../views/AboutView.vue'),
    },
  ],
})

export default router
