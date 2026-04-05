import { useAgentLogs } from '../hooks/useApi'

const agentColors: Record<string, string> = {
  market_analyst: 'text-blue-600',
  news_analyst: 'text-purple-600',
  sentiment_analyst: 'text-pink-600',
  fundamentals_analyst: 'text-cyan-600',
  bull_researcher: 'text-profit',
  bear_researcher: 'text-loss',
  research_manager: 'text-yellow-600',
  trader: 'text-accent',
  aggressive_debator: 'text-orange-600',
  conservative_debator: 'text-teal-600',
  neutral_debator: 'text-secondary',
  portfolio_manager: 'text-indigo-600',
}

const agentLabels: Record<string, string> = {
  market_analyst: 'Market Analyst',
  news_analyst: 'News Analyst',
  sentiment_analyst: 'Sentiment Analyst',
  fundamentals_analyst: 'Fundamentals Analyst',
  bull_researcher: 'Bull Researcher',
  bear_researcher: 'Bear Researcher',
  research_manager: 'Research Manager',
  trader: 'Trader',
  aggressive_debator: 'Aggressive Risk',
  conservative_debator: 'Conservative Risk',
  neutral_debator: 'Neutral Risk',
  portfolio_manager: 'Portfolio Manager',
}

interface Props {
  cycleId: string
}

export default function AgentReasoningPanel({ cycleId }: Props) {
  const { data, isLoading } = useAgentLogs({ cycle_id: cycleId })

  if (isLoading) return <div className="text-muted text-sm">Loading agent reasoning...</div>

  const logs = data?.logs ?? []
  if (!logs.length) return <div className="text-muted text-sm">No agent logs for this cycle.</div>

  return (
    <div className="space-y-3">
      <h4 className="text-sm font-medium text-muted">Agent Reasoning Chain</h4>
      {logs.map((log) => (
        <div key={log.id} className="card-inner">
          <div className={`text-xs font-semibold mb-1.5 ${agentColors[log.agent_name] || 'text-muted'}`}>
            {agentLabels[log.agent_name] || log.agent_name}
          </div>
          <div className="text-sm text-secondary whitespace-pre-wrap leading-relaxed">
            {log.content.length > 500 ? log.content.slice(0, 500) + '...' : log.content}
          </div>
        </div>
      ))}
    </div>
  )
}
