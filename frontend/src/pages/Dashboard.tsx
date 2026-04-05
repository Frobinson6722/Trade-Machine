import PnLCard from '../components/PnLCard'
import EquityCurve from '../components/EquityCurve'
import TradeTable from '../components/TradeTable'
import { useSessionStatus, useTrades, useEquityCurve, useStartSession, useStopSession, usePauseSession, useResumeSession } from '../hooks/useApi'
import { Play, Square, Pause, SkipForward } from 'lucide-react'

export default function Dashboard() {
  const { data: status } = useSessionStatus()
  const { data: tradesData } = useTrades({ limit: 5 })
  const { data: equityData } = useEquityCurve()
  const startSession = useStartSession()
  const stopSession = useStopSession()
  const pauseSession = usePauseSession()
  const resumeSession = useResumeSession()

  const stats = status?.stats ?? { total: 0, wins: 0, losses: 0, win_rate: 0, total_pnl: 0, avg_pnl: 0 }
  const isRunning = status?.running ?? false
  const isPaused = status?.paused ?? false

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Dashboard</h2>
          <p className="text-sm text-gray-500 mt-1">
            Stage: {status?.stage?.current_stage ?? 'paper'} | Mode: {status?.mode ?? 'paper'}
          </p>
        </div>

        <div className="flex gap-2">
          {!isRunning ? (
            <button
              className="btn-primary flex items-center gap-2"
              onClick={() => startSession.mutate({ mode: 'paper' })}
              disabled={startSession.isPending}
            >
              <Play className="w-4 h-4" />
              Start Paper Trading
            </button>
          ) : isPaused ? (
            <button
              className="btn-primary flex items-center gap-2"
              onClick={() => resumeSession.mutate()}
            >
              <SkipForward className="w-4 h-4" />
              Resume
            </button>
          ) : (
            <button
              className="bg-yellow-600 hover:bg-yellow-700 text-white font-medium px-4 py-2 rounded-lg flex items-center gap-2"
              onClick={() => pauseSession.mutate()}
            >
              <Pause className="w-4 h-4" />
              Pause
            </button>
          )}
          {isRunning && (
            <button
              className="btn-danger flex items-center gap-2"
              onClick={() => stopSession.mutate()}
            >
              <Square className="w-4 h-4" />
              Stop
            </button>
          )}
        </div>
      </div>

      {/* P&L Cards */}
      <PnLCard
        totalPnl={stats.total_pnl}
        winRate={stats.win_rate * 100}
        totalTrades={stats.total}
        avgPnl={stats.avg_pnl}
      />

      {/* Stage Progress */}
      {status?.stage && (
        <div className="card">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-gray-400">Stage Progress</h3>
            <span className="text-xs text-gray-500">
              {status.stage.trades_completed} trades | {(status.stage.win_rate * 100).toFixed(1)}% win rate
            </span>
          </div>
          <div className="text-sm text-gray-300">{status.stage.graduation_check?.details}</div>
          {status.stage.graduation_check?.eligible && (
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
