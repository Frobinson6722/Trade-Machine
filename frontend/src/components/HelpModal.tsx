import { useState, ReactNode } from 'react'
import { HelpCircle, X, Zap, BarChart3, Brain, GraduationCap, Settings, ArrowRight, Play, Square, Pause, TrendingUp, TrendingDown, Target, ChevronDown, AlertTriangle, Lightbulb, CheckCircle2 } from 'lucide-react'

/* ── Mini mockup components ─────────────────────────────────── */

function MockPnLCards() {
  return (
    <div className="grid grid-cols-4 gap-2 text-xs">
      <div className="bg-gray-800 rounded p-2">
        <div className="text-gray-500 flex items-center gap-1"><TrendingUp className="w-3 h-3 text-green-400" /> Total P&L</div>
        <div className="text-green-400 font-bold text-sm mt-0.5">+$342.18</div>
      </div>
      <div className="bg-gray-800 rounded p-2">
        <div className="text-gray-500 flex items-center gap-1"><Target className="w-3 h-3" /> Win Rate</div>
        <div className="text-green-400 font-bold text-sm mt-0.5">58.3%</div>
      </div>
      <div className="bg-gray-800 rounded p-2">
        <div className="text-gray-500 flex items-center gap-1"><BarChart3 className="w-3 h-3" /> Trades</div>
        <div className="font-bold text-sm mt-0.5">24</div>
      </div>
      <div className="bg-gray-800 rounded p-2">
        <div className="text-gray-500 flex items-center gap-1"><TrendingUp className="w-3 h-3 text-green-400" /> Avg P&L</div>
        <div className="text-green-400 font-bold text-sm mt-0.5">+$14.26</div>
      </div>
    </div>
  )
}

function MockEquityCurve() {
  return (
    <div className="bg-gray-800 rounded p-3">
      <div className="text-xs text-gray-500 mb-2">Equity Curve</div>
      <svg viewBox="0 0 200 60" className="w-full h-12">
        <defs>
          <linearGradient id="mockGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#22c55e" stopOpacity="0.3" />
            <stop offset="100%" stopColor="#22c55e" stopOpacity="0" />
          </linearGradient>
        </defs>
        <path d="M0,50 L20,48 L40,45 L60,42 L80,38 L100,40 L120,35 L140,30 L160,25 L180,22 L200,15" stroke="#22c55e" strokeWidth="2" fill="none" />
        <path d="M0,50 L20,48 L40,45 L60,42 L80,38 L100,40 L120,35 L140,30 L160,25 L180,22 L200,15 L200,60 L0,60Z" fill="url(#mockGrad)" />
      </svg>
      <div className="flex justify-between text-[10px] text-gray-600 mt-1">
        <span>Apr 1</span><span>Apr 2</span><span>Apr 3</span><span>Apr 4</span><span>Apr 5</span>
      </div>
    </div>
  )
}

function MockTradeRow({ pair, side, pnl, expanded }: { pair: string; side: string; pnl: number; expanded?: boolean }) {
  return (
    <div className="bg-gray-800 rounded">
      <div className="flex items-center gap-3 px-3 py-2 text-xs">
        <ChevronDown className={`w-3 h-3 text-gray-500 ${expanded ? '' : '-rotate-90'}`} />
        <span className="font-medium">{pair}</span>
        <span className={side === 'BUY' ? 'text-green-400' : 'text-red-400'}>{side}</span>
        <span className="ml-auto font-medium">{pnl >= 0 ? <span className="text-green-400">+${pnl.toFixed(2)}</span> : <span className="text-red-400">-${Math.abs(pnl).toFixed(2)}</span>}</span>
      </div>
      {expanded && (
        <div className="px-3 pb-2 border-t border-gray-700 pt-2 space-y-1">
          <div className="text-[10px] text-blue-400 font-medium">Market Analyst</div>
          <div className="text-[10px] text-gray-400">RSI at 68, MACD bullish crossover, testing $85k resistance...</div>
          <div className="text-[10px] text-green-400 font-medium mt-1">Bull Researcher</div>
          <div className="text-[10px] text-gray-400">Strong momentum with ETF inflows supporting price...</div>
          <div className="text-[10px] text-red-400 font-medium mt-1">Bear Researcher</div>
          <div className="text-[10px] text-gray-400">Overbought conditions, potential resistance at $86k...</div>
        </div>
      )}
    </div>
  )
}

