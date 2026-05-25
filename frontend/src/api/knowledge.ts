import myAxios from '@/request'

export function getDocuments() {
  return myAxios.get('/agent/documents')
}

export function ingestDocument(data: FormData) {
  return myAxios.post('/agent/documents/ingest', data)
}

export function searchDocuments(params: { query: string; top_k?: number }) {
  return myAxios.get('/agent/documents/search', { params })
}