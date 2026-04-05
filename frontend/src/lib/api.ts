// API client for the Trade Machine backend

const BASE_URL = '/api'

function getAuthHeaders(): Record<string, string> {
  const token = localStorage.getItem('auth_token') || ''
  return token ? { Authorization: `Bearer ${token}` } : {}
}

async function fetchApi<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeaders(),
      ...options?.headers,
    },
  })

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(error.detail || `API error: ${res.status}`)
  }

  return res.json()
}

// Trades
export const getTrades = (params?: { pair?: string; status?: string; limit?: number; offset?: number }) => {
  const query = new URLSearchParams()
  if (params?.pair) query.set('pair', params.pair)
  if (params?.status) query.set('status', params.status)
  if (params?.limit) query.set('limit', String(params.limit))
  if (params?.offset) query.set('offset', String(params.offset))
  const qs = query.toString()
  return fetchApi<import('./types').TradeListResponse>(`/trades${qs ? `?${qs}` : ''}`)
}

export const getTrade = (id: number) =>
  fetchApi<import('./types').Trade>(`/trades/${id}`)

export const clearTrades = () =>
  fetchApi('/trades', { method: 'DELETE' })

// Portfolio
export const getPortfolio = () =>
  fetchApi<import('./types').Portfolio>('/portfolio')

export const getEquityCurve = (limit = 500) =>
  fetchApi<{ points: import('./types').EquityCurvePoint[] }>(`/portfolio/equity-curve?limit=${limit}`)

// Agents
export const getAgentLogs = (params?: { cycle_id?: string; agent_name?: string; limit?: number }) => {
  const query = new URLSearchParams()
  if (params?.cycle_id) query.set('cycle_id', params.cycle_id)
  if (params?.agent_name) query.set('agent_name', params.agent_name)
  if (params?.limit) query.set('limit', String(params.limit))
  const qs = query.toString()
  return fetchApi<import('./types').AgentLogListResponse>(`/agents/logs${qs ? `?${qs}` : ''}`)
}

// Learning
export const getLearningData = () =>
  fetchApi<import('./types').LearningData>('/learning')

// Sessions
export const startSession = (mode = 'paper', config = {}) =>
  fetchApi('/sessions/start', { method: 'POST', body: JSON.stringify({ mode, config }) })

export const stopSession = () =>
  fetchApi('/sessions/stop', { method: 'POST' })

export const pauseSession = () =>
  fetchApi('/sessions/pause', { method: 'POST' })

export const resumeSession = () =>
  fetchApi('/sessions/resume', { method: 'POST' })

export const getSessionStatus = () =>
  fetchApi<import('./types').SessionStatus>('/sessions/status')

// Settings
export const getSettings = () =>
  fetchApi<import('./types').Settings>('/settings')

export const updateSettings = (updates: Partial<import('./types').Settings>) =>
  fetchApi('/settings', { method: 'PUT', body: JSON.stringify(updates) })

// Health
export const getHealth = () =>
  fetchApi<{ status: string; engine: Record<string, unknown> }>('/health')
