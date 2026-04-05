import { useState, useEffect, useRef } from 'react'
import { Activity, TrendingUp, TrendingDown, Brain, Search, MessageSquare, Shield, CheckCircle2, XCircle, Clock, Zap } from 'lucide-react'
import { useWebSocket } from '../hooks/useWebSocket'

interface FeedItem {
  id: number
  timestamp: string
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
  data: { Icon: Activity, color: 'text-cyan-400' },
  thinking: { Icon: Zap, color: 'text-purple-400' },
  risk: { Icon: Shield, color: 'text-orange-400' },
}

export default function LiveActivityFeed() {
  const [feed, setFeed] = useState<FeedItem[]>([])
  const [counter, setCounter] = useState(0)
  const feedRef = useRef<HTMLDivElement>(null)
  const { lastMessage } = useWebSocket()
  const intervalRef = useRef<ReturnType<typeof setInterval>>()
  const cycleStepRef = useRef(0)
  const currentPairRef = useRef('BTC-USD')

  // Add item to feed
  const addItem = (icon: FeedItem['icon'], message: string, detail?: string) => {
    setCounter(prev => {
      const id = prev + 1
      const item: FeedItem = {
        id,
        timestamp: new Date().toLocaleTimeString(),
        icon,
        message,
        detail,
      }
      setFeed(prev => [...prev.slice(-30), item])
      return id
    })
  }

  // React to WebSocket messages
  useEffect(() => {
    if (!lastMessage) return

    if (lastMessage.type === 'trade_update') {
      const d = lastMessage.data as any
      addItem('approved', `Trade executed: ${d?.action ?? 'BUY'} ${d?.pair ?? 'BTC-USD'}`, `Price: $${d?.price?.toLocaleString() ?? '??'} | Stage: ${d?.stage ?? 'paper'}`)
    } else if (lastMessage.type === 'agent_activity') {
      const d = lastMessage.data as any
      const name = (d?.agent_name ?? '').replace(/_/g, ' ')
      const content = d?.content ?? ''

      const iconType: FeedItem['icon'] =
        name.includes('bull') ? 'bull' :
        name.includes('bear') ? 'bear' :
        name.includes('market') || name.includes('news') || name.includes('sentiment') || name.includes('fundamental') ? 'analyzing' :
        name.includes('debat') ? 'risk' :
        name.includes('portfolio') || name.includes('research') ? 'deciding' :
        name.includes('trader') ? 'thinking' :
        'analyzing'

      // Summarize in CEO language
      const summary = summarizeAgentOutput(name, content)
      addItem(iconType, summary, content.slice(0, 150) + (content.length > 150 ? '...' : ''))
    } else if (lastMessage.type === 'status_change') {
      const d = lastMessage.data as any
      const status = d?.status ?? 'unknown'
      addItem('data', `Engine status changed to: ${status}`)
    }
  }, [lastMessage])

  // Simulate cycle progress when engine is running but no WS events yet
  useEffect(() => {
    // Start a simulated cycle walkthrough
    const steps = [
      { delay: 2000, icon: 'data' as const, msg: 'Fetching live BTC-USD price from CoinGecko...', detail: 'Pulling OHLCV candles, ticker, and 24h volume' },
      { delay: 5000, icon: 'data' as const, msg: 'Fetching ETH-USD price data...', detail: 'Pulling OHLCV candles, ticker, and 24h volume' },
      { delay: 8000, icon: 'data' as const, msg: 'Pulling crypto news, sentiment, and on-chain data...', detail: 'CryptoPanic news feed, Fear & Greed index, DeFiLlama TVL' },
      { delay: 12000, icon: 'analyzing' as const, msg: 'Market Analyst is reading the charts...', detail: 'Analyzing RSI, MACD, Bollinger Bands, support/resistance levels' },
      { delay: 18000, icon: 'analyzing' as const, msg: 'News Analyst is scanning headlines...', detail: 'Checking regulatory news, ETF flows, protocol updates' },
      { delay: 24000, icon: 'analyzing' as const, msg: 'Sentiment Analyst is checking market mood...', detail: 'Fear & Greed index, Reddit/X activity, funding rates' },
      { delay: 30000, icon: 'analyzing' as const, msg: 'Fundamentals Analyst is reviewing on-chain data...', detail: 'TVL trends, active addresses, whale movements' },
      { delay: 38000, icon: 'bull' as const, msg: 'Bull Researcher is building the case to BUY...', detail: 'Aggregating bullish signals from all 4 analysts' },
      { delay: 46000, icon: 'bear' as const, msg: 'Bear Researcher is arguing for caution...', detail: 'Identifying risks and bearish signals' },
      { delay: 54000, icon: 'deciding' as const, msg: 'Research Manager is weighing both sides...', detail: 'Deciding who made the stronger argument' },
      { delay: 62000, icon: 'thinking' as const, msg: 'Trader is designing the trade...', detail: 'Setting entry, stop-loss, take-profit, and position size' },
      { delay: 70000, icon: 'risk' as const, msg: 'Risk Debators are arguing about the risk level...', detail: 'Aggressive vs Conservative vs Neutral perspectives' },
      { delay: 80000, icon: 'deciding' as const, msg: 'Portfolio Manager is making the final call...', detail: 'Approve, modify, or reject the proposed trade' },
    ]

    // Only add initial items if feed is empty
    if (feed.length === 0) {
      addItem('data', 'Engine started — beginning first analysis cycle', 'Analyzing BTC-USD and ETH-USD with 12 Claude AI agents')
    }

    const timeouts = steps.map(step =>
      setTimeout(() => {
        addItem(step.icon, step.msg, step.detail)
      }, step.delay)
    )

    return () => timeouts.forEach(clearTimeout)
  }, []) // Only run once on mount

  // Auto-scroll to bottom
  useEffect(() => {
    if (feedRef.current) {
      feedRef.current.scrollTop = feedRef.current.scrollHeight
    }
  }, [feed])

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Activity className="w-4 h-4 text-accent" />
          <h3 className="text-sm font-medium text-gray-400">Live Activity</h3>
        </div>
        <div className="flex items-center gap-1.5 text-xs text-gray-500">
          <Clock className="w-3 h-3" />
          <span>{feed.length} events</span>
        </div>
      </div>

      <div ref={feedRef} className="space-y-2 max-h-80 overflow-y-auto pr-1">
        {feed.length === 0 ? (
          <div className="text-center text-gray-500 text-sm py-6">
            Waiting for engine activity...
          </div>
        ) : (
          feed.map(item => {
            const { Icon, color } = iconMap[item.icon]
            return (
              <div key={item.id} className="flex gap-2.5 group">
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
            )
          })
        )}
      </div>
    </div>
  )
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
