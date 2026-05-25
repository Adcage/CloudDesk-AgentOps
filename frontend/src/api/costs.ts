import myAxios from '@/request'

export interface CostByAgent {
  agent_name: string
  total_cost: number
}

export interface CostByModel {
  model_name: string
  total_cost: number
  call_count: number
  total_input_tokens: number
  total_output_tokens: number
}

export interface CostSummary {
  total_cost: number
  by_agent: CostByAgent[]
  by_model: CostByModel[]
  days: number
}

export interface DailyTrend {
  date: string
  daily_cost: number
}

export interface CostHistory {
  daily_trend: DailyTrend[]
  days: number
}

export function getCostsToday() {
  return myAxios.get<any, { data: CostSummary }>('/agent/costs/today')
}

export function getCostsByAgent(days: number = 7) {
  return myAxios.get<any, { data: { by_agent: CostByAgent[]; days: number } }>(
    '/agent/costs/by-agent',
    { params: { days } },
  )
}

export function getCostsHistory(days: number = 30) {
  return myAxios.get<any, { data: CostHistory }>('/agent/costs/history', {
    params: { days },
  })
}
