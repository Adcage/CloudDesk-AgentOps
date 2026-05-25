import type { RouteRecordRaw } from 'vue-router'
import type { Component } from 'vue'
import BackendLayout from '@/layouts/BackendLayout.vue'

import { DashboardOutlined } from '@ant-design/icons-vue'

/** 菜单分组描述，挂在同组路由的 meta.group 上 */
export interface MenuGroup {
  key: string
  title: string
  icon: Component
}

declare module 'vue-router' {
  interface RouteMeta {
    title?: string
    /** 顶级菜单图标（无分组时使用） */
    icon?: Component
    /** 所属分组，有此字段则归入 sub-menu */
    group?: MenuGroup
  }
}

const adminRoutes: RouteRecordRaw = {
  path: '/admin',
  component: BackendLayout,
  redirect: '/admin/dashboard',
  meta: { title: '管理后台' },
  children: [
    {
      path: 'dashboard',
      name: 'AdminDashboard',
      component: () => import('@/views/DashboardView.vue'),
      meta: { title: '数据总览', icon: DashboardOutlined },
    }
  ],
}

export default adminRoutes
