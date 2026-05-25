import myAxios from '@/request'
import { getStoredUserId } from '@/stores/user'

export function getApprovals(params?: object) {
  return myAxios.get('/approvals', { params })
}

export function approveApproval(id: string) {
  return myAxios.post(`/approvals/${id}/approve`, { reviewedBy: getStoredUserId() })
}

export function rejectApproval(id: string, data?: { reason: string }) {
  return myAxios.post(`/approvals/${id}/reject`, { ...data, reviewedBy: getStoredUserId() })
}