import myAxios from '@/request'

export function getOrder(id: string) {
  return myAxios.get(`/orders/${id}`)
}