import myAxios from '@/request'

export function getEvalSummary() {
  return myAxios.get('/evals/summary')
}

export function getEvalResults(page = 1, pageSize = 10) {
  return myAxios.get('/evals/results', {
    params: {
      page,
      page_size: pageSize,
    },
  })
}

export function runEval(caseIds?: string[]) {
  return myAxios.post('/evals/run', caseIds?.length ? { case_ids: caseIds } : {})
}

export function getEvalByVersion() {
  return myAxios.get('/evals/results/by-version')
}
