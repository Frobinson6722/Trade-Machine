import { useLearningData } from '../hooks/useApi'
import LearningTimeline from '../components/LearningTimeline'
import { GraduationCap } from 'lucide-react'

export default function LearningPage() {
  const { data, isLoading } = useLearningData()

  if (isLoading) {
    return <div className="text-gray-500">Loading learning data...</div>
  }

  const reflections = data?.reflections ?? []
  const strategyUpdates = data?.strategy_updates ?? []
  const hypotheses = data?.hypotheses ?? []
  const params = data?.current_parameters ?? {}

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <GraduationCap className="w-6 h-6 text-accent" />
        <h2 className="text-2xl font-bold">Learning Log</h2>
      </div>

      {/* Stats summary */}
      <div className="grid grid-cols-3 gap-4">
        <div className="card text-center">
          <div className="text-2xl font-bold text-purple-400">{reflections.length}</div>
          <div className="text-xs text-gray-500">Reflections</div>
        </div>
        <div className="card text-center">
          <div className="text-2xl font-bold text-yellow-400">
            {hypotheses.filter((h) => h.status === 'validated').length}
          </div>
          <div className="text-xs text-gray-500">Validated Hypotheses</div>
        </div>
        <div className="card text-center">
          <div className="text-2xl font-bold text-accent">{strategyUpdates.length}</div>
          <div className="text-xs text-gray-500">Strategy Updates</div>
        </div>
      </div>

      {/* Current strategy parameters */}
      {Object.keys(params).length > 0 && (
        <div className="card">
          <h3 className="text-sm font-medium text-gray-400 mb-3">Current Strategy Parameters</h3>
          <div className="grid grid-cols-2 lg:grid-cols-3 gap-2">
            {Object.entries(params).map(([key, value]) => (
              <div key={key} className="flex justify-between text-sm">
                <span className="text-gray-500">{key.replace(/_/g, ' ')}</span>
                <span className="text-gray-300 font-mono">{String(value)}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Timeline */}
      <div>
        <h3 className="text-lg font-medium mb-3">Learning Timeline</h3>
        <LearningTimeline
          reflections={reflections}
          strategyUpdates={strategyUpdates}
          hypotheses={hypotheses}
        />
      </div>
    </div>
  )
}
