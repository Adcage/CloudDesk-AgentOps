import myAxios from '@/request'

export function getTickets(params?: object) {
  return myAxios.get('/tickets', { params })
}

export function getTicketDetail(id: string) {
  return myAxios.get(`/tickets/${id}`)
}

export function getMyTodoTickets(userId: string) {
  return myAxios.get('/tickets/my-todos', { params: { userId } })
}

export function batchAssignTickets(data: { ticketIds: string[]; assignedTo: string }) {
  return myAxios.post('/tickets/batch/assign', data)
}

export function batchCloseTickets(data: { ticketIds: string[]; closureReason: string }) {
  return myAxios.post('/tickets/batch/close', data)
}