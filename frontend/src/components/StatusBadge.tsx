import { useSessionStatus } from '../hooks/useApi'

const statusColors: Record<string, string> = {
  running: 'bg-green-500',
  paused: 'bg-yellow-500',
  stopped: 'bg-gray-500',
}

const stageLabels: Record<string, string> = {
  paper: 'Paper Trading',
  micro: 'Micro ($1)',
  graduated: 'Graduated',
}

export default function StatusBadge() {
  const { data } = useSessionStatus()

  const isRunning = data?.running ?? false
  const isPaused = data?.paused ?? false
  const status = isPaused ? 'paused' : isRunning ? 'running' : 'stopped'
  const stage = data?.stage?.current_stage ?? 'paper'
  const mode = data?.mode ?? 'paper'

  return (
    <div className="space-y-1">
      <div className="flex items-center gap-2">
        <span className={`w-2 h-2 rounded-full ${statusColors[status] || 'bg-gray-500'}`} />
        <span className="text-sm font-medium capitalize">{status}</span>
      </div>
      <div className="text-xs text-gray-500">
        {stageLabels[stage] || stage} · {mode === 'live' ? 'LIVE' : 'Paper'}
      </div>
    </div>
  )
}
