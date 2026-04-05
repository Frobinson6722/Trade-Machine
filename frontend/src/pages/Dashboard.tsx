import { useState } from 'react'
import PnLCard from '../components/PnLCard'
import EquityCurve from '../components/EquityCurve'
import TradeTable from '../components/TradeTable'
import { useSessionStatus, useTrades, useEquityCurve, useStartSession, useStopSession, usePauseSession, useResumeSession } from '../hooks/useApi'
import { Play, Square, Pause, SkipForward, Loader2, AlertCircle, CheckCircle2, Info } from 'lucide-react'

type Toast = { message: string; type: 'success' | 'error' | 'info' }

export default function Dashboard() {
  const { data: status } = useSessionStatus()
  const { data: tradesData } = useTrades({ limit: 5 })
  const { data: equityData } = useEquityCurve()
  const startSession = useStartSession()
  const stopSession = useStopSession()
  const pauseSession = usePauseSession()
  const resumeSession = useResumeSession()
  const [toast, setToast] = useState<Toast | null>(null)

  const showToast = (message: string, type: Toast['type'] = 'info') => {
    setToast({ message, type })
    setTimeout(() => setToast(null), 5000)
  }

  const handleStart = () => {
    startSession.mutate(
      { mode: 'paper' },
      {
        onSuccess: () => showToast('Paper trading session started! The engine will analyze markets every 15 minutes.', 'success'),
        onError: (err) => showToast(`Failed to start: ${err.message}`, 'error'),
      }
    )
  }

  const handleStop = () => {
    stopSession.mutate(undefined, {
      onSuccess: () => showToast('Trading session stopped.', 'info'),
      onError: (err) => showToast(`Failed to stop: ${err.message}`, 'error'),
    })
  }

  const handlePause = () => {
    pauseSession.mutate(undefined, {
      onSuccess: () => showToast('Trading session paused.', 'info'),
      onError: (err) => showToast(`Failed to pause: ${err.message}`, 'error'),
    })
  }

  const handleResume = () => {
    resumeSession.mutate(undefined, {
      onSuccess: () => showToast('Trading session resumed!', 'success'),
      onError: (err) => showToast(`Failed to resume: ${err.message}`, 'error'),
    })
  }

  // Safely extract stats with defaults
  const rawStats = (status as any)?.stats ?? {}
  const totalPnl = Number(rawStats.total_pnl) || 0
  const winRate = Number(rawStats.win_rate) || 0
  const totalTrades = Number(rawStats.total) || Number(rawStats.total_trades) || 0
  const avgPnl = Number(rawStats.avg_pnl) || 0

  const isRunning = Boolean((status as any)?.running)
  const isPaused = Boolean((status as any)?.paused)
  const currentStage = (status as any)?.stage?.current_stage ?? (status as any)?.stage ?? 'paper'
  const mode = (status as any)?.mode ?? 'paper'

  // Safely extract stage info
  const stage = (status as any)?.stage ?? {}
  const tradesCompleted = Number(stage.trades_completed) || 0
  const stageWinRate = Number(stage.win_rate) || 0
  const graduationDetails = stage.graduation_check?.details ?? ''
  const graduationEligible = Boolean(stage.graduation_check?.eligible)

  return (
    <div className="space-y-6">
      {/* Toast notification */}
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

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Dashboard</h2>
          <p className="text-sm text-gray-500 mt-1">
            Stage: {typeof currentStage === 'string' ? currentStage : 'paper'} | Mode: {mode}
          </p>
        </div>

        <div className="flex gap-2">
          {!isRunning ? (
            <button
              className="btn-primary flex items-center gap-2"
              onClick={handleStart}
              disabled={startSession.isPending}
            >
              {startSession.isPending ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Play className="w-4 h-4" />
              )}
              {startSession.isPending ? 'Starting...' : 'Start Paper Trading'}
            </button>
          ) : isPaused ? (
            <button
              className="btn-primary flex items-center gap-2"
              onClick={handleResume}
              disabled={resumeSession.isPending}
            >
              {resumeSession.isPending ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <SkipForward className="w-4 h-4" />
              )}
              {resumeSession.isPending ? 'Resuming...' : 'Resume'}
            </button>
          ) : (
            <button
              className="bg-yellow-600 hover:bg-yellow-700 text-white font-medium px-4 py-2 rounded-lg flex items-center gap-2"
              onClick={handlePause}
              disabled={pauseSession.isPending}
            >
              {pauseSession.isPending ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Pause className="w-4 h-4" />
              )}
              {pauseSession.isPending ? 'Pausing...' : 'Pause'}
            </button>
          )}
          {isRunning && (
            <button
              className="btn-danger flex items-center gap-2"
              onClick={handleStop}
              disabled={stopSession.isPending}
            >
              {stopSession.isPending ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Square className="w-4 h-4" />
              )}
              {stopSession.isPending ? 'Stopping...' : 'Stop'}
            </button>
          )}
        </div>
      </div>

      {/* System status banner */}
      {isRunning && !isPaused && (
        <div className="flex items-center gap-3 px-4 py-3 bg-green-500/10 border border-green-500/30 rounded-lg">
          <div className="relative flex h-3 w-3">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
          </div>
          <span className="text-sm text-green-400">
            Engine is running — analyzing BTC & ETH with Claude AI agents. Cycles run every 15 minutes.
          </span>
        </div>
      )}

      {isPaused && (
        <div className="flex items-center gap-3 px-4 py-3 bg-yellow-500/10 border border-yellow-500/30 rounded-lg">
          <Pause className="w-4 h-4 text-yellow-400" />
          <span className="text-sm text-yellow-400">
            Engine is paused. No new analysis cycles will run until you resume.
          </span>
        </div>
      )}

      {!isRunning && !startSession.isPending && (
        <div className="flex items-center gap-3 px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg">
          <Info className="w-4 h-4 text-gray-400" />
          <span className="text-sm text-gray-400">
            Engine is stopped. Click "Start Paper Trading" to begin. Make sure your Anthropic API key is set in the .env file.
          </span>
        </div>
      )}

      {/* P&L Cards */}
      <PnLCard
        totalPnl={totalPnl}
        winRate={winRate * 100}
        totalTrades={totalTrades}
        avgPnl={avgPnl}
      />

      {/* Stage Progress */}
      {graduationDetails && (
        <div className="card">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-gray-400">Stage Progress</h3>
            <span className="text-xs text-gray-500">
              {tradesCompleted} trades | {(stageWinRate * 100).toFixed(1)}% win rate
            </span>
          </div>
          <div className="text-sm text-gray-300">{graduationDetails}</div>
          {graduationEligible && (
            <div className="mt-2 px-3 py-1.5 bg-green-500/10 border border-green-500/30 rounded text-green-400 text-sm">
              Eligible for graduation!
            </div>
          )}
        </div>
      )}

      {/* Equity Curve */}
      <EquityCurve data={equityData?.points ?? []} />

      {/* Recent Trades */}
      <div>
        <h3 className="text-lg font-medium mb-3">Recent Trades</h3>
        <TradeTable trades={tradesData?.trades ?? []} />
      </div>
    </div>
  )
}
