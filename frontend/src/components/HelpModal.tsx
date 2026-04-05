import { useState, ReactNode } from 'react'
import { HelpCircle, X, Zap, BarChart3, Brain, GraduationCap, Settings, ArrowRight, ArrowDown, Play, TrendingUp, TrendingDown, Target, ChevronDown, AlertTriangle, Lightbulb, CheckCircle2 } from 'lucide-react'

/* ── Light-mode mockup components (large, readable) ────────── */

function MockPnLCards() {
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div className="bg-white border border-stone-200 rounded-xl p-4 shadow-sm">
        <div className="text-stone-400 flex items-center gap-2 text-sm mb-1"><TrendingUp className="w-4 h-4 text-green-600" /> Total P&L</div>
        <div className="text-green-600 font-bold text-2xl">+$342.18</div>
      </div>
      <div className="bg-white border border-stone-200 rounded-xl p-4 shadow-sm">
        <div className="text-stone-400 flex items-center gap-2 text-sm mb-1"><Target className="w-4 h-4 text-amber-600" /> Win Rate</div>
        <div className="text-green-600 font-bold text-2xl">58.3%</div>
      </div>
      <div className="bg-white border border-stone-200 rounded-xl p-4 shadow-sm">
        <div className="text-stone-400 flex items-center gap-2 text-sm mb-1"><BarChart3 className="w-4 h-4 text-stone-500" /> Total Trades</div>
        <div className="text-stone-800 font-bold text-2xl">24</div>
      </div>
      <div className="bg-white border border-stone-200 rounded-xl p-4 shadow-sm">
        <div className="text-stone-400 flex items-center gap-2 text-sm mb-1"><TrendingUp className="w-4 h-4 text-green-600" /> Avg P&L</div>
        <div className="text-green-600 font-bold text-2xl">+$14.26</div>
      </div>
    </div>
  )
}

function MockEquityCurve() {
  return (
    <div className="bg-white border border-stone-200 rounded-xl p-5 shadow-sm">
      <div className="text-sm text-stone-400 mb-3 font-medium">Equity Curve — Portfolio Value Over Time</div>
      <svg viewBox="0 0 400 100" className="w-full h-24">
        <defs>
          <linearGradient id="mockGradLight" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#16a34a" stopOpacity="0.2" />
            <stop offset="100%" stopColor="#16a34a" stopOpacity="0" />
          </linearGradient>
        </defs>
        <path d="M0,80 L40,78 L80,72 L120,68 L160,60 L200,65 L240,55 L280,45 L320,38 L360,30 L400,20" stroke="#16a34a" strokeWidth="2.5" fill="none" />
        <path d="M0,80 L40,78 L80,72 L120,68 L160,60 L200,65 L240,55 L280,45 L320,38 L360,30 L400,20 L400,100 L0,100Z" fill="url(#mockGradLight)" />
      </svg>
      <div className="flex justify-between text-xs text-stone-400 mt-2">
        <span>Apr 1</span><span>Apr 2</span><span>Apr 3</span><span>Apr 4</span><span>Apr 5</span>
      </div>
    </div>
  )
}

function MockTradeRow({ pair, side, pnl, expanded }: { pair: string; side: string; pnl: number; expanded?: boolean }) {
  return (
    <div className="bg-white border border-stone-200 rounded-xl shadow-sm overflow-hidden">
      <div className="flex items-center gap-4 px-5 py-4">
        <ChevronDown className={`w-5 h-5 text-stone-400 ${expanded ? '' : '-rotate-90'}`} />
        <span className="font-semibold text-stone-800 text-base">{pair}</span>
        <span className={`font-medium text-base ${side === 'BUY' ? 'text-green-600' : 'text-red-600'}`}>{side}</span>
        <span className="ml-auto font-bold text-base">
          {pnl >= 0
            ? <span className="text-green-600">+${pnl.toFixed(2)}</span>
            : <span className="text-red-600">-${Math.abs(pnl).toFixed(2)}</span>
          }
        </span>
      </div>
      {expanded && (
        <div className="px-5 pb-4 border-t border-stone-100 pt-4 space-y-3">
          <div>
            <div className="text-sm text-blue-600 font-semibold">Market Analyst</div>
            <div className="text-sm text-stone-500 mt-0.5">RSI at 68, MACD bullish crossover forming. XRP testing $2.15 resistance with increasing volume...</div>
          </div>
          <div>
            <div className="text-sm text-green-600 font-semibold">Bull Researcher</div>
            <div className="text-sm text-stone-500 mt-0.5">Strong momentum with Ripple SEC case resolution driving inflows. Breakout above $2.20 likely...</div>
          </div>
          <div>
            <div className="text-sm text-red-600 font-semibold">Bear Researcher</div>
            <div className="text-sm text-stone-500 mt-0.5">Overbought RSI, potential double top at $2.15. Volume divergence suggests weakening buying pressure...</div>
          </div>
        </div>
      )}
    </div>
  )
}

