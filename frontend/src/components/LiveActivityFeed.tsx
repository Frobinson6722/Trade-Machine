import { useRef, useEffect } from 'react'
import { Activity, TrendingUp, TrendingDown, Brain, Search, Shield, CheckCircle2, XCircle, Clock, Zap, Database } from 'lucide-react'
import { useActivityFeed } from '../hooks/useActivityFeed'

const iconMap = {
  analyzing: { Icon: Search, color: 'text-blue-400' },
  bull: { Icon: TrendingUp, color: 'text-green-400' },
  bear: { Icon: TrendingDown, color: 'text-red-400' },
  deciding: { Icon: Brain, color: 'text-yellow-400' },
  approved: { Icon: CheckCircle2, color: 'text-green-400' },
  rejected: { Icon: XCircle, color: 'text-gray-400' },
  data: { Icon: Database, color: 'text-cyan-400' },
  thinking: { Icon: Zap, color: 'text-purple-400' },
  risk: { Icon: Shield, color: 'text-orange-400' },
}

const phaseConfig = {
  data: { label: 'DATA', color: 'bg-cyan-500/15 text-cyan-400 border-cyan-500/30' },
  analysis: { label: 'ANALYSIS', color: 'bg-blue-500/15 text-blue-400 border-blue-500/30' },
  research: { label: 'RESEARCH', color: 'bg-yellow-500/15 text-yellow-400 border-yellow-500/30' },
  action: { label: 'ACTION', color: 'bg-green-500/15 text-green-400 border-green-500/30' },
}

export default function LiveActivityFeed() {
  const { feed } = useActivityFeed()
  const feedRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (feedRef.current) feedRef.current.scrollTop = 0
  }, [feed])

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Activity className="w-4 h-4 text-accent" />
          <h3 className="text-sm font-medium text-gray-400">Live Activity</h3>
        </div>
        <div className="flex items-center gap-3">
          <div className="hidden sm:flex items-center gap-2">
            {Object.entries(phaseConfig).map(([key, cfg]) => (
              <span key={key} className={`text-[9px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded border ${cfg.color}`}>
                {cfg.label}
              </span>
            ))}
          </div>
          <div className="flex items-center gap-1.5 text-xs text-gray-500">
            <Clock className="w-3 h-3" />
            <span>{feed.length}</span>
          </div>
        </div>
      </div>

      <div ref={feedRef} className="space-y-0.5 max-h-96 overflow-y-auto pr-1">
        {feed.length === 0 ? (
          <div className="text-center text-gray-500 text-sm py-6">
            Waiting for engine activity...
          </div>
        ) : (
          feed.map((item, idx) => {
            const { Icon, color } = iconMap[item.icon]
            const phase = phaseConfig[item.phase]
            const showPhaseHeader = idx === 0 || item.phase !== feed[idx - 1]?.phase

            return (
              <div key={item.id}>
                {showPhaseHeader && (
                  <div className="flex items-center gap-2 pt-2 pb-1">
                    <span className={`text-[9px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded border ${phase.color}`}>
                      {phase.label}
                    </span>
                    <div className="flex-1 border-t border-gray-800" />
                  </div>
                )}
                <div className="flex gap-2.5 py-1.5 px-2 rounded hover:bg-gray-800/30 transition-colors">
                  <div className="mt-0.5 shrink-0">
                    <Icon className={`w-4 h-4 ${color}`} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-baseline gap-2">
                      <span className="text-sm text-gray-200">{item.message}</span>
                      <span className="text-[10px] text-gray-600 shrink-0">{item.timestamp}</span>
                    </div>
                    {item.detail && (
                      <p className="text-xs text-gray-500 mt-0.5 leading-relaxed">{item.detail}</p>
                    )}
                  </div>
                </div>
              </div>
            )
          })
        )}
      </div>
    </div>
  )
}
