import myAxios from '@/request'

export function postChat(data: { conversationId?: string; message: string }) {
  return myAxios.post('/chat', data)
}