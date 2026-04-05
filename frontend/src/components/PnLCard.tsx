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
        <div className="flex items-center gap-2 text-gray-400 text-sm mb-1">
          {isProfit ? <TrendingUp className="w-4 h-4 text-profit" /> : <TrendingDown className="w-4 h-4 text-loss" />}
          Total P&L
        </div>
        <div className={`text-2xl font-bold ${isProfit ? 'text-profit' : 'text-loss'}`}>
          {isProfit ? '+' : ''}{totalPnl.toFixed(2)}
        </div>
      </div>

      <div className="card">
        <div className="flex items-center gap-2 text-gray-400 text-sm mb-1">
          <Target className="w-4 h-4" />
          Win Rate
        </div>
        <div className={`text-2xl font-bold ${winRate >= 55 ? 'text-profit' : winRate >= 50 ? 'text-yellow-400' : 'text-loss'}`}>
          {(winRate).toFixed(1)}%
        </div>
      </div>

      <div className="card">
        <div className="flex items-center gap-2 text-gray-400 text-sm mb-1">
          <BarChart3 className="w-4 h-4" />
          Total Trades
        </div>
        <div className="text-2xl font-bold">{totalTrades}</div>
      </div>

      <div className="card">
        <div className="flex items-center gap-2 text-gray-400 text-sm mb-1">
          {avgPnl >= 0 ? <TrendingUp className="w-4 h-4 text-profit" /> : <TrendingDown className="w-4 h-4 text-loss" />}
          Avg P&L/Trade
        </div>
        <div className={`text-2xl font-bold ${avgPnl >= 0 ? 'text-profit' : 'text-loss'}`}>
          {avgPnl >= 0 ? '+' : ''}{avgPnl.toFixed(2)}
        </div>
      </div>
    </div>
  )
}
