<template>
  <div class="utils-demo">
    <a-card title="工具类使用示例" :bordered="false">
      <a-tabs v-model:activeKey="activeTab">
        <!-- Excel 导入导出 -->
        <a-tab-pane key="excel" tab="Excel 导入导出">
          <a-space direction="vertical" :size="16" style="width: 100%">
            <!-- 导出示例 -->
            <a-card title="导出 Excel" size="small">
              <a-space>
                <a-button type="primary" @click="handleExportExcel">
                  <template #icon><component :is="DownloadOutlined" /></template>
                  导出用户列表
                </a-button>
                <a-button @click="handleExportMultiSheet">
                  导出多工作表
                </a-button>
                <a-button @click="handleExportCSV">
                  导出 CSV
                </a-button>
              </a-space>
            </a-card>

            <!-- 导入示例 -->
            <a-card title="导入 Excel" size="small">
              <a-space direction="vertical" style="width: 100%">
                <a-upload
                  :before-upload="handleBeforeUpload"
                  :show-upload-list="false"
                  accept=".xlsx,.xls,.csv"
                >
                  <a-button>
                    <template #icon><component :is="UploadOutlined" /></template>
                    选择文件导入
                  </a-button>
                </a-upload>
                <a-button type="link" @click="handleDownloadTemplate">
                  下载导入模板
                </a-button>
                <a-alert
                  v-if="importResult"
                  :message="importResult.message"
                  :type="importResult.success ? 'success' : 'error'"
                  closable
                  @close="importResult = null"
                />
              </a-space>
            </a-card>

            <!-- 导入的数据预览 -->
            <a-card v-if="importedData.length > 0" title="导入数据预览" size="small">
              <a-table
                :columns="importColumns"
                :data-source="importedData"
                :pagination="{ pageSize: 5 }"
                size="small"
              />
            </a-card>
          </a-space>
        </a-tab-pane>

        <!-- PDF 生成 -->
        <a-tab-pane key="pdf" tab="PDF 生成">
          <a-space direction="vertical" :size="16" style="width: 100%">
            <!-- PDF 导出示例 -->
            <a-card title="导出 PDF" size="small">
              <a-space>
                <a-button type="primary" @click="handleExportPDF">
                  <template #icon><component :is="FilePdfOutlined" /></template>
                  导出当前页面
                </a-button>
                <a-button @click="handleExportTablePDF">
                  导出表格 PDF
                </a-button>
                <a-button @click="handlePrint">
                  <template #icon><component :is="PrinterOutlined" /></template>
                  打印
                </a-button>
              </a-space>
            </a-card>

            <!-- PDF 预览内容 -->
            <a-card id="pdf-content" title="PDF 预览内容" size="small">
              <div style="padding: 20px">
                <h2>这是一个示例报表</h2>
                <p>生成时间：{{ currentTime }}</p>
                <a-table
                  :columns="sampleColumns"
                  :data-source="sampleData"
                  :pagination="false"
                  size="small"
                />
              </div>
            </a-card>
          </a-space>
        </a-tab-pane>

        <!-- 通用工具 -->
        <a-tab-pane key="common" tab="通用工具">
          <a-space direction="vertical" :size="16" style="width: 100%">
            <!-- 日期格式化 -->
            <a-card title="日期格式化" size="small">
              <p>当前时间：{{ formattedDate }}</p>
              <p>自定义格式：{{ customFormattedDate }}</p>
            </a-card>

            <!-- 数字格式化 -->
            <a-card title="数字格式化" size="small">
              <p>千分位：{{ formattedNumber }}</p>
              <p>金额：{{ formattedCurrency }}</p>
              <p>文件大小：{{ formattedFileSize }}</p>
            </a-card>

            <!-- 数据脱敏 -->
            <a-card title="数据脱敏" size="small">
              <p>手机号：{{ maskedPhone }}</p>
              <p>身份证：{{ maskedIdCard }}</p>
              <p>邮箱：{{ maskedEmail }}</p>
            </a-card>

            <!-- 复制功能 -->
            <a-card title="复制到剪贴板" size="small">
              <a-space>
                <a-input v-model:value="copyText" placeholder="输入要复制的内容" />
                <a-button @click="handleCopy">
                  <template #icon><component :is="CopyOutlined" /></template>
                  复制
                </a-button>
              </a-space>
            </a-card>
          </a-space>
        </a-tab-pane>
      </a-tabs>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { message } from 'ant-design-vue';
import type { UploadProps } from 'ant-design-vue';
import {
  DownloadOutlined,
  UploadOutlined,
  FilePdfOutlined,
  PrinterOutlined,
  CopyOutlined
} from '@ant-design/icons-vue';
import { ExcelUtil, PDFUtil, CommonUtil } from '@/utils';

interface ImportResult {
  success: boolean
  message: string
}

interface SampleData {
  id: number
  name: string
  age: number
  city: string
  salary: number
}

const activeTab = ref<string>('excel');
const importResult = ref<ImportResult | null>(null);
const importedData = ref<SampleData[]>([]);
const copyText = ref<string>('Hello World!');

const sampleData: SampleData[] = [
  { id: 1, name: '张三', age: 25, city: '北京', salary: 8000 },
  { id: 2, name: '李四', age: 30, city: '上海', salary: 12000 },
  { id: 3, name: '王五', age: 28, city: '广州', salary: 10000 },
  { id: 4, name: '赵六', age: 32, city: '深圳', salary: 15000 },
  { id: 5, name: '钱七', age: 27, city: '杭州', salary: 9000 }
];

