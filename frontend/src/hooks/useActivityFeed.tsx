import { createContext, useContext, useState, useCallback, useEffect, ReactNode } from 'react'
import { useWebSocket } from './useWebSocket'

type Phase = 'data' | 'analysis' | 'research' | 'action'

export interface FeedItem {
  id: number
  timestamp: string
  phase: Phase
  icon: 'analyzing' | 'bull' | 'bear' | 'deciding' | 'approved' | 'rejected' | 'data' | 'thinking' | 'risk'
  message: string
  detail?: string
}

interface ActivityCounts {
  trades: number
  agents: number
  learning: number
}

interface ActivityContextValue {
  feed: FeedItem[]
  counts: ActivityCounts
  clearCount: (key: keyof ActivityCounts) => void
}

const ActivityContext = createContext<ActivityContextValue>({
  feed: [],
  counts: { trades: 0, agents: 0, learning: 0 },
  clearCount: () => {},
})

export function useActivityFeed() {
  return useContext(ActivityContext)
}

let globalId = 0

export function ActivityProvider({ children }: { children: ReactNode }) {
  const [feed, setFeed] = useState<FeedItem[]>([])
  const [counts, setCounts] = useState<ActivityCounts>({ trades: 0, agents: 0, learning: 0 })
  const { lastMessage } = useWebSocket()
  const [initialized, setInitialized] = useState(false)

  const addItem = useCallback((phase: Phase, icon: FeedItem['icon'], message: string, detail?: string) => {
    globalId++
    const item: FeedItem = {
      id: globalId,
      timestamp: new Date().toLocaleTimeString(),
      phase,
      icon,
      message,
      detail,
    }
    setFeed(prev => [item, ...prev].slice(0, 50))
  }, [])

  const clearCount = useCallback((key: keyof ActivityCounts) => {
    setCounts(prev => ({ ...prev, [key]: 0 }))
  }, [])

  // React to WebSocket messages
  useEffect(() => {
    if (!lastMessage) return

    if (lastMessage.type === 'trade_update') {
      const d = lastMessage.data as any
      addItem('action', 'approved', `Trade executed: ${d?.action ?? 'BUY'} ${d?.pair ?? 'BTC-USD'}`, `Price: $${d?.price?.toLocaleString() ?? '??'} | Stage: ${d?.stage ?? 'paper'}`)
      setCounts(prev => ({ ...prev, trades: prev.trades + 1 }))
    } else if (lastMessage.type === 'agent_activity') {
      const d = lastMessage.data as any
      const name = (d?.agent_name ?? '').replace(/_/g, ' ')
      const content = d?.content ?? ''
      const { phase, icon } = classifyAgent(name)
      const summary = summarizeAgentOutput(name, content)
      addItem(phase, icon, summary, content.slice(0, 150) + (content.length > 150 ? '...' : ''))
      setCounts(prev => ({ ...prev, agents: prev.agents + 1 }))

      // Reflections count toward learning
      if (name.includes('reflect') || name.includes('hypothesis') || name.includes('nightly')) {
        setCounts(prev => ({ ...prev, learning: prev.learning + 1 }))
      }
    } else if (lastMessage.type === 'status_change') {
      const d = lastMessage.data as any
      addItem('data', 'data', `Engine status: ${d?.status ?? 'unknown'}`)
    }
  }, [lastMessage, addItem])

  // Simulated cycle walkthrough on first engine start
  useEffect(() => {
    if (initialized) return

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

    setInitialized(true)
    const timeouts = steps.map(step =>
      setTimeout(() => addItem(step.phase, step.icon, step.msg, step.detail), step.delay)
    )
    return () => timeouts.forEach(clearTimeout)
  }, [initialized, addItem])

  return (
    <ActivityContext.Provider value={{ feed, counts, clearCount }}>
      {children}
    </ActivityContext.Provider>
  )
}

function classifyAgent(name: string): { phase: Phase; icon: FeedItem['icon'] } {
  const n = name.toLowerCase()
  if (n.includes('market') || n.includes('news') || n.includes('sentiment') || n.includes('fundamental'))
    return { phase: 'analysis', icon: 'analyzing' }
  if (n.includes('bull')) return { phase: 'research', icon: 'bull' }
  if (n.includes('bear')) return { phase: 'research', icon: 'bear' }
  if (n.includes('research')) return { phase: 'research', icon: 'deciding' }
  if (n.includes('trader')) return { phase: 'action', icon: 'thinking' }
  if (n.includes('aggressive') || n.includes('conservative') || n.includes('neutral') || n.includes('debat'))
    return { phase: 'action', icon: 'risk' }
  if (n.includes('portfolio')) return { phase: 'action', icon: 'deciding' }
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
