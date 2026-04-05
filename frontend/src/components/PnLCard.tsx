import { TrendingUp, TrendingDown, BarChart3, Target } from 'lucide-react'

interface Props {
  totalPnl: number
  winRate: number
  totalTrades: number
  avgPnl: number
}

export default function PnLCard({ totalPnl, winRate, totalTrades, avgPnl }: Props) {
  const isProfit = totalPnl >= 0

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
      <div className="card">
        <div className="flex items-center gap-2 text-muted text-sm mb-1">
          {isProfit ? <TrendingUp className="w-4 h-4 text-profit" /> : <TrendingDown className="w-4 h-4 text-loss" />}
          Total P&L
        </div>
        <div className={`text-2xl font-bold text-profit`} style={{ color: isProfit ? 'var(--profit)' : 'var(--loss)' }}>
          {isProfit ? '+' : ''}{totalPnl.toFixed(2)}
        </div>
      </div>
      <div className="card">
        <div className="flex items-center gap-2 text-muted text-sm mb-1">
          <Target className="w-4 h-4" />
          Win Rate
        </div>
        <div className="text-2xl font-bold" style={{ color: winRate >= 55 ? 'var(--profit)' : winRate >= 50 ? '#ca8a04' : 'var(--loss)' }}>
          {winRate.toFixed(1)}%
        </div>
      </div>
      <div className="card">
        <div className="flex items-center gap-2 text-muted text-sm mb-1">
          <BarChart3 className="w-4 h-4" />
          Total Trades
        </div>
        <div className="text-2xl font-bold text-primary">{totalTrades}</div>
      </div>
      <div className="card">
        <div className="flex items-center gap-2 text-muted text-sm mb-1">
          {avgPnl >= 0 ? <TrendingUp className="w-4 h-4 text-profit" /> : <TrendingDown className="w-4 h-4 text-loss" />}
          Avg P&L/Trade
        </div>
        <div className="text-2xl font-bold" style={{ color: avgPnl >= 0 ? 'var(--profit)' : 'var(--loss)' }}>
          {avgPnl >= 0 ? '+' : ''}{avgPnl.toFixed(2)}
        </div>
      </div>
    </div>
  )
}