function MockAgentLog() {
  return (
    <div className="space-y-4">
      <div className="bg-white border border-stone-200 rounded-xl p-5 shadow-sm">
        <div className="text-base text-blue-600 font-semibold mb-2">Market Analyst</div>
        <div className="text-sm text-stone-600 leading-relaxed">XRP showing bullish momentum. RSI: 65 (neutral-bullish). MACD just crossed bullish. Volume 15% above 20-day average. Detected <strong>Bull Flag</strong> pattern — psychology: profit-taking pullback before next leg up. Key resistance at $2.20.</div>
      </div>
      <div className="bg-white border border-stone-200 rounded-xl p-5 shadow-sm">
        <div className="text-base text-purple-600 font-semibold mb-2">News Analyst</div>
        <div className="text-sm text-stone-600 leading-relaxed">Positive: Ripple partnership with major bank announced. Neutral: Fed holding rates steady. XRP-specific: trading volume up 40% on Binance in last 24h.</div>
      </div>
      <div className="bg-white border border-stone-200 rounded-xl p-5 shadow-sm">
        <div className="text-base text-pink-600 font-semibold mb-2">Sentiment Analyst</div>
        <div className="text-sm text-stone-600 leading-relaxed">Fear & Greed: 72 (Greed). Reddit r/XRP sentiment improving. Twitter mentions up 23%. Contrarian caution: approaching extreme greed territory.</div>
      </div>
    </div>
  )
}

function MockLearningTimeline() {
  return (
    <div className="space-y-4">
      <div className="bg-white border border-stone-200 rounded-xl p-5 shadow-sm flex gap-4">
        <Brain className="w-6 h-6 text-purple-500 shrink-0 mt-0.5" />
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-bold text-stone-400 uppercase tracking-wide">Reflection</span>
            <span className="text-xs px-2 py-0.5 rounded-full bg-red-100 text-red-600 font-medium">loss</span>
          </div>
          <div className="text-sm text-stone-600 leading-relaxed">RSI was at 72 but volume was declining — should have weighted volume divergence more heavily before entering. The <strong>Bearish Divergence</strong> pattern was present but underweighted.</div>
        </div>
      </div>
      <div className="bg-white border border-stone-200 rounded-xl p-5 shadow-sm flex gap-4">
        <Lightbulb className="w-6 h-6 text-yellow-500 shrink-0 mt-0.5" />
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-bold text-stone-400 uppercase tracking-wide">Hypothesis</span>
            <span className="text-xs px-2 py-0.5 rounded-full bg-green-100 text-green-600 font-medium">validated</span>
          </div>
          <div className="text-sm text-stone-600 leading-relaxed">When RSI &gt; 70 AND volume is declining, short-term pullback occurs 73% of the time. Tested against last 50 trades — confirmed.</div>
        </div>
      </div>
      <div className="bg-white border border-stone-200 rounded-xl p-5 shadow-sm flex gap-4">
        <Settings className="w-6 h-6 text-amber-600 shrink-0 mt-0.5" />
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-bold text-stone-400 uppercase tracking-wide">Strategy Update</span>
          </div>
          <div className="text-sm text-stone-600 leading-relaxed">New rule added: <strong>Skip BUY when RSI &gt; 70 and volume ratio &lt; 0.8</strong>. This rule would have avoided 4 of the last 6 losing trades.</div>
        </div>
      </div>
    </div>
  )
}

