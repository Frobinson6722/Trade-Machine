import { Brain, Lightbulb, Settings } from 'lucide-react'
import type { Reflection, StrategyUpdate, Hypothesis } from '../lib/types'

interface Props {
  reflections: Reflection[]
  strategyUpdates: StrategyUpdate[]
  hypotheses: Hypothesis[]
}

type TimelineItem = {
  type: 'reflection' | 'strategy' | 'hypothesis'
  timestamp: string
  data: Reflection | StrategyUpdate | Hypothesis
}

export default function LearningTimeline({ reflections, strategyUpdates, hypotheses }: Props) {
  // Merge all items into a sorted timeline
  const items: TimelineItem[] = [
    ...reflections.map((r) => ({ type: 'reflection' as const, timestamp: r.created_at, data: r })),
    ...strategyUpdates.map((s) => ({ type: 'strategy' as const, timestamp: s.created_at, data: s })),
    ...hypotheses.map((h) => ({ type: 'hypothesis' as const, timestamp: h.created_at, data: h })),
  ].sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())

  if (!items.length) {
    return (
      <div className="card text-center text-gray-500 py-8">
        No learning data yet. The system will start learning from trades.
      </div>
    )
  }

  return (
    <div className="space-y-3">
      {items.map((item, i) => (
        <div key={`${item.type}-${i}`} className="card flex gap-3">
          <div className="mt-1">
            {item.type === 'reflection' && <Brain className="w-5 h-5 text-purple-400" />}
            {item.type === 'strategy' && <Settings className="w-5 h-5 text-accent" />}
            {item.type === 'hypothesis' && <Lightbulb className="w-5 h-5 text-yellow-400" />}
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <span className="text-xs font-medium uppercase tracking-wide text-gray-500">
                {item.type}
              </span>
              {item.type === 'reflection' && (
                <span className={`text-xs px-1.5 py-0.5 rounded ${
                  (item.data as Reflection).trade_outcome === 'win'
                    ? 'bg-green-500/20 text-green-400'
                    : 'bg-red-500/20 text-red-400'
                }`}>
                  {(item.data as Reflection).trade_outcome}
                </span>
              )}
              {item.type === 'hypothesis' && (
                <span className={`text-xs px-1.5 py-0.5 rounded ${
                  (item.data as Hypothesis).status === 'validated'
                    ? 'bg-green-500/20 text-green-400'
                    : (item.data as Hypothesis).status === 'rejected'
                    ? 'bg-red-500/20 text-red-400'
                    : 'bg-yellow-500/20 text-yellow-400'
                }`}>
                  {(item.data as Hypothesis).status}
                </span>
              )}
              <span className="text-xs text-gray-600 ml-auto">
                {new Date(item.timestamp).toLocaleString()}
              </span>
            </div>
            <div className="text-sm text-gray-300">
              {item.type === 'reflection' && (item.data as Reflection).reflection_text}
              {item.type === 'strategy' && (
                <>
                  <span className="font-medium">{(item.data as StrategyUpdate).description}</span>
                  <div className="text-xs text-gray-500 mt-1">
                    Changes: {JSON.stringify((item.data as StrategyUpdate).parameter_changes)}
                  </div>
                </>
              )}
              {item.type === 'hypothesis' && (item.data as Hypothesis).hypothesis}
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}
