import api from './client'

export interface CompareRequest {
  prompt: string
  system_prompt?: string
  model_ids?: string[] | null
  free_only?: boolean
}

export interface EvalBreakdown {
  length: number
  first_person: number
  digits: number
  structure: number
  no_opener: number
  readability: number
  ai_isms_penalty: number
}

export interface ModelResult {
  model_id: string
  display_name: string
  provider: string
  is_free: boolean
  text: string
  elapsed_sec: number
  error: string
  score: number | null
  zone: 'Green' | 'Orange' | 'Red' | null
  breakdown: EvalBreakdown | null
  ai_isms_found: string[]
}

export interface CompareResponse {
  results: ModelResult[]
  total_models: number
  successful: number
  prompt: string
}

export async function runComparison(req: CompareRequest): Promise<CompareResponse> {
  // Explicit path relative to baseURL (/api), no leading slash to avoid double /api
  const { data } = await api.post<CompareResponse>('v1/compare', req)
  return data
}