function MockStages() {
  return (
    <div className="space-y-4">
      {[
        { name: 'Stage 1: Paper Trading', desc: '$10,000 fake money', rule: 'Win >55% of 100+ trades to graduate', active: true },
        { name: 'Stage 2: Micro Stakes', desc: '$1 real trades on Robinhood', rule: 'Stay profitable over 1,000 trades', active: false },
        { name: 'Stage 3: Graduated Scaling', desc: '$2 → $5 → $10 per trade', rule: 'Scale only if consistently profitable', active: false },
      ].map((s, i) => (
        <div key={i} className={`rounded-xl p-5 border-2 ${s.active ? 'border-amber-400 bg-amber-50' : 'border-stone-200 bg-white'} shadow-sm`}>
          <div className="flex items-center justify-between">
            <div>
              <div className="text-base font-semibold text-stone-800">{s.name}</div>
              <div className="text-sm text-stone-500 mt-0.5">{s.desc}</div>
            </div>
            <div className="text-right">
              <div className="text-sm text-stone-500">{s.rule}</div>
              {s.active ? (
                <div className="text-sm text-amber-600 font-bold mt-1">You are here</div>
              ) : (
                <div className="text-sm text-stone-300 mt-1">Locked</div>
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
    { agents: ['Market', 'News', 'Sentiment', 'Fundamentals'], label: 'Analysts gather data + detect patterns', color: 'bg-blue-50 text-blue-700 border-blue-200' },
    { agents: ['Bull Researcher', 'Bear Researcher'], label: 'Opposing sides build their case', color: 'bg-green-50 text-green-700 border-green-200' },
    { agents: ['Research Manager'], label: 'Weighs both sides, picks the winner', color: 'bg-yellow-50 text-yellow-700 border-yellow-200' },
    { agents: ['Trader'], label: 'Designs the specific trade proposal', color: 'bg-purple-50 text-purple-700 border-purple-200' },
    { agents: ['Aggressive', 'Conservative', 'Neutral'], label: 'Three risk perspectives debate the trade', color: 'bg-orange-50 text-orange-700 border-orange-200' },
    { agents: ['Portfolio Manager'], label: 'Final approval or rejection', color: 'bg-indigo-50 text-indigo-700 border-indigo-200' },
  ]
  return (
    <div className="space-y-3">
      {stages.map((s, i) => (
        <div key={i}>
          <div className={`rounded-xl px-5 py-4 border ${s.color}`}>
            <div className="flex items-center justify-between">
              <div>
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="text-xs font-bold bg-white/60 rounded px-2 py-0.5">Step {i + 1}</span>
                  {s.agents.map((a, j) => (
                    <span key={j} className="text-sm font-semibold">{a}</span>
                  ))}
                </div>
                <div className="text-sm opacity-80 mt-1">{s.label}</div>
              </div>
            </div>
          </div>
          {i < stages.length - 1 && (
            <div className="flex justify-center py-1">
              <ArrowDown className="w-4 h-4 text-stone-300" />
            </div>
          )}
        </div>
      ))}
    </div>
  )
}

function MockControlBar() {
  return (
    <div className="space-y-4">
      <div className="bg-white border border-stone-200 rounded-xl p-5 shadow-sm">
        <div className="flex items-center justify-between">
          <div>
            <div className="text-lg font-bold text-stone-800">Dashboard</div>
            <div className="text-sm text-stone-400">Stage: paper | Mode: paper</div>
          </div>
          <button className="bg-amber-600 text-white px-4 py-2 rounded-lg flex items-center gap-2 text-sm font-medium">
            <Play className="w-4 h-4" /> Start Paper Trading
          </button>
        </div>
      </div>
      <div className="flex items-center gap-3 px-5 py-3 bg-green-50 border border-green-200 rounded-xl">
        <div className="w-3 h-3 rounded-full bg-green-500 animate-pulse" />
        <span className="text-sm text-green-700 font-medium">
          Engine is running — analyzing XRP & DOGE with Claude AI agents. Cycles run every 15 minutes.
        </span>
      </div>
    </div>
  )
}

function MockSettingsCard() {
  return (
    <div className="space-y-4">
      <div className="bg-white border border-stone-200 rounded-xl p-5 shadow-sm space-y-4">
        <div>
          <div className="text-sm text-stone-500 mb-1 font-medium">Claude Model</div>
          <div className="bg-stone-50 rounded-lg px-4 py-2.5 text-sm border border-stone-200 text-stone-800">Claude Sonnet 4 (recommended)</div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <div className="text-sm text-stone-500 mb-1 font-medium">Trading Pairs</div>
            <div className="bg-stone-50 rounded-lg px-4 py-2.5 text-sm border border-stone-200 text-stone-800">XRP-USD, DOGE-USD</div>
          </div>
          <div>
            <div className="text-sm text-stone-500 mb-1 font-medium">Cycle Interval</div>
            <div className="bg-stone-50 rounded-lg px-4 py-2.5 text-sm border border-stone-200 text-stone-800">15 minutes</div>
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <div className="text-sm text-stone-500 mb-1 font-medium">Default Stop Loss</div>
            <div className="bg-stone-50 rounded-lg px-4 py-2.5 text-sm border border-stone-200 text-stone-800">3%</div>
          </div>
          <div>
            <div className="text-sm text-stone-500 mb-1 font-medium">Default Take Profit</div>
            <div className="bg-stone-50 rounded-lg px-4 py-2.5 text-sm border border-stone-200 text-stone-800">6%</div>
          </div>
        </div>
      </div>
      <div className="border-2 border-red-200 rounded-xl p-5 bg-red-50">
        <div className="flex items-center gap-2 text-base text-red-600 font-semibold">
          <AlertTriangle className="w-5 h-5" /> Live Trading
        </div>
        <div className="text-sm text-red-500 mt-1">Requires Robinhood credentials + stage graduation. Uses real money.</div>
      </div>
    </div>
  )
}

/* ── Annotation wrapper (light mode) ───────────────────────── */

function Annotation({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div className="relative">
      <div className="absolute -left-2 -top-3 px-2.5 py-1 bg-amber-600 rounded-lg text-xs font-bold text-white z-10 shadow-sm">{label}</div>
      <div className="border-2 border-amber-200 rounded-xl p-5 pt-6 bg-stone-50/50">
        {children}
      </div>
    </div>
  )
}

/* ── Page definitions ────────────────────────────────────────── */

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
      <div className="space-y-5">
        <Annotation label="Your dashboard will look like this">
          <MockControlBar />
          <div className="mt-4"><MockPnLCards /></div>
          <div className="mt-4"><MockEquityCurve /></div>
        </Annotation>
      </div>
    ),
    highlight: 'Click "Start Paper Trading" on the Dashboard to begin.',
  },
  {
    title: 'The 12-Agent Pipeline',
    icon: ArrowRight,
    description: 'Every 15 minutes, 12 Claude AI agents run in sequence. They analyze 365 days of historical data, detect 21 chart patterns with crowd psychology, debate bull vs bear, and decide whether to trade.',
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
    description: 'Start/stop the engine, see P&L at a glance, track your equity curve over time, and browse recent trades.',
    mockup: () => (
      <div className="space-y-5">
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
    highlight: 'The green pulsing dot means the engine is actively running analysis cycles.',
  },
  {
    title: 'Trades: Click Any Row to See Why',
    icon: BarChart3,
    description: 'Every trade is recorded with full transparency. Click any trade row to expand it and read exactly what each AI agent said when making that decision.',
    mockup: () => (
      <Annotation label="Click any trade to see the full reasoning chain">
        <div className="space-y-3">
          <MockTradeRow pair="XRP-USD" side="BUY" pnl={23.45} />
          <MockTradeRow pair="DOGE-USD" side="BUY" pnl={-8.12} expanded />
          <MockTradeRow pair="XRP-USD" side="SELL" pnl={45.00} />
        </div>
      </Annotation>
    ),
    highlight: 'Green = profit, Red = loss. Every single decision is explainable and auditable.',
  },
  {
    title: 'Agents: The Full Reasoning Chain',
    icon: Brain,
    description: 'See what every AI agent said during each trading cycle. Each agent is color-coded. Filter by agent type or cycle ID to audit any specific decision.',
    mockup: () => (
      <Annotation label="Each agent's full analysis is logged and searchable">
        <MockAgentLog />
      </Annotation>
    ),
    highlight: 'If a trade loses money, come here to understand exactly what went wrong.',
  },
  {
    title: 'Learning: The Bot Gets Smarter',
    icon: GraduationCap,
    description: 'After every trade, the bot reflects on what happened. For losses, it forms hypotheses about why and tests them against history. When validated, it rewrites its own trading rules.',
    mockup: () => (
      <Annotation label="The learning timeline shows how the bot evolves over time">
        <MockLearningTimeline />
      </Annotation>
    ),
    highlight: 'Every night at midnight, the bot reviews all trades and updates its strategy automatically.',
  },
  {
    title: 'Settings: Configure Everything',
    icon: Settings,
    description: 'Choose your Claude model, trading pairs, cycle frequency, and risk parameters. The live trading toggle is locked until the bot proves itself profitable.',
    mockup: () => (
      <Annotation label="All configuration in one place">
        <MockSettingsCard />
      </Annotation>
    ),
    highlight: 'WARNING: The Live Trading toggle uses real money. Only available after proving profitability in paper trading.',
  },
  {
    title: 'The 3 Stages to Real Money',
    icon: GraduationCap,
    description: 'The bot must earn its way to real money. It cannot skip stages. Each graduation requires your manual approval. The system is designed to protect your capital.',
    mockup: () => (
      <Annotation label="Your current progress through the stages">
        <MockStages />
      </Annotation>
    ),
    highlight: 'You are currently in Stage 1 (Paper). The bot is proving itself with fake money before touching a single real dollar.',
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
          {/* Header */}
          <div className="flex items-center justify-between px-8 py-5 border-b border-stone-200 bg-white shadow-sm">
            <div className="flex items-center gap-3">
              <Icon className="w-7 h-7 text-amber-600" />
              <h2 className="font-bold text-2xl text-stone-800">{page.title}</h2>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-sm text-stone-400">{currentPage + 1} of {pages.length}</span>
              <button onClick={() => setIsOpen(false)} className="p-2 rounded-lg hover:bg-stone-100 text-stone-400">
                <X className="w-6 h-6" />
              </button>
            </div>
          </div>

          {/* Content */}
          <div className="flex-1 overflow-y-auto">
            <div className="max-w-4xl mx-auto px-8 py-10 space-y-8">
              <p className="text-lg text-stone-600 leading-relaxed">{page.description}</p>
              {page.mockup()}
              <div className="px-5 py-4 bg-amber-50 border border-amber-200 rounded-xl">
                <p className="text-base text-amber-800 font-medium">{page.highlight}</p>
              </div>
            </div>
          </div>

          {/* Footer */}
          <div className="flex items-center justify-between px-8 py-4 border-t border-stone-200 bg-white shadow-sm">
            <div className="flex gap-2">
              {pages.map((_, i) => (
                <button
                  key={i}
                  onClick={() => setCurrentPage(i)}
                  className={`w-3 h-3 rounded-full transition-colors ${i === currentPage ? 'bg-amber-600' : 'bg-stone-300 hover:bg-stone-400'}`}
                />
              ))}
            </div>
            <div className="flex gap-3">
              {currentPage > 0 && (
                <button onClick={() => setCurrentPage(currentPage - 1)} className="px-5 py-2.5 rounded-lg bg-stone-100 text-stone-600 text-sm hover:bg-stone-200 font-medium">Back</button>
              )}
              {currentPage < pages.length - 1 ? (
                <button onClick={() => setCurrentPage(currentPage + 1)} className="px-5 py-2.5 rounded-lg bg-amber-600 text-white text-sm hover:bg-amber-700 font-medium">Next</button>
              ) : (
                <button onClick={() => setIsOpen(false)} className="px-5 py-2.5 rounded-lg bg-amber-600 text-white text-sm hover:bg-amber-700 font-medium">Got it!</button>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  )
}
