import { useState } from 'react'
import { useAgentLogs } from '../hooks/useApi'
import { Brain } from 'lucide-react'

const agentTypes = [
  { value: '', label: 'All Agents' },
  { value: 'market_analyst', label: 'Market Analyst' },
  { value: 'news_analyst', label: 'News Analyst' },
  { value: 'sentiment_analyst', label: 'Sentiment Analyst' },
  { value: 'fundamentals_analyst', label: 'Fundamentals Analyst' },
  { value: 'bull_researcher', label: 'Bull Researcher' },
  { value: 'bear_researcher', label: 'Bear Researcher' },
  { value: 'research_manager', label: 'Research Manager' },
  { value: 'trader', label: 'Trader' },
  { value: 'aggressive_debator', label: 'Aggressive Risk' },
  { value: 'conservative_debator', label: 'Conservative Risk' },
  { value: 'neutral_debator', label: 'Neutral Risk' },
  { value: 'portfolio_manager', label: 'Portfolio Manager' },
]

export default function AgentsPage() {
  const [agentFilter, setAgentFilter] = useState('')
  const [cycleFilter, setCycleFilter] = useState('')
  const { data, isLoading } = useAgentLogs({
    agent_name: agentFilter || undefined,
    cycle_id: cycleFilter || undefined,
    limit: 50,
  })
  const logs = data?.logs ?? []

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Brain className="w-6 h-6 text-accent" />
        <h2 className="text-2xl font-bold text-primary">Agent Reasoning</h2>
      </div>

      <div className="flex gap-3">
        <select className="input" value={agentFilter} onChange={(e) => setAgentFilter(e.target.value)}>
          {agentTypes.map((t) => (
            <option key={t.value} value={t.value}>{t.label}</option>
          ))}
        </select>
        <input className="input" placeholder="Filter by cycle ID..." value={cycleFilter}
          onChange={(e) => setCycleFilter(e.target.value)} />
      </div>

      {isLoading ? (
        <div className="text-muted">Loading agent logs...</div>
      ) : !logs.length ? (
        <div className="card text-center text-muted py-8">
          No agent logs yet. Start a trading session to see agent reasoning.
        </div>
      ) : (
        <div className="space-y-3">
          {logs.map((log) => (
            <div key={log.id} className="card">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-surface-tertiary text-secondary">
                    {log.agent_name.replace(/_/g, ' ')}
                  </span>
                  <span className="text-xs text-faint">Cycle: {log.cycle_id}</span>
                </div>
                <span className="text-xs text-faint">{new Date(log.created_at).toLocaleString()}</span>
              </div>
              <div className="text-sm text-secondary whitespace-pre-wrap leading-relaxed">{log.content}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
