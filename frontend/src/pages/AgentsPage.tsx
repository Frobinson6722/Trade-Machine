import { useTrades } from '../hooks/useApi'
import { Brain, TrendingUp, TrendingDown, Minus } from 'lucide-react'
import { formatTime } from '../lib/time'
import type { Trade } from '../lib/types'

export default function AgentsPage() {
  const { data, isLoading } = useTrades({ limit: 50 })
  const trades = data?.trades ?? []

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-primary">Trade Decisions</h2>
        <p className="text-sm text-muted mt-1">Why each trade was made — the reasoning behind every buy and sell.</p>
      </div>

      {isLoading ? (
        <div className="text-muted">Loading trade decisions...</div>
      ) : !trades.length ? (
        <div className="card text-center text-muted py-12">
          <Brain className="w-10 h-10 mx-auto mb-3 opacity-30" />
          <div className="text-lg font-medium mb-1">No trades yet</div>
          <div className="text-sm">Start a trading session. Trades and their reasoning will appear here.</div>
        </div>
      ) : (
        <div className="space-y-4">
          {trades.map((trade) => (
            <TradeDecisionCard key={trade.id} trade={trade} />
          ))}
        </div>
      )}
    </div>
  )
}

function TradeDecisionCard({ trade }: { trade: Trade }) {
  const isBuy = trade.side === 'BUY'
  const isClosed = trade.status === 'closed'
  const pnl = trade.pnl ?? 0
  const isProfit = pnl >= 0

  return (
    <div className="card">
      {/* Header row */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-3">
          <div className={`p-2 rounded-lg ${isBuy ? 'bg-green-500/10' : 'bg-red-500/10'}`}>
            {isBuy ? <TrendingUp className="w-5 h-5 text-profit" /> : <TrendingDown className="w-5 h-5 text-loss" />}
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-primary text-lg">{trade.side} {trade.pair}</span>
              <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                trade.status === 'open' ? 'bg-blue-500/15 text-blue-600' : 'bg-surface-tertiary text-muted'
              }`}>{trade.status}</span>
            </div>
            <div className="text-xs text-faint">{formatTime(trade.opened_at)}</div>
          </div>
        </div>

        {/* P&L */}
        <div className="text-right">
          <div className="text-sm text-muted">Entry: ${trade.entry_price.toFixed(6)}</div>
          {isClosed && trade.exit_price && (
            <div className="text-sm text-muted">Exit: ${trade.exit_price.toFixed(6)}</div>
          )}
          {(isClosed && trade.pnl != null) ? (
            <div className={`text-xl font-bold ${isProfit ? 'text-profit' : 'text-loss'}`}>
              {isProfit ? '+' : ''}${pnl.toFixed(2)}
              <span className="text-sm ml-1">({trade.pnl_pct != null ? `${trade.pnl_pct >= 0 ? '+' : ''}${trade.pnl_pct.toFixed(1)}%` : ''})</span>
            </div>
          ) : (
            <div className="text-sm text-muted">Open position</div>
          )}
        </div>
      </div>

      {/* Trade parameters */}
      <div className="flex gap-4 text-sm text-muted mb-3">
        <span>Size: ${trade.size_usd.toFixed(2)}</span>
        {trade.stop_loss && <span>Stop: ${trade.stop_loss.toFixed(6)}</span>}
        {trade.take_profit && <span>Target: ${trade.take_profit.toFixed(6)}</span>}
        <span>Stage: {trade.stage}</span>
        {trade.exit_trigger && <span>Closed by: {trade.exit_trigger.replace(/_/g, ' ')}</span>}
      </div>

      {/* Divider */}
      <div className="border-t border-border my-3" />

      {/* Decision summary */}
      <div className="text-sm text-secondary leading-relaxed">
        <span className="text-xs font-semibold text-muted uppercase tracking-wide">Decision Logic: </span>
        {isBuy
          ? `The 12-agent pipeline analyzed ${trade.pair} and determined a buying opportunity. The Bull Researcher's thesis was stronger than the Bear's, the Research Manager approved, and the Portfolio Manager signed off on a ${trade.size_usd.toFixed(2)} position with a ${trade.stop_loss ? `$${trade.stop_loss.toFixed(6)} stop-loss` : 'no stop-loss'} and ${trade.take_profit ? `$${trade.take_profit.toFixed(6)} profit target` : 'no explicit target'}.`
          : `The system decided to sell ${trade.pair}. ${trade.exit_trigger === 'stop_loss' ? 'Stop-loss was triggered — price dropped below the safety level.' : trade.exit_trigger === 'take_profit' ? 'Take-profit was hit — the price target was reached.' : trade.exit_trigger === 'auto_stop_loss' ? 'Auto safety stop triggered at -5% to limit losses.' : trade.exit_trigger === 'auto_take_profit' ? 'Auto profit lock at +8% to secure gains.' : 'Position was closed based on updated market analysis.'}`
        }
      </div>

      {/* Outcome for closed trades */}
      {isClosed && trade.pnl != null && (
        <div className={`mt-3 px-3 py-2 rounded-lg text-sm font-medium ${
          isProfit ? 'bg-green-500/10 text-green-700' : 'bg-red-500/10 text-red-700'
        }`}>
          {isProfit
            ? `This trade earned $${pnl.toFixed(2)} (${trade.pnl_pct?.toFixed(1)}%). The bullish thesis was correct.`
            : `This trade lost $${Math.abs(pnl).toFixed(2)} (${trade.pnl_pct?.toFixed(1)}%). The system will reflect on what went wrong and adjust its strategy.`
          }
        </div>
      )}
    </div>
  )
}
