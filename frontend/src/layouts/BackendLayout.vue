<template>
  <a-layout class="admin-layout">
    <a-layout-header class="header">
      <div class="header-content">
        <div class="logo">
          <span class="logo-text">CloudDesk</span>
        </div>
        <div class="header-right">
          <a-space :size="16">
            <a-tag color="blue">{{ userStore.userRole || 'user' }}</a-tag>
            <span class="user-name">{{ userStore.username }}</span>
            <a-button type="link" size="small" @click="handleLogout">退出</a-button>
          </a-space>
        </div>
      </div>
    </a-layout-header>

    <a-layout>
      <a-layout-sider
        v-model:collapsed="collapsed"
        :trigger="null"
        collapsible
        :width="200"
        class="sider"
      >
        <div class="sider-header" @click="collapsed = !collapsed">
          <MenuUnfoldOutlined v-if="collapsed" />
          <MenuFoldOutlined v-else />
        </div>
        <a-menu
          v-model:selectedKeys="selectedKeys"
          v-model:openKeys="openKeys"
          mode="inline"
          theme="light"
          class="menu"
          @click="handleMenuClick"
        >
          <a-menu-item v-for="item in menuItems" :key="item.key">
            <component :is="item.icon" v-if="item.icon" />
            <span>{{ item.title }}</span>
          </a-menu-item>
        </a-menu>
      </a-layout-sider>

      <a-layout
        class="content-layout"
        :class="[
          collapsed ? 'content-layout-collapsed' : 'content-layout-expanded',
          isChatRoute ? 'content-layout-chat' : ''
        ]"
      >
        <a-layout-content class="content" :class="{ 'content-chat': isChatRoute }">
          <router-view />
        </a-layout-content>
      </a-layout>
    </a-layout>
  </a-layout>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { MenuFoldOutlined, MenuUnfoldOutlined } from '@ant-design/icons-vue'
import {
  CustomerServiceOutlined,
  UnorderedListOutlined,
  CheckCircleOutlined,
  BookOutlined,
  CloudServerOutlined,
  DashboardOutlined,
  FileSearchOutlined,
} from '@ant-design/icons-vue'
import type { Component } from 'vue'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const isChatRoute = computed(() => route.name === 'Chat')

const collapsed = ref(false)
const selectedKeys = ref<string[]>(['Chat'])
const openKeys = ref<string[]>([])

interface MenuItem {
  key: string
  title: string
  icon?: Component
}

const cloudDeskMenuItems: MenuItem[] = [
  { key: 'Chat', title: '智能客服', icon: CustomerServiceOutlined },
  { key: 'Tickets', title: '工单管理', icon: UnorderedListOutlined },
  { key: 'Approvals', title: '审批中心', icon: CheckCircleOutlined },
  { key: 'Knowledge', title: '知识库', icon: BookOutlined },
  { key: 'AgentOps', title: 'Agent 运维', icon: CloudServerOutlined },
  { key: 'EvalDashboard', title: '评估中心', icon: FileSearchOutlined },
  { key: 'Dashboard', title: '数据总览', icon: DashboardOutlined },
]

const adminMenuItems: MenuItem[] = [
  { key: 'AdminDashboard', title: '数据总览', icon: DashboardOutlined },
]

const menuItems = computed((): MenuItem[] => {
  const currentPath = route.path
  const isAdmin = currentPath.startsWith('/admin')
  return isAdmin ? adminMenuItems : cloudDeskMenuItems
})

watch(
  () => route.name,
  (name) => {
    if (name) {
      selectedKeys.value = [name as string]
    }
  },
  { immediate: true }
)

const handleMenuClick = ({ key }: { key: string }) => {
  router.push({ name: key })
}

const handleLogout = async () => {
  await userStore.logout()
  router.push('/user/login')
}
</script>

<style scoped>
.admin-layout {
  min-height: 100vh;
}

.header {
  background: #fff;
  padding: 0;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  position: sticky;
  top: 0;
  z-index: 1001;
  height: 64px;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100%;
  padding: 0 24px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 18px;
  font-weight: 600;
  color: #1f5fae;
}

.logo-text {
  color: #1f5fae;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-name {
  color: rgba(0, 0, 0, 0.65);
  font-size: 14px;
}

.sider {
  background: #fff;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.05);
  height: calc(100vh - 64px);
  position: fixed;
  left: 0;
  top: 64px;
  overflow-y: auto;
  z-index: 100;
}

.sider-header {
  text-align: right;
  padding: 12px 16px;
  cursor: pointer;
  color: rgba(0, 0, 0, 0.45);
  font-size: 16px;
}

.sider-header:hover {
  color: #1f5fae;
}

.menu {
  border-right: none;
  padding-top: 0;
}

.content-layout {
  background: #f0f2f5;
  transition: all 0.2s;
}

.content-layout-collapsed {
  margin-left: 80px;
}

.content-layout-expanded {
  margin-left: 200px;
}

.content-layout-chat {
  overflow: hidden;
}

.content {
  margin: 24px;
  padding: 24px;
  background: #fff;
  border-radius: 8px;
  min-height: calc(100vh - 112px);
}

.content-chat {
  margin: 0;
  padding: 0;
  background: transparent;
  border-radius: 0;
  height: calc(100vh - 64px);
  overflow: hidden;
}
</style>
