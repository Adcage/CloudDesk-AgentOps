<template>
  <div class="knowledge-view">
    <a-page-header title="知识库" sub-title="管理 RAG 文档与检索测试" />

    <a-row :gutter="[16, 16]">
      <a-col :xs="24" :lg="16">
        <a-card title="文档列表" :bordered="false">
          <template #extra>
            <a-upload
              :before-upload="handleBeforeUpload"
              :show-upload-list="false"
              accept=".md"
            >
              <a-button type="primary">
                <upload-outlined />
                上传文档
              </a-button>
            </a-upload>
          </template>
          <a-table
            :columns="docColumns"
            :data-source="documents"
            :loading="docsLoading"
            :pagination="false"
            row-key="documentId"
            size="small"
          >
            <template #bodyCell="{ column, record }">
              <template v-if="column.dataIndex === 'createdAt'">
                {{ formatDate(record.createdAt) }}
              </template>
            </template>
          </a-table>
        </a-card>
      </a-col>

      <a-col :xs="24" :lg="8">
        <a-card title="检索测试" :bordered="false">
          <a-space direction="vertical" style="width: 100%" :size="12">
            <a-input-search
              v-model:value="searchQuery"
              placeholder="输入查询内容测试 RAG 检索"
              enter-button="搜索"
              :loading="searchLoading"
              @search="handleSearch"
            />
            <div v-if="searchResults.length > 0" class="search-results">
              <a-card
                v-for="(result, idx) in searchResults"
                :key="idx"
                size="small"
                :bordered="true"
                style="margin-bottom: 12px"
              >
                <template #title>
                  <span class="result-source">{{ result.source || result.documentId || `结果 ${idx + 1}` }}</span>
                </template>
                <div class="result-text">{{ result.text || result.chunkText }}</div>
                <div v-if="result.score != null" class="result-score">
                  相似度: {{ (result.score * 100).toFixed(1) }}%
                </div>
              </a-card>
            </div>
            <a-empty v-else-if="searchQuery && !searchLoading" description="未找到相关文档" />
          </a-space>
        </a-card>
      </a-col>
    </a-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { message as antMessage } from 'ant-design-vue'
import { UploadOutlined } from '@ant-design/icons-vue'
import { getDocuments, ingestDocument, searchDocuments } from '@/api/knowledge'

const docColumns = [
  { title: '文档ID', dataIndex: 'documentId', width: 140 },
  { title: '标题', dataIndex: 'title', ellipsis: true },
  { title: '类型', dataIndex: 'docType', width: 100 },
  { title: '版本', dataIndex: 'version', width: 80 },
  { title: '创建时间', dataIndex: 'createdAt', width: 180 },
]

const documents = ref<any[]>([])
const docsLoading = ref(false)
const searchQuery = ref('')
const searchLoading = ref(false)
const searchResults = ref<any[]>([])

const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

const loadDocuments = async () => {
  docsLoading.value = true
  try {
    const res = await getDocuments()
    const data = res.data?.data ?? res.data
    const rawList = Array.isArray(data) ? data : data?.records ?? data?.list ?? []
    documents.value = rawList.map(normalizeDoc)
  } catch (err: any) {
    console.error('加载文档列表失败', err)
    antMessage.error('加载文档列表失败，请刷新重试')
  } finally {
    docsLoading.value = false
  }
}

const normalizeDoc = (d: any) => ({
  documentId: d.documentId ?? d.document_id ?? '',
  title: d.title ?? '',
  docType: d.docType ?? d.doc_type ?? '',
  version: d.version ?? '',
  createdAt: d.createdAt ?? d.created_at ?? '',
})

const handleBeforeUpload = async (file: File) => {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('title', file.name.replace(/\.md$/i, ''))
  formData.append('doc_type', 'policy')

  try {
    await ingestDocument(formData)
    antMessage.success('文档上传成功')
    loadDocuments()
  } catch (err: any) {
    antMessage.error('文档上传失败: ' + (err.message || '未知错误'))
  }
  return false
}

const handleSearch = async () => {
  if (!searchQuery.value.trim()) return
  searchLoading.value = true
  try {
    const res = await searchDocuments({ query: searchQuery.value, top_k: 5 })
    const data = res.data?.data ?? res.data
    searchResults.value = Array.isArray(data) ? data : data?.chunks ?? data?.results ?? []
  } catch (err: any) {
    console.error('检索失败', err)
    searchResults.value = []
  } finally {
    searchLoading.value = false
  }
}

onMounted(() => {
  loadDocuments()
})
</script>

<style scoped>
.knowledge-view {
  min-height: 100%;
}

.search-results {
  max-height: 500px;
  overflow-y: auto;
}

.result-source {
  font-weight: 600;
  color: #1f5fae;
}

.result-text {
  font-size: 13px;
  color: rgba(0, 0, 0, 0.65);
  line-height: 1.6;
}

.result-score {
  margin-top: 8px;
  font-size: 12px;
  color: rgba(0, 0, 0, 0.45);
}
</style>