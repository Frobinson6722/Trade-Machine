import { useAgentLogs } from '../hooks/useApi'

const agentColors: Record<string, string> = {
  market_analyst: 'text-blue-400',
  news_analyst: 'text-purple-400',
  sentiment_analyst: 'text-pink-400',
  fundamentals_analyst: 'text-cyan-400',
  bull_researcher: 'text-profit',
  bear_researcher: 'text-loss',
  research_manager: 'text-yellow-400',
  trader: 'text-accent',
  aggressive_debator: 'text-orange-400',
  conservative_debator: 'text-teal-400',
  neutral_debator: 'text-gray-300',
  portfolio_manager: 'text-indigo-400',
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

  if (isLoading) {
    return <div className="text-gray-500 text-sm">Loading agent reasoning...</div>
  }

  const logs = data?.logs ?? []

  if (!logs.length) {
    return <div className="text-gray-500 text-sm">No agent logs for this cycle.</div>
  }

  return (
    <div className="space-y-3">
      <h4 className="text-sm font-medium text-gray-400">Agent Reasoning Chain</h4>
      {logs.map((log) => (
        <div key={log.id} className="bg-gray-900 rounded-lg p-3 border border-gray-800">
          <div className={`text-xs font-medium mb-1 ${agentColors[log.agent_name] || 'text-gray-400'}`}>
            {agentLabels[log.agent_name] || log.agent_name}
          </div>
          <div className="text-sm text-gray-300 whitespace-pre-wrap leading-relaxed">
            {log.content.length > 500 ? log.content.slice(0, 500) + '...' : log.content}
          </div>
        </div>
      ))}
    </div>
  )
}