function MockAgentLog() {
  return (
    <div className="space-y-2">
      <div className="bg-gray-800 rounded p-2">
        <div className="text-[10px] text-blue-400 font-medium mb-1">Market Analyst</div>
        <div className="text-[10px] text-gray-400 leading-relaxed">BTC showing bullish momentum. RSI: 65 (neutral-bullish). MACD just crossed bullish. Volume 15% above 20-day average. Key resistance at $86,200.</div>
      </div>
      <div className="bg-gray-800 rounded p-2">
        <div className="text-[10px] text-purple-400 font-medium mb-1">News Analyst</div>
        <div className="text-[10px] text-gray-400 leading-relaxed">Positive: SEC approved new BTC ETF options. Neutral: Fed holding rates steady. No negative regulatory news in last 24h.</div>
      </div>
      <div className="bg-gray-800 rounded p-2">
        <div className="text-[10px] text-pink-400 font-medium mb-1">Sentiment Analyst</div>
        <div className="text-[10px] text-gray-400 leading-relaxed">Fear & Greed: 72 (Greed). Reddit sentiment improving. Twitter mentions up 23%. Contrarian caution: approaching extreme greed.</div>
      </div>
    </div>
  )
}

function MockLearningTimeline() {
  return (
    <div className="space-y-2">
      <div className="bg-gray-800 rounded p-2 flex gap-2">
        <Brain className="w-4 h-4 text-purple-400 shrink-0 mt-0.5" />
        <div>
          <div className="flex items-center gap-2">
            <span className="text-[10px] text-gray-500 uppercase">Reflection</span>
            <span className="text-[10px] px-1 rounded bg-red-500/20 text-red-400">loss</span>
          </div>
          <div className="text-[10px] text-gray-400 mt-0.5">RSI was at 72 but volume was declining — should have weighted volume divergence more heavily before entering.</div>
        </div>
      </div>
      <div className="bg-gray-800 rounded p-2 flex gap-2">
        <Lightbulb className="w-4 h-4 text-yellow-400 shrink-0 mt-0.5" />
        <div>
          <div className="flex items-center gap-2">
            <span className="text-[10px] text-gray-500 uppercase">Hypothesis</span>
            <span className="text-[10px] px-1 rounded bg-green-500/20 text-green-400">validated</span>
          </div>
          <div className="text-[10px] text-gray-400 mt-0.5">When RSI &gt; 70 AND volume is declining, short-term pullback occurs 73% of the time.</div>
        </div>
      </div>
      <div className="bg-gray-800 rounded p-2 flex gap-2">
        <Settings className="w-4 h-4 text-accent shrink-0 mt-0.5" />
        <div>
          <div className="flex items-center gap-2">
            <span className="text-[10px] text-gray-500 uppercase">Strategy Update</span>
          </div>
          <div className="text-[10px] text-gray-400 mt-0.5">Added rule: Skip BUY when RSI &gt; 70 and volume ratio &lt; 0.8</div>
        </div>
      </div>
    </div>
  )
}

