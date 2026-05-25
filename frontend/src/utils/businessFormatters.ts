export const STATUS_MAP: Record<number, { label: string; color: string }> = {
  0: { label: '待处理', color: 'gold' },
  1: { label: '进行中', color: 'blue' },
  2: { label: '已完成', color: 'green' },
  3: { label: '已取消', color: 'red' },
  4: { label: '异常', color: 'error' },
}

export const getStatusMeta = (status?: number) => STATUS_MAP[status ?? -1] ?? { label: '未知状态', color: 'default' }
