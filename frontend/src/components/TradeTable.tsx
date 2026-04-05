import { useState } from 'react'
import { ChevronDown, ChevronRight } from 'lucide-react'
import type { Trade } from '../lib/types'
import AgentReasoningPanel from './AgentReasoningPanel'

interface Props {
  trades: Trade[]
  showExpand?: boolean
}

export default function TradeTable({ trades, showExpand = true }: Props) {
  const [expandedId, setExpandedId] = useState<number | null>(null)

  if (!trades.length) {
    return (
      <div className="card text-center text-gray-500 py-8">
        No trades yet.
      </div>
    )
  }

  return (
    <div className="card overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="text-gray-400 border-b border-gray-800">
            {showExpand && <th className="w-8 pb-2" />}
            <th className="text-left pb-2">Pair</th>
            <th className="text-left pb-2">Side</th>
            <th className="text-right pb-2">Entry</th>
            <th className="text-right pb-2">Exit</th>
            <th className="text-right pb-2">P&L</th>
            <th className="text-right pb-2">P&L %</th>
            <th className="text-left pb-2">Stage</th>
            <th className="text-left pb-2">Status</th>
            <th className="text-left pb-2">Time</th>
          </tr>
        </thead>
        <tbody>
          {trades.map((trade) => (
            <>
              <tr
                key={trade.id}
                className="border-b border-gray-800/50 hover:bg-gray-800/30 cursor-pointer"
                onClick={() => showExpand && setExpandedId(expandedId === trade.id ? null : trade.id)}
              >
                {showExpand && (
                  <td className="py-2">
                    {expandedId === trade.id ? (
                      <ChevronDown className="w-4 h-4 text-gray-500" />
                    ) : (
                      <ChevronRight className="w-4 h-4 text-gray-500" />
                    )}
                  </td>
                )}
                <td className="py-2 font-medium">{trade.pair}</td>
                <td className={`py-2 ${trade.side === 'BUY' ? 'text-profit' : 'text-loss'}`}>
                  {trade.side}
                </td>
                <td className="py-2 text-right">${trade.entry_price.toLocaleString()}</td>
                <td className="py-2 text-right">
                  {trade.exit_price ? `$${trade.exit_price.toLocaleString()}` : '-'}
                </td>
                <td className={`py-2 text-right font-medium ${
                  trade.pnl != null ? (trade.pnl >= 0 ? 'text-profit' : 'text-loss') : ''
                }`}>
                  {trade.pnl != null ? `${trade.pnl >= 0 ? '+' : ''}$${trade.pnl.toFixed(2)}` : '-'}
                </td>
                <td className={`py-2 text-right ${
                  trade.pnl_pct != null ? (trade.pnl_pct >= 0 ? 'text-profit' : 'text-loss') : ''
                }`}>
                  {trade.pnl_pct != null ? `${trade.pnl_pct >= 0 ? '+' : ''}${trade.pnl_pct.toFixed(2)}%` : '-'}
                </td>
                <td className="py-2 text-gray-400 capitalize">{trade.stage}</td>
                <td className="py-2">
                  <span className={`px-2 py-0.5 rounded text-xs ${
                    trade.status === 'open' ? 'bg-blue-500/20 text-blue-400' :
                    trade.status === 'closed' ? 'bg-gray-700 text-gray-300' :
                    'bg-yellow-500/20 text-yellow-400'
                  }`}>
                    {trade.status}
                  </span>
                </td>
                <td className="py-2 text-gray-400 text-xs">
                  {new Date(trade.opened_at).toLocaleString()}
                </td>
              </tr>
              {showExpand && expandedId === trade.id && (
                <tr key={`${trade.id}-detail`}>
                  <td colSpan={10} className="p-4 bg-gray-800/20">
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
