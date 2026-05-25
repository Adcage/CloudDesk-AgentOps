import type { RouteRecordRaw } from 'vue-router'
import BackendLayout from '@/layouts/BackendLayout.vue'
import {
  CustomerServiceOutlined,
  UnorderedListOutlined,
  CheckCircleOutlined,
  BookOutlined,
  CloudServerOutlined,
  DashboardOutlined,
  FileSearchOutlined,
  DollarOutlined,
} from '@ant-design/icons-vue'

const clouddeskRoutes: RouteRecordRaw = {
  path: '/',
  component: BackendLayout,
  redirect: '/chat',
  children: [
    {
      path: 'chat',
      name: 'Chat',
      component: () => import('@/views/chat/ChatView.vue'),
      meta: { title: '智能客服', icon: CustomerServiceOutlined },
    },
    {
      path: 'tickets',
      name: 'Tickets',
      component: () => import('@/views/tickets/TicketsView.vue'),
      meta: { title: '工单管理', icon: UnorderedListOutlined },
    },
    {
      path: 'approvals',
      name: 'Approvals',
      component: () => import('@/views/approvals/ApprovalsView.vue'),
      meta: { title: '审批中心', icon: CheckCircleOutlined },
    },
    {
      path: 'knowledge',
      name: 'Knowledge',
      component: () => import('@/views/knowledge/KnowledgeView.vue'),
      meta: { title: '知识库', icon: BookOutlined },
    },
    {
      path: 'agentops',
      name: 'AgentOps',
      component: () => import('@/views/agentops/AgentOpsView.vue'),
      meta: { title: 'Agent 运维', icon: CloudServerOutlined },
    },
    {
      path: 'agentops/eval',
      name: 'EvalDashboard',
      component: () => import('@/views/agentops/EvalView.vue'),
      meta: { title: '评估中心', icon: FileSearchOutlined },
    },
    {
      path: 'agentops/costs',
      name: 'CostAnalysis',
      component: () => import('@/views/agentops/CostView.vue'),
      meta: { title: '成本分析', icon: DollarOutlined },
    },
    {
      path: 'dashboard',
      name: 'Dashboard',
      component: () => import('@/views/DashboardView.vue'),
      meta: { title: '数据总览', icon: DashboardOutlined },
    },
  ],
}

export default clouddeskRoutes