function MockStages() {
  return (
    <div className="space-y-2">
      {[
        { name: 'Stage 1: Paper', desc: '$10,000 fake money', rule: 'Win >55% of 100+ trades', status: 'current', color: 'border-accent' },
        { name: 'Stage 2: Micro', desc: '$1 real trades', rule: 'Stay profitable over 1,000 trades', status: 'locked', color: 'border-gray-700' },
        { name: 'Stage 3: Graduated', desc: '$2 → $5 → $10', rule: 'Scale only if consistently profitable', status: 'locked', color: 'border-gray-700' },
      ].map((s, i) => (
        <div key={i} className={`rounded p-2 border ${s.color} ${s.status === 'current' ? 'bg-accent/5' : 'bg-gray-800/50'}`}>
          <div className="flex items-center justify-between">
            <div>
              <div className="text-xs font-medium">{s.name}</div>
              <div className="text-[10px] text-gray-500">{s.desc}</div>
            </div>
            <div className="text-right">
              <div className="text-[10px] text-gray-400">{s.rule}</div>
              {s.status === 'current' ? (
                <div className="text-[10px] text-accent font-medium">Active now</div>
              ) : (
                <div className="text-[10px] text-gray-600">Locked</div>
              )}
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}

function MockAgentPipeline() {
  const stages = [
    { agents: ['Market', 'News', 'Sentiment', 'Fundamentals'], label: 'Analysts gather data', color: 'bg-blue-500/20 text-blue-400' },
    { agents: ['Bull', 'Bear'], label: 'Researchers debate', color: 'bg-green-500/20 text-green-400' },
    { agents: ['Research Mgr'], label: 'Picks the winner', color: 'bg-yellow-500/20 text-yellow-400' },
    { agents: ['Trader'], label: 'Proposes a trade', color: 'bg-accent/20 text-accent' },
    { agents: ['Aggressive', 'Conservative', 'Neutral'], label: 'Risk debate', color: 'bg-orange-500/20 text-orange-400' },
    { agents: ['Portfolio Mgr'], label: 'Final decision', color: 'bg-indigo-500/20 text-indigo-400' },
  ]
  return (
    <div className="space-y-1.5">
      {stages.map((s, i) => (
        <div key={i} className="flex items-center gap-2">
          <div className="w-5 text-center text-[10px] text-gray-600 font-mono">{i + 1}</div>
          <div className={`flex-1 rounded px-2 py-1.5 ${s.color}`}>
            <div className="flex items-center gap-1.5 flex-wrap">
              {s.agents.map((a, j) => (
                <span key={j} className="text-[10px] font-medium">{a}</span>
              ))}
              {s.agents.length > 1 && <span className="text-[10px] opacity-50">×{s.agents.length}</span>}
            </div>
            <div className="text-[10px] opacity-70 mt-0.5">{s.label}</div>
          </div>
          {i < stages.length - 1 && <ArrowRight className="w-3 h-3 text-gray-600 shrink-0" />}
        </div>
      ))}
    </div>
  )
}

function MockControlBar() {
  return (
    <div className="bg-gray-800 rounded p-3 space-y-2">
      <div className="flex items-center justify-between">
        <div>
          <div className="text-xs font-medium">Dashboard</div>
          <div className="text-[10px] text-gray-500">Stage: paper | Mode: paper</div>
        </div>
        <div className="flex gap-1.5">
          <button className="bg-blue-500 text-white text-[10px] px-2 py-1 rounded flex items-center gap-1">
            <Play className="w-2.5 h-2.5" /> Start Paper Trading
          </button>
        </div>
      </div>
      <div className="flex items-center gap-2 px-2 py-1.5 bg-green-500/10 border border-green-500/30 rounded text-[10px] text-green-400">
        <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
        Engine is running — analyzing BTC & ETH with Claude AI agents
      </div>
    </div>
  )
}

function MockSettingsCard() {
  return (
    <div className="bg-gray-800 rounded p-3 space-y-2">
      <div>
        <div className="text-[10px] text-gray-500 mb-0.5">Claude Model</div>
        <div className="bg-gray-900 rounded px-2 py-1 text-[10px] border border-gray-700">Claude Sonnet 4 (recommended)</div>
      </div>
      <div className="grid grid-cols-2 gap-2">
        <div>
          <div className="text-[10px] text-gray-500 mb-0.5">Trading Pairs</div>
          <div className="bg-gray-900 rounded px-2 py-1 text-[10px] border border-gray-700">BTC-USD, ETH-USD</div>
        </div>
        <div>
          <div className="text-[10px] text-gray-500 mb-0.5">Cycle Interval</div>
          <div className="bg-gray-900 rounded px-2 py-1 text-[10px] border border-gray-700">15 minutes</div>
        </div>
      </div>
      <div className="grid grid-cols-2 gap-2">
        <div>
          <div className="text-[10px] text-gray-500 mb-0.5">Stop Loss %</div>
          <div className="bg-gray-900 rounded px-2 py-1 text-[10px] border border-gray-700">3%</div>
        </div>
        <div>
          <div className="text-[10px] text-gray-500 mb-0.5">Take Profit %</div>
          <div className="bg-gray-900 rounded px-2 py-1 text-[10px] border border-gray-700">6%</div>
        </div>
      </div>
      <div className="border border-red-800 rounded p-2 mt-1">
        <div className="flex items-center gap-1 text-[10px] text-red-400 font-medium">
          <AlertTriangle className="w-3 h-3" /> Live Trading
        </div>
        <div className="text-[10px] text-gray-500 mt-0.5">Requires Robinhood credentials + stage graduation</div>
      </div>
    </div>
  )
}

/* ── Annotation wrapper ─────────────────────────────────────── */

function Annotation({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div className="relative">
      <div className="absolute -left-1 -top-1 px-1.5 py-0.5 bg-accent rounded text-[9px] font-bold text-white z-10">{label}</div>
      <div className="border border-accent/30 rounded-lg p-2 pt-4 bg-gray-950/50">
        {children}
      </div>
    </div>
  )
}

/* ── Page definitions with visual mockups ────────────────────── */

interface Page {
  title: string
  icon: typeof Zap
  description: string
  mockup: () => ReactNode
  highlight: string
}

const pages: Page[] = [
  {
    title: 'Welcome to Trade Machine',
    icon: Zap,
    description: 'An autonomous crypto trading bot powered by Claude AI. 12 agents debate and collaborate to trade XRP and DOGE — high-volatility coins that move 5-15% daily. Starting with $10,000 fake money. Zero risk.',
    mockup: () => (
      <div className="space-y-3">
        <Annotation label="Your dashboard will look like this">
          <MockControlBar />
          <div className="mt-2"><MockPnLCards /></div>
          <div className="mt-2"><MockEquityCurve /></div>
        </Annotation>
      </div>
    ),
    highlight: 'Click "Start Paper Trading" on the Dashboard to begin.',
  },
  {
    title: 'The 12-Agent Pipeline',
    icon: ArrowRight,
    description: 'Every 15 minutes, 12 Claude AI agents run in sequence. They analyze 365 days of historical data, detect chart patterns with crowd psychology, debate bull vs bear, and decide whether to trade.',
    mockup: () => (
      <Annotation label="Each cycle runs these 6 steps">
        <MockAgentPipeline />
      </Annotation>
    ),
    highlight: 'Each cycle takes 1-2 minutes and makes ~12 Claude API calls.',
  },
  {
    title: 'Dashboard: Your Control Center',
    icon: BarChart3,
    description: 'Start/stop the engine, see P&L at a glance, track your equity curve, and browse recent trades.',
    mockup: () => (
      <div className="space-y-3">
        <Annotation label="Controls & Status">
          <MockControlBar />
        </Annotation>
        <Annotation label="Performance at a glance">
          <MockPnLCards />
        </Annotation>
        <Annotation label="Portfolio value over time">
          <MockEquityCurve />
        </Annotation>
      </div>
    ),
    highlight: 'The green pulsing dot means the engine is actively running cycles.',
  },
  {
    title: 'Trades: Click to See Why',
    icon: BarChart3,
    description: 'Every trade is recorded. Click any row to expand it and see exactly what each AI agent said when making that decision.',
    mockup: () => (
      <Annotation label="Click any trade to expand agent reasoning">
        <div className="space-y-1.5">
          <MockTradeRow pair="XRP-USD" side="BUY" pnl={23.45} />
          <MockTradeRow pair="DOGE-USD" side="BUY" pnl={-8.12} expanded />
          <MockTradeRow pair="XRP-USD" side="SELL" pnl={45.00} />
        </div>
      </Annotation>
    ),
    highlight: 'Green = profit, Red = loss. Every decision is explainable.',
  },
  {
    title: 'Agents: The Full Reasoning Chain',
    icon: Brain,
    description: 'See what every AI agent said during each trading cycle. Filter by agent type or cycle ID to audit any specific decision.',
    mockup: () => (
      <Annotation label="Each agent's analysis is logged">
        <MockAgentLog />
      </Annotation>
    ),
    highlight: 'If a trade loses money, come here to understand exactly what went wrong.',
  },
  {
    title: 'Learning: The Bot Gets Smarter',
    icon: GraduationCap,
    description: 'After every trade, the bot reflects on what happened. For losses, it forms hypotheses and tests them. When validated, it rewrites its own rules.',
    mockup: () => (
      <Annotation label="The learning timeline shows how the bot evolves">
        <MockLearningTimeline />
      </Annotation>
    ),
    highlight: 'Every night at midnight, the bot reviews all trades and updates its strategy.',
  },
  {
    title: 'Settings: Configure Everything',
    icon: Settings,
    description: 'Choose your Claude model, trading pairs, cycle frequency, and risk parameters. The live trading toggle is locked until the bot proves itself.',
    mockup: () => (
      <Annotation label="All settings in one place">
        <MockSettingsCard />
      </Annotation>
    ),
    highlight: 'WARNING: The Live Trading toggle uses real money. Only available after proving profitability.',
  },
  {
    title: 'The 3 Stages to Real Money',
    icon: GraduationCap,
    description: 'The bot must earn its way to real money. It cannot skip stages. You manually approve each graduation.',
    mockup: () => (
      <Annotation label="Your current progress">
        <MockStages />
      </Annotation>
    ),
    highlight: 'You are in Stage 1 (Paper). The bot is proving itself with fake money.',
  },
]

/* ── Main component ──────────────────────────────────────────── */

export default function HelpModal() {
  const [isOpen, setIsOpen] = useState(false)
  const [currentPage, setCurrentPage] = useState(0)

  const page = pages[currentPage]
  const Icon = page.icon

  return (
    <>
      <button
        onClick={() => { setIsOpen(true); setCurrentPage(0) }}
        className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-accent/10 text-accent hover:bg-accent/20 transition-colors text-sm"
      >
        <HelpCircle className="w-4 h-4" />
        How it works
      </button>

      {isOpen && (
        <div className="fixed inset-0 z-50 flex flex-col bg-stone-50 text-stone-800">
          {/* Full-screen header */}
          <div className="flex items-center justify-between px-8 py-4 border-b border-stone-200 bg-white">
            <div className="flex items-center gap-3">
              <Icon className="w-6 h-6 text-amber-600" />
              <h2 className="font-bold text-xl text-stone-800">{page.title}</h2>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-sm text-stone-400">{currentPage + 1} of {pages.length}</span>
              <button onClick={() => setIsOpen(false)} className="p-2 rounded-lg hover:bg-stone-100 text-stone-400">
                <X className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* Full-screen content */}
          <div className="flex-1 overflow-y-auto">
            <div className="max-w-3xl mx-auto px-8 py-8 space-y-6">
              <p className="text-base text-stone-600 leading-relaxed">{page.description}</p>
              <div className="bg-white border border-stone-200 rounded-xl p-6 shadow-sm">
                {page.mockup()}
              </div>
              <div className="px-4 py-3 bg-amber-50 border border-amber-200 rounded-lg">
                <p className="text-sm text-amber-800 font-medium">{page.highlight}</p>
              </div>
            </div>
          </div>

          {/* Full-screen footer */}
          <div className="flex items-center justify-between px-8 py-4 border-t border-stone-200 bg-white">
            <div className="flex gap-2">
              {pages.map((_, i) => (
                <button
                  key={i}
                  onClick={() => setCurrentPage(i)}
                  className={`w-2.5 h-2.5 rounded-full transition-colors ${i === currentPage ? 'bg-amber-600' : 'bg-stone-300 hover:bg-stone-400'}`}
                />
              ))}
            </div>
            <div className="flex gap-3">
              {currentPage > 0 && (
                <button onClick={() => setCurrentPage(currentPage - 1)} className="px-4 py-2 rounded-lg bg-stone-100 text-stone-600 text-sm hover:bg-stone-200 font-medium">Back</button>
              )}
              {currentPage < pages.length - 1 ? (
                <button onClick={() => setCurrentPage(currentPage + 1)} className="px-4 py-2 rounded-lg bg-amber-600 text-white text-sm hover:bg-amber-700 font-medium">Next</button>
              ) : (
                <button onClick={() => setIsOpen(false)} className="px-4 py-2 rounded-lg bg-amber-600 text-white text-sm hover:bg-amber-700 font-medium">Got it!</button>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  )
}
