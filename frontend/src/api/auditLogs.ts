import myAxios from '@/request'

export function getAuditLogs(params?: object) {
  return myAxios.get('/audit-logs', { params })
}