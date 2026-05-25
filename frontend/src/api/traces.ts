import myAxios from '@/request'

export function getTraceDetail(id: string) {
  return myAxios.get(`/traces/${id}`)
}

export function getTraces(params?: object) {
  return myAxios.get('/traces', { params })
}