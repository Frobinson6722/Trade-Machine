import { useState } from 'react'
import { useSessionStatus, useTrades, useStartSession, useStopSession, usePauseSession, useResumeSession } from '../hooks/useApi'
import { Play, Square, Pause, SkipForward, Loader2, AlertCircle, CheckCircle2, Info } from 'lucide-react'

type Toast = { message: string; type: 'success' | 'error' | 'info' }
type Period = 'today' | '7d' | '30d' | 'all'

export default function Dashboard() {
  const { data: status } = useSessionStatus()
  const { data: tradesData } = useTrades({ limit: 200 })
  const startSession = useStartSession()
  const stopSession = useStopSession()
  const pauseSession = usePauseSession()
  const resumeSession = useResumeSession()
  const [toast, setToast] = useState<Toast | null>(null)
  const [period, setPeriod] = useState<Period>('all')

  const showToast = (message: string, type: Toast['type'] = 'info') => {
    setToast({ message, type })
    setTimeout(() => setToast(null), 5000)
  }

  const handleStart = () => {
    startSession.mutate(
      { mode: 'paper' },
      {
        onSuccess: () => showToast('Paper trading started.', 'success'),
        onError: (err) => showToast(`Failed to start: ${err.message}`, 'error'),
      }
    )
  }

  const handleStop = () => {
    stopSession.mutate(undefined, {
      onSuccess: () => showToast('Stopped.', 'info'),
      onError: (err) => showToast(`Failed to stop: ${err.message}`, 'error'),
    })
  }

  const handlePause = () => {
    pauseSession.mutate(undefined, {
      onSuccess: () => showToast('Paused.', 'info'),
      onError: (err) => showToast(`Failed to pause: ${err.message}`, 'error'),
    })
  }

  const handleResume = () => {
    resumeSession.mutate(undefined, {
      onSuccess: () => showToast('Resumed.', 'success'),
      onError: (err) => showToast(`Failed to resume: ${err.message}`, 'error'),
    })
  }

  const isRunning = Boolean((status as any)?.running)
  const isPaused = Boolean((status as any)?.paused)

  // Filter trades by period
  const allTrades = tradesData?.trades ?? []
  const closedTrades = allTrades.filter(t => t.status === 'closed' && t.pnl !== null)

  const now = new Date()
  const filteredTrades = closedTrades.filter(t => {
    if (period === 'all') return true
    const tradeDate = new Date(t.closed_at || t.opened_at)
    const diffMs = now.getTime() - tradeDate.getTime()
    const diffDays = diffMs / (1000 * 60 * 60 * 24)
    if (period === 'today') return diffDays < 1
    if (period === '7d') return diffDays < 7
    if (period === '30d') return diffDays < 30
    return true
  })

  // Cumulative P&L for filtered period
  const totalPnl = filteredTrades.reduce((sum, t) => sum + (t.pnl || 0), 0)
  const wins = filteredTrades.filter(t => (t.pnl || 0) > 0).length
  const losses = filteredTrades.filter(t => (t.pnl || 0) <= 0).length
  const winRate = filteredTrades.length > 0 ? (wins / filteredTrades.length) * 100 : 0

  // Show all trades (open + closed) sorted by most recent
  const displayTrades = allTrades.slice().sort((a, b) =>
    new Date(b.opened_at).getTime() - new Date(a.opened_at).getTime()
  )

  const formatTime = (dateStr: string) => {
    const d = new Date(dateStr)
    return d.toLocaleString('en-US', {
      month: 'short', day: 'numeric',
      hour: 'numeric', minute: '2-digit',
      hour12: true
    })
  }

  return (
    <div className="space-y-6 max-w-3xl mx-auto">
      {/* Toast */}
      {toast && (
        <div className={`fixed top-4 right-4 z-50 flex items-center gap-3 px-4 py-3 rounded-lg shadow-lg border max-w-md ${
          toast.type === 'success' ? 'bg-green-500/10 border-green-500/30 text-green-400' :
          toast.type === 'error' ? 'bg-red-500/10 border-red-500/30 text-red-400' :
          'bg-blue-500/10 border-blue-500/30 text-blue-400'
        }`}>
          {toast.type === 'success' && <CheckCircle2 className="w-5 h-5 shrink-0" />}
          {toast.type === 'error' && <AlertCircle className="w-5 h-5 shrink-0" />}
          {toast.type === 'info' && <Info className="w-5 h-5 shrink-0" />}
          <span className="text-sm">{toast.message}</span>
        </div>
      )}

      {/* Controls */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          {isRunning && !isPaused && (
            <div className="flex items-center gap-2">
              <span className="relative flex h-2.5 w-2.5">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-green-500"></span>
              </span>
              <span className="text-sm text-green-600 font-medium">Running</span>
            </div>
          )}
          {isPaused && (
            <span className="text-sm text-yellow-600 font-medium">Paused</span>
          )}
          {!isRunning && (
            <span className="text-sm text-muted">Stopped</span>
          )}
        </div>
        <div className="flex gap-2">
          {!isRunning ? (
            <button className="btn-primary flex items-center gap-2" onClick={handleStart} disabled={startSession.isPending}>
              {startSession.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
              {startSession.isPending ? 'Starting...' : 'Start'}
            </button>
          ) : isPaused ? (
            <button className="btn-primary flex items-center gap-2" onClick={handleResume} disabled={resumeSession.isPending}>
              {resumeSession.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : <SkipForward className="w-4 h-4" />}
              Resume
            </button>
          ) : (
            <button className="bg-yellow-600 hover:bg-yellow-700 text-white font-medium px-4 py-2 rounded-lg flex items-center gap-2"
              onClick={handlePause} disabled={pauseSession.isPending}>
              {pauseSession.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : <Pause className="w-4 h-4" />}
              Pause
            </button>
          )}
          {isRunning && (
            <button className="btn-danger flex items-center gap-2" onClick={handleStop} disabled={stopSession.isPending}>
              {stopSession.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : <Square className="w-4 h-4" />}
              Stop
            </button>
          )}
        </div>
      </div>

      {/* Big P&L Display */}
      <div className="card text-center py-8">
        <div className="text-sm text-muted mb-2">
          Total P&L
          <span className="ml-2 text-faint">
            ({filteredTrades.length} trades | {winRate.toFixed(0)}% win rate)
          </span>
        </div>
        <div className={`text-5xl font-bold`}
          style={{ color: totalPnl >= 0 ? 'var(--profit)' : 'var(--loss)' }}>
          {totalPnl >= 0 ? '+' : ''}${totalPnl.toFixed(2)}
        </div>
        <div className="flex justify-center gap-2 mt-4">
          {(['today', '7d', '30d', 'all'] as Period[]).map(p => (
            <button key={p} onClick={() => setPeriod(p)}
              className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                period === p
                  ? 'bg-accent text-white'
                  : 'text-muted hover:text-primary hover:bg-surface-hover'
              }`}>
              {p === 'today' ? 'Today' : p === '7d' ? '7 Days' : p === '30d' ? '30 Days' : 'All Time'}
            </button>
          ))}
        </div>
      </div>

      {/* Trade List */}
      <div>
        <h3 className="text-sm font-medium text-muted mb-3">Trades</h3>
        {displayTrades.length === 0 ? (
          <div className="card text-center text-muted py-8">
            No trades yet. {!isRunning && 'Click Start to begin.'}
          </div>
        ) : (
          <div className="space-y-1">
            {displayTrades.map((trade, i) => {
              const isOpen = trade.status === 'open'
              const pnl = trade.pnl || 0
              const isWin = pnl > 0

              return (
                <div key={trade.id || i} className="card flex items-center justify-between py-3 px-4">
                  <div className="flex items-center gap-3">
                    <div className={`w-2 h-2 rounded-full ${
                      isOpen ? 'bg-blue-500' : isWin ? 'bg-green-500' : 'bg-red-500'
                    }`} />
                    <div>
                      <span className="text-sm font-medium text-primary">{trade.pair}</span>
                      <span className="text-xs text-muted ml-2">
                        {formatTime(trade.closed_at || trade.opened_at)}
                      </span>
                    </div>
                  </div>
                  <div className="text-right">
                    {isOpen ? (
                      <span className="text-sm text-blue-500 font-medium">Open</span>
                    ) : (
                      <span className={`text-sm font-bold`}
                        style={{ color: isWin ? 'var(--profit)' : 'var(--loss)' }}>
                        {pnl >= 0 ? '+' : ''}${pnl.toFixed(2)}
                      </span>
                    )}
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}