const sampleColumns = [
  { title: 'ID', dataIndex: 'id', key: 'id' },
  { title: '姓名', dataIndex: 'name', key: 'name' },
  { title: '年龄', dataIndex: 'age', key: 'age' },
  { title: '城市', dataIndex: 'city', key: 'city' },
  { title: '薪资', dataIndex: 'salary', key: 'salary' }
];

const importColumns = [
  { title: '姓名', dataIndex: 'name', key: 'name' },
  { title: '年龄', dataIndex: 'age', key: 'age' },
  { title: '城市', dataIndex: 'city', key: 'city' }
];

const currentTime = computed(() => CommonUtil.formatDate(new Date()));
const formattedDate = computed(() => CommonUtil.formatDate(new Date(), 'YYYY-MM-DD HH:mm:ss'));
const customFormattedDate = computed(() => CommonUtil.formatDate(new Date(), 'YYYY年MM月DD日'));
const formattedNumber = computed(() => CommonUtil.formatNumber(1234567.89));
const formattedCurrency = computed(() => CommonUtil.formatCurrency(1234567.89));
const formattedFileSize = computed(() => CommonUtil.formatFileSize(1234567890));
const maskedPhone = computed(() => CommonUtil.maskPhone('13812345678'));
const maskedIdCard = computed(() => CommonUtil.maskIdCard('110101199001011234'));
const maskedEmail = computed(() => CommonUtil.maskEmail('example@email.com'));

const handleExportExcel = (): void => {
  const result = ExcelUtil.exportExcel(sampleData as unknown as Record<string, unknown>[], '用户列表', {
    header: ['ID', '姓名', '年龄', '城市', '薪资'],
    autoWidth: true
  });

  if (result.success) {
    message.success('导出成功');
  } else {
    message.error('导出失败');
  }
};

const handleExportMultiSheet = (): void => {
  const sheets = [
    { name: '用户列表', data: sampleData as unknown as Record<string, unknown>[] },
    { name: '统计数据', data: [
      { type: '总人数', value: sampleData.length },
      { type: '平均年龄', value: 28.4 },
      { type: '平均薪资', value: 10800 }
    ]}
  ];

  const result = ExcelUtil.exportMultiSheet(sheets as never, '综合报表');

  if (result.success) {
    message.success('导出成功');
  } else {
    message.error('导出失败');
  }
};

const handleExportCSV = (): void => {
  const result = ExcelUtil.exportCSV(sampleData as unknown as Record<string, unknown>[], '用户列表', {
    header: ['ID', '姓名', '年龄', '城市', '薪资']
  });

  if (result.success) {
    message.success('导出成功');
  } else {
    message.error('导出失败');
  }
};

const handleBeforeUpload: UploadProps['beforeUpload'] = async (file) => {
  const validation = ExcelUtil.validateFile(file);
  if (!validation.valid) {
    message.error(validation.message);
    return false;
  }

  try {
    const result = await ExcelUtil.importExcel(file, {
      header: true,
      transform: (data) => {
        return data.map(item => ({
          name: (item['姓名'] || item['name']) as string,
          age: parseInt(String(item['年龄'] || item['age'])),
          city: (item['城市'] || item['city']) as string
        }));
      }
    });

    if (result.success) {
      importedData.value = result.data as unknown as SampleData[];
      importResult.value = {
        success: true,
        message: `成功导入 ${result.data.length} 条数据`
      };
      message.success('导入成功');
    }
  } catch (error) {
    importResult.value = {
      success: false,
      message: (error as Error).message || '导入失败'
    };
    message.error('导入失败');
  }

  return false;
};

const handleDownloadTemplate = (): void => {
  const result = ExcelUtil.downloadTemplate(
    ['姓名', '年龄', '城市'],
    '用户导入模板',
    [['张三', 25, '北京'], ['李四', 30, '上海']]
  );

  if (result.success) {
    message.success('模板下载成功');
  }
};

const handleExportPDF = async (): Promise<void> => {
  message.loading('正在生成 PDF...', 0);
  
  const result = await PDFUtil.exportFromHTML('#pdf-content', '示例报表', {
    orientation: 'portrait',
    quality: 0.95
  });

  message.destroy();

  if (result.success) {
    message.success('PDF 生成成功');
  } else {
    message.error('PDF 生成失败');
  }
};

const handleExportTablePDF = (): void => {
  const result = PDFUtil.exportTable(sampleData as unknown as Record<string, unknown>[], {
    title: '用户列表报表',
    columns: [
      { header: 'ID', dataKey: 'id' },
      { header: '姓名', dataKey: 'name' },
      { header: '年龄', dataKey: 'age' },
      { header: '城市', dataKey: 'city' },
      { header: '薪资', dataKey: 'salary' }
    ],
    fileName: '用户列表'
  });

  if (result.success) {
    message.success('PDF 生成成功');
  } else {
    message.error('PDF 生成失败');
  }
};

const handlePrint = (): void => {
  const result = PDFUtil.print('#pdf-content', {
    title: '示例报表'
  });

  if (result.success) {
    message.success('打印成功');
  }
};

const handleCopy = async (): Promise<void> => {
  const result = await CommonUtil.copyToClipboard(copyText.value);
  
  if (result.success) {
    message.success('复制成功');
  } else {
    message.error('复制失败');
  }
};
</script>

<style scoped>
.utils-demo {
  padding: 24px;
}
</style>

