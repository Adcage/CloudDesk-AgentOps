import myAxios from '@/request'

export function getCustomer(id: string) {
  return myAxios.get(`/customers/${id}`)
}