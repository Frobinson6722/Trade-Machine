import { useQuery } from '@tanstack/react-query'
import { DollarSign, Zap, Clock, BarChart3, TrendingUp } from 'lucide-react'
import { formatTime } from '../lib/time'

interface UsageData {
  total_calls: number
  total_input_tokens: number
  total_output_tokens: number
  total_tokens: number
  total_cost: number
  estimated_daily_cost: number
  cost_per_cycle: number
  by_agent: Record<string, { calls: number; input_tokens: number; output_tokens: number; cost: number }>
  by_model: Record<string, { calls: number; input_tokens: number; output_tokens: number; cost: number }>
  hourly_costs: { hour: string; cost: number }[]
  recent_calls: { timestamp: string; model: string; agent_name: string; input_tokens: number; output_tokens: number; cost: number }[]
}

function useUsageData() {
  return useQuery<UsageData>({
    queryKey: ['usage'],
    queryFn: async () => {
      const res = await fetch('/api/usage')
      return res.json()
    },
    refetchInterval: 15000,
  })
}

function formatTokens(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`
  return String(n)
}

function formatCost(n: number): string {
  if (n < 0.01) return `$${n.toFixed(4)}`
  return `$${n.toFixed(2)}`
}

export default function ApiCostsPage() {
  const { data, isLoading } = useUsageData()

  if (isLoading) return <div className="text-muted">Loading usage data...</div>

  const usage = data ?? {
    total_calls: 0, total_input_tokens: 0, total_output_tokens: 0,
    total_tokens: 0, total_cost: 0, estimated_daily_cost: 0,
    cost_per_cycle: 0, by_agent: {}, by_model: {}, hourly_costs: [], recent_calls: [],
  }

  const agentEntries = Object.entries(usage.by_agent).sort((a, b) => b[1].cost - a[1].cost)
  const modelEntries = Object.entries(usage.by_model).sort((a, b) => b[1].cost - a[1].cost)

  return (
    <div className="space-y-6 max-w-4xl">
      <div className="flex items-center gap-3">
        <DollarSign className="w-6 h-6 text-accent" />
        <h2 className="text-2xl font-bold text-primary">API Costs</h2>
      </div>
      <p className="text-sm text-muted">Real-time tracking of every Claude API call, token usage, and estimated costs.</p>

      {/* Top-level cost cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="card">
          <div className="flex items-center gap-2 text-muted text-sm mb-1">
            <DollarSign className="w-4 h-4" /> Total Spend
          </div>
          <div className="text-2xl font-bold text-primary">{formatCost(usage.total_cost)}</div>
        </div>
        <div className="card">
          <div className="flex items-center gap-2 text-muted text-sm mb-1">
            <TrendingUp className="w-4 h-4" /> Est. Daily Cost
          </div>
          <div className="text-2xl font-bold" style={{
            color: usage.estimated_daily_cost > 5 ? 'var(--loss)' :
                   usage.estimated_daily_cost > 1 ? '#ca8a04' : 'var(--profit)'
          }}>
            {formatCost(usage.estimated_daily_cost)}/day
          </div>
        </div>
        <div className="card">
          <div className="flex items-center gap-2 text-muted text-sm mb-1">
            <Zap className="w-4 h-4" /> API Calls
          </div>
          <div className="text-2xl font-bold text-primary">{usage.total_calls}</div>
        </div>
        <div className="card">
          <div className="flex items-center gap-2 text-muted text-sm mb-1">
            <BarChart3 className="w-4 h-4" /> Cost/Cycle
          </div>
          <div className="text-2xl font-bold text-primary">{formatCost(usage.cost_per_cycle)}</div>
        </div>
      </div>

      {/* Token breakdown */}
      <div className="card">
        <h3 className="text-sm font-medium text-muted mb-3">Token Usage</h3>
        <div className="grid grid-cols-3 gap-4">
          <div>
            <div className="text-faint text-xs mb-1">Input Tokens</div>
            <div className="text-lg font-semibold text-primary">{formatTokens(usage.total_input_tokens)}</div>
          </div>
          <div>
            <div className="text-faint text-xs mb-1">Output Tokens</div>
            <div className="text-lg font-semibold text-primary">{formatTokens(usage.total_output_tokens)}</div>
          </div>
          <div>
            <div className="text-faint text-xs mb-1">Total Tokens</div>
            <div className="text-lg font-semibold text-primary">{formatTokens(usage.total_tokens)}</div>
          </div>
        </div>
      </div>

      {/* Cost by agent */}
      {agentEntries.length > 0 && (
        <div className="card">
          <h3 className="text-sm font-medium text-muted mb-3">Cost by Agent</h3>
          <p className="text-xs text-faint mb-3">Which AI agents are costing the most</p>
          <div className="space-y-2">
            {agentEntries.map(([name, stats]) => {
              const pct = usage.total_cost > 0 ? (stats.cost / usage.total_cost) * 100 : 0
              return (
                <div key={name} className="flex items-center gap-3">
                  <div className="w-36 text-sm font-medium text-secondary truncate">
                    {name.replace(/_/g, ' ')}
                  </div>
                  <div className="flex-1 h-6 rounded-full overflow-hidden bg-surface-tertiary">
                    <div
                      className="h-full rounded-full bg-accent/60"
                      style={{ width: `${Math.max(pct, 2)}%` }}
                    />
                  </div>
                  <div className="text-sm font-semibold text-primary w-16 text-right">{formatCost(stats.cost)}</div>
                  <div className="text-xs text-faint w-12 text-right">{stats.calls} calls</div>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* Cost by model */}
      {modelEntries.length > 0 && (
        <div className="card">
          <h3 className="text-sm font-medium text-muted mb-3">Cost by Model</h3>
          <div className="space-y-3">
            {modelEntries.map(([model, stats]) => (
              <div key={model} className="card-inner flex items-center justify-between">
                <div>
                  <div className="text-sm font-semibold text-primary">{model}</div>
                  <div className="text-xs text-faint">{stats.calls} calls | {formatTokens(stats.input_tokens)} in / {formatTokens(stats.output_tokens)} out</div>
                </div>
                <div className="text-lg font-bold text-primary">{formatCost(stats.cost)}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recent API calls */}
      {usage.recent_calls.length > 0 && (
        <div className="card">
          <h3 className="text-sm font-medium text-muted mb-3">Recent API Calls</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-muted border-b border-border">
                  <th className="text-left pb-2 font-medium">Time</th>
                  <th className="text-left pb-2 font-medium">Agent</th>
                  <th className="text-left pb-2 font-medium">Model</th>
                  <th className="text-right pb-2 font-medium">In</th>
                  <th className="text-right pb-2 font-medium">Out</th>
                  <th className="text-right pb-2 font-medium">Cost</th>
                </tr>
              </thead>
              <tbody>
                {[...usage.recent_calls].reverse().map((call, i) => (
                  <tr key={i} className="border-b border-border">
                    <td className="py-2 text-faint text-xs">{formatTime(call.timestamp)}</td>
                    <td className="py-2 text-secondary">{call.agent_name?.replace(/_/g, ' ') || '-'}</td>
                    <td className="py-2 text-faint text-xs">{call.model.split('-').slice(0, 2).join(' ')}</td>
                    <td className="py-2 text-right text-secondary">{formatTokens(call.input_tokens)}</td>
                    <td className="py-2 text-right text-secondary">{formatTokens(call.output_tokens)}</td>
                    <td className="py-2 text-right font-medium text-primary">{formatCost(call.cost)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Monthly projection */}
      <div className="card">
        <h3 className="text-sm font-medium text-muted mb-3">Cost Projections</h3>
        <div className="grid grid-cols-3 gap-4">
          <div className="card-inner text-center">
            <div className="text-faint text-xs mb-1">Daily</div>
            <div className="text-lg font-bold text-primary">{formatCost(usage.estimated_daily_cost)}</div>
          </div>
          <div className="card-inner text-center">
            <div className="text-faint text-xs mb-1">Weekly</div>
            <div className="text-lg font-bold text-primary">{formatCost(usage.estimated_daily_cost * 7)}</div>
          </div>
          <div className="card-inner text-center">
            <div className="text-faint text-xs mb-1">Monthly</div>
            <div className="text-lg font-bold" style={{
              color: usage.estimated_daily_cost * 30 > 100 ? 'var(--loss)' :
                     usage.estimated_daily_cost * 30 > 30 ? '#ca8a04' : 'var(--profit)'
            }}>
              {formatCost(usage.estimated_daily_cost * 30)}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
