import { Brain, Lightbulb, Settings } from 'lucide-react'
import type { Reflection, StrategyUpdate, Hypothesis } from '../lib/types'
import { formatTime } from '../lib/time'

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
  const items: TimelineItem[] = [
    ...reflections.map((r) => ({ type: 'reflection' as const, timestamp: r.created_at, data: r })),
    ...strategyUpdates.map((s) => ({ type: 'strategy' as const, timestamp: s.created_at, data: s })),
    ...hypotheses.map((h) => ({ type: 'hypothesis' as const, timestamp: h.created_at, data: h })),
  ].sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())

  if (!items.length) {
    return (
      <div className="card text-center text-muted py-8">
        No learning data yet. The system will start learning from trades.
      </div>
    )
  }

  return (
    <div className="space-y-3">
      {items.map((item, i) => (
        <div key={`${item.type}-${i}`} className="card flex gap-3">
          <div className="mt-1">
            {item.type === 'reflection' && <Brain className="w-5 h-5 text-purple-600" />}
            {item.type === 'strategy' && <Settings className="w-5 h-5 text-accent" />}
            {item.type === 'hypothesis' && <Lightbulb className="w-5 h-5 text-yellow-600" />}
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <span className="text-xs font-semibold uppercase tracking-wide text-faint">{item.type}</span>
              {item.type === 'reflection' && (
                <span className={`text-xs px-1.5 py-0.5 rounded-full font-medium ${
                  (item.data as Reflection).trade_outcome === 'win'
                    ? 'bg-green-500/15 text-green-700' : 'bg-red-500/15 text-red-700'
                }`}>
                  {(item.data as Reflection).trade_outcome}
                </span>
              )}
              {item.type === 'hypothesis' && (
                <span className={`text-xs px-1.5 py-0.5 rounded-full font-medium ${
                  (item.data as Hypothesis).status === 'validated' ? 'bg-green-500/15 text-green-700' :
                  (item.data as Hypothesis).status === 'rejected' ? 'bg-red-500/15 text-red-700' :
                  'bg-yellow-500/15 text-yellow-700'
                }`}>
                  {(item.data as Hypothesis).status}
                </span>
              )}
              <span className="text-xs text-faint ml-auto">{formatTime(item.timestamp)}</span>
            </div>
            <div className="text-sm text-secondary leading-relaxed">
              {item.type === 'reflection' && (item.data as Reflection).reflection_text}
              {item.type === 'strategy' && (
                <>
                  <span className="font-medium text-primary">{(item.data as StrategyUpdate).description}</span>
                  <div className="text-xs text-muted mt-1">
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
