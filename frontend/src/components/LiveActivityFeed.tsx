import { useState, useEffect, useRef } from 'react'
import { Activity, TrendingUp, TrendingDown, Brain, Search, Shield, CheckCircle2, XCircle, Clock, Zap, Database } from 'lucide-react'
import { useWebSocket } from '../hooks/useWebSocket'

type Phase = 'data' | 'analysis' | 'research' | 'action'

interface FeedItem {
  id: number
  timestamp: string
  phase: Phase
  icon: 'analyzing' | 'bull' | 'bear' | 'deciding' | 'approved' | 'rejected' | 'data' | 'thinking' | 'risk'
  message: string
  detail?: string
}

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
  const [feed, setFeed] = useState<FeedItem[]>([])
  const [counter, setCounter] = useState(0)
  const feedRef = useRef<HTMLDivElement>(null)
  const { lastMessage } = useWebSocket()

  const addItem = (phase: Phase, icon: FeedItem['icon'], message: string, detail?: string) => {
    setCounter(prev => {
      const id = prev + 1
      const item: FeedItem = {
        id,
        timestamp: new Date().toLocaleTimeString(),
        phase,
        icon,
        message,
        detail,
      }
      // Prepend (newest first), keep max 40
      setFeed(prev => [item, ...prev].slice(0, 40))
      return id
    })
  }

  // React to WebSocket messages
  useEffect(() => {
    if (!lastMessage) return

    if (lastMessage.type === 'trade_update') {
      const d = lastMessage.data as any
      addItem('action', 'approved', `Trade executed: ${d?.action ?? 'BUY'} ${d?.pair ?? 'BTC-USD'}`, `Price: $${d?.price?.toLocaleString() ?? '??'} | Stage: ${d?.stage ?? 'paper'}`)
    } else if (lastMessage.type === 'agent_activity') {
      const d = lastMessage.data as any
      const name = (d?.agent_name ?? '').replace(/_/g, ' ')
      const content = d?.content ?? ''

      const { phase, icon } = classifyAgent(name)
      const summary = summarizeAgentOutput(name, content)
      addItem(phase, icon, summary, content.slice(0, 150) + (content.length > 150 ? '...' : ''))
    } else if (lastMessage.type === 'status_change') {
      const d = lastMessage.data as any
      addItem('data', 'data', `Engine status: ${d?.status ?? 'unknown'}`)
    }
  }, [lastMessage])

  // Simulate cycle progress on mount
  useEffect(() => {
    if (feed.length > 0) return

    const steps: { delay: number; phase: Phase; icon: FeedItem['icon']; msg: string; detail: string }[] = [
      { delay: 500, phase: 'data', icon: 'data', msg: 'Engine started — beginning first analysis cycle', detail: 'Analyzing BTC-USD and ETH-USD with 12 Claude AI agents' },
      { delay: 2000, phase: 'data', icon: 'data', msg: 'Fetching live BTC-USD price from CoinGecko...', detail: 'Pulling OHLCV candles, ticker, and 24h volume' },
      { delay: 5000, phase: 'data', icon: 'data', msg: 'Fetching ETH-USD price data...', detail: 'Pulling OHLCV candles, ticker, and 24h volume' },
      { delay: 8000, phase: 'data', icon: 'data', msg: 'Pulling crypto news, sentiment, and on-chain data...', detail: 'CryptoPanic news, Fear & Greed index, DeFiLlama TVL' },
      { delay: 12000, phase: 'analysis', icon: 'analyzing', msg: 'Market Analyst is reading the charts...', detail: 'RSI, MACD, Bollinger Bands, support/resistance levels' },
      { delay: 18000, phase: 'analysis', icon: 'analyzing', msg: 'News Analyst is scanning headlines...', detail: 'Regulatory news, ETF flows, protocol updates' },
      { delay: 24000, phase: 'analysis', icon: 'analyzing', msg: 'Sentiment Analyst is checking market mood...', detail: 'Fear & Greed index, Reddit/X activity, funding rates' },
      { delay: 30000, phase: 'analysis', icon: 'analyzing', msg: 'Fundamentals Analyst is reviewing on-chain data...', detail: 'TVL trends, active addresses, whale movements' },
      { delay: 38000, phase: 'research', icon: 'bull', msg: 'Bull Researcher is building the case to BUY...', detail: 'Aggregating bullish signals from all 4 analysts' },
      { delay: 46000, phase: 'research', icon: 'bear', msg: 'Bear Researcher is arguing for caution...', detail: 'Identifying risks and bearish signals' },
      { delay: 54000, phase: 'research', icon: 'deciding', msg: 'Research Manager is weighing both sides...', detail: 'Deciding who made the stronger argument' },
      { delay: 62000, phase: 'action', icon: 'thinking', msg: 'Trader is designing the trade...', detail: 'Setting entry, stop-loss, take-profit, and position size' },
      { delay: 70000, phase: 'action', icon: 'risk', msg: 'Risk Debators are arguing about the risk level...', detail: 'Aggressive vs Conservative vs Neutral perspectives' },
      { delay: 80000, phase: 'action', icon: 'deciding', msg: 'Portfolio Manager is making the final call...', detail: 'Approve, modify, or reject the proposed trade' },
    ]

    const timeouts = steps.map(step =>
      setTimeout(() => addItem(step.phase, step.icon, step.msg, step.detail), step.delay)
    )

    return () => timeouts.forEach(clearTimeout)
  }, [])

  // Scroll to top (newest) when new items added
  useEffect(() => {
    if (feedRef.current) {
      feedRef.current.scrollTop = 0
    }
  }, [feed])

  // Group consecutive items by phase for visual separation
  let lastPhase: Phase | null = null

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Activity className="w-4 h-4 text-accent" />
          <h3 className="text-sm font-medium text-gray-400">Live Activity</h3>
        </div>
        <div className="flex items-center gap-3">
          {/* Phase legend */}
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
            const showPhaseHeader = item.phase !== feed[idx - 1]?.phase

            return (
              <div key={item.id}>
                {/* Phase divider when phase changes */}
                {(idx === 0 || showPhaseHeader) && (
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

function classifyAgent(name: string): { phase: Phase; icon: FeedItem['icon'] } {
  const n = name.toLowerCase()
  if (n.includes('market') || n.includes('news') || n.includes('sentiment') || n.includes('fundamental'))
    return { phase: 'analysis', icon: 'analyzing' }
  if (n.includes('bull'))
    return { phase: 'research', icon: 'bull' }
  if (n.includes('bear'))
    return { phase: 'research', icon: 'bear' }
  if (n.includes('research'))
    return { phase: 'research', icon: 'deciding' }
  if (n.includes('trader'))
    return { phase: 'action', icon: 'thinking' }
  if (n.includes('aggressive') || n.includes('conservative') || n.includes('neutral') || n.includes('debat'))
    return { phase: 'action', icon: 'risk' }
  if (n.includes('portfolio'))
    return { phase: 'action', icon: 'deciding' }
  return { phase: 'data', icon: 'data' }
}

function summarizeAgentOutput(agentName: string, content: string): string {
  const name = agentName.toLowerCase()

  if (name.includes('market analyst')) {
    if (content.toLowerCase().includes('bullish')) return 'Market Analyst sees bullish technical signals'
    if (content.toLowerCase().includes('bearish')) return 'Market Analyst sees bearish technical signals'
    return 'Market Analyst completed technical analysis'
  }
  if (name.includes('news analyst')) return 'News Analyst finished scanning crypto headlines'
  if (name.includes('sentiment analyst')) return 'Sentiment Analyst checked market mood'
  if (name.includes('fundamentals analyst')) return 'Fundamentals Analyst reviewed on-chain metrics'
  if (name.includes('bull researcher')) return 'Bull Researcher built the case for buying'
  if (name.includes('bear researcher')) return 'Bear Researcher built the case for caution'
  if (name.includes('research manager')) {
    if (content.toLowerCase().includes('buy')) return 'Research Manager verdict: lean towards BUYING'
    if (content.toLowerCase().includes('sell')) return 'Research Manager verdict: lean towards SELLING'
    return 'Research Manager reached a consensus verdict'
  }
  if (name.includes('trader')) return 'Trader designed a specific trade proposal'
  if (name.includes('aggressive')) return 'Aggressive Risk Analyst: argues for bigger position'
  if (name.includes('conservative')) return 'Conservative Risk Analyst: argues for smaller position'
  if (name.includes('neutral')) return 'Neutral Risk Analyst: found the middle ground'
  if (name.includes('portfolio manager')) {
    if (content.toLowerCase().includes('approved') || content.toLowerCase().includes('"approved": true')) return 'Portfolio Manager APPROVED the trade!'
    if (content.toLowerCase().includes('reject') || content.toLowerCase().includes('"approved": false')) return 'Portfolio Manager REJECTED the trade'
    return 'Portfolio Manager made the final decision'
  }

  return `${agentName} completed analysis`
}
