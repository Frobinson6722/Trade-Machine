import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import * as api from '../lib/api'

// Session status
export function useSessionStatus() {
  return useQuery({
    queryKey: ['session-status'],
    queryFn: api.getSessionStatus,
    refetchInterval: 5000,
  })
}

// Trades
export function useTrades(params?: Parameters<typeof api.getTrades>[0]) {
  return useQuery({
    queryKey: ['trades', params],
    queryFn: () => api.getTrades(params),
  })
}

// Portfolio
export function usePortfolio() {
  return useQuery({
    queryKey: ['portfolio'],
    queryFn: api.getPortfolio,
    refetchInterval: 10000,
  })
}

// Equity curve
export function useEquityCurve(limit = 500) {
  return useQuery({
    queryKey: ['equity-curve', limit],
    queryFn: () => api.getEquityCurve(limit),
  })
}

// Agent logs
export function useAgentLogs(params?: Parameters<typeof api.getAgentLogs>[0]) {
  return useQuery({
    queryKey: ['agent-logs', params],
    queryFn: () => api.getAgentLogs(params),
  })
}

// Learning data
export function useLearningData() {
  return useQuery({
    queryKey: ['learning'],
    queryFn: api.getLearningData,
  })
}

// Settings
export function useSettings() {
  return useQuery({
    queryKey: ['settings'],
    queryFn: api.getSettings,
  })
}

// Mutations
export function useStartSession() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ mode, config }: { mode?: string; config?: Record<string, unknown> }) =>
      api.startSession(mode, config),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['session-status'] }),
  })
}

export function useStopSession() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: api.stopSession,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['session-status'] }),
  })
}

export function usePauseSession() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: api.pauseSession,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['session-status'] }),
  })
}

export function useResumeSession() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: api.resumeSession,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['session-status'] }),
  })
}

export function useUpdateSettings() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: api.updateSettings,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['settings'] }),
  })
}
