import { useState } from 'react'
import { ChevronDown, ChevronRight } from 'lucide-react'
import type { Trade } from '../lib/types'
import { formatTime } from '../lib/time'
import AgentReasoningPanel from './AgentReasoningPanel'

interface Props {
  trades: Trade[]
  showExpand?: boolean
}

export default function TradeTable({ trades, showExpand = true }: Props) {
  const [expandedId, setExpandedId] = useState<number | null>(null)

  if (!trades.length) {
    return (
      <div className="card text-center text-muted py-8">
        No trades yet.
      </div>
    )
  }

  return (
    <div className="card overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="text-muted border-b border-border">
            {showExpand && <th className="w-8 pb-3" />}
            <th className="text-left pb-3 font-medium">Pair</th>
            <th className="text-left pb-3 font-medium">Side</th>
            <th className="text-right pb-3 font-medium">Entry</th>
            <th className="text-right pb-3 font-medium">Exit</th>
            <th className="text-right pb-3 font-medium">P&L</th>
            <th className="text-right pb-3 font-medium">P&L %</th>
            <th className="text-left pb-3 font-medium">Stage</th>
            <th className="text-left pb-3 font-medium">Status</th>
            <th className="text-left pb-3 font-medium">Time</th>
          </tr>
        </thead>
        <tbody>
          {trades.map((trade) => (
            <>
              <tr
                key={trade.id}
                className="border-b border-border hover:bg-surface-hover cursor-pointer transition-colors"
                onClick={() => showExpand && setExpandedId(expandedId === trade.id ? null : trade.id)}
              >
                {showExpand && (
                  <td className="py-3">
                    {expandedId === trade.id
                      ? <ChevronDown className="w-4 h-4 text-muted" />
                      : <ChevronRight className="w-4 h-4 text-muted" />
                    }
                  </td>
                )}
                <td className="py-3 font-semibold text-primary">{trade.pair}</td>
                <td className="py-3">
                  <span className={`font-medium ${trade.side === 'BUY' ? 'text-profit' : 'text-loss'}`}>
                    {trade.side}
                  </span>
                </td>
                <td className="py-3 text-right text-secondary">${trade.entry_price.toLocaleString()}</td>
                <td className="py-3 text-right text-secondary">
                  {trade.exit_price ? `$${trade.exit_price.toLocaleString()}` : '-'}
                </td>
                <td className={`py-3 text-right font-semibold ${
                  trade.pnl != null ? (trade.pnl >= 0 ? 'text-profit' : 'text-loss') : 'text-muted'
                }`}>
                  {trade.pnl != null ? `${trade.pnl >= 0 ? '+' : ''}$${trade.pnl.toFixed(2)}` : '-'}
                </td>
                <td className={`py-3 text-right ${
                  trade.pnl_pct != null ? (trade.pnl_pct >= 0 ? 'text-profit' : 'text-loss') : 'text-muted'
                }`}>
                  {trade.pnl_pct != null ? `${trade.pnl_pct >= 0 ? '+' : ''}${trade.pnl_pct.toFixed(2)}%` : '-'}
                </td>
                <td className="py-3 text-muted capitalize">{trade.stage}</td>
                <td className="py-3">
                  <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                    trade.status === 'open' ? 'bg-blue-500/15 text-blue-600' :
                    trade.status === 'closed' ? 'bg-surface-tertiary text-muted' :
                    'bg-yellow-500/15 text-yellow-600'
                  }`}>
                    {trade.status}
                  </span>
                </td>
                <td className="py-3 text-faint text-xs">
                  {formatTime(trade.opened_at)}
                </td>
              </tr>
              {showExpand && expandedId === trade.id && (
                <tr key={`${trade.id}-detail`}>
                  <td colSpan={10} className="p-4 bg-surface-tertiary">
                    <AgentReasoningPanel cycleId={trade.cycle_id} />
                  </td>
                </tr>
              )}
            </>
          ))}
        </tbody>
      </table>
    </div>
  )
}
