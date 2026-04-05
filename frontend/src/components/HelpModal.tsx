import { useState } from 'react'
import { HelpCircle, X, Zap, BarChart3, Brain, GraduationCap, Settings, ArrowRight } from 'lucide-react'

const pages = [
  {
    title: 'Welcome to Trade Machine',
    icon: Zap,
    content: [
      'Trade Machine is an autonomous crypto trading bot powered by Claude AI.',
      'It uses 12 AI agents that debate and collaborate to decide whether to buy or sell BTC and ETH.',
      'Right now it trades with $10,000 of fake money (paper trading). Zero risk. It must prove itself profitable before touching real money.',
    ],
    highlight: 'Click "Start Paper Trading" on the Dashboard to begin.',
  },
  {
    title: 'How a Trading Cycle Works',
    icon: ArrowRight,
    content: [
      '1. Every 15 minutes, the engine fetches live crypto prices',
      '2. Four analyst agents analyze: price charts, news, social sentiment, and on-chain data',
      '3. A Bull Researcher argues to BUY, a Bear Researcher argues to SELL',
      '4. They debate back and forth for 2 rounds',
      '5. A Research Manager picks the winning argument',
      '6. A Trader proposes a specific trade (pair, size, stop-loss)',
      '7. Three Risk Debators argue about the risk level',
      '8. A Portfolio Manager makes the final call: approve or reject',
      '9. If approved, the trade executes with paper money',
    ],
    highlight: 'Each cycle takes 1-2 minutes because it makes ~12 Claude API calls.',
  },
  {
    title: 'Dashboard Page',
    icon: BarChart3,
    content: [
      'Start/Stop/Pause — Controls the trading engine',
      'Green pulsing dot — Engine is actively running cycles',
      'P&L Cards — Total profit/loss, win rate, number of trades, average P&L per trade',
      'Stage Progress — Shows how close you are to graduating to real money',
      'Equity Curve — Chart of your portfolio value over time',
      'Recent Trades — Last 5 trades with expandable agent reasoning',
    ],
    highlight: 'Click any trade row to see exactly what each AI agent said.',
  },
  {
    title: 'Trades Page',
    icon: BarChart3,
    content: [
      'Full history of every trade the bot has made',
      'Filter by pair (BTC, ETH) or status (open, closed)',
      'Each row shows: entry price, exit price, P&L, which stage it was in',
      'Click any row to expand and see the full agent reasoning chain',
      'Green = profitable trade, Red = losing trade',
    ],
    highlight: 'This is your trade journal — every decision is recorded and explainable.',
  },
  {
    title: 'Agents Page',
    icon: Brain,
    content: [
      'Browse what every AI agent said during each trading cycle',
      'Filter by agent type (Market Analyst, Bull Researcher, etc.)',
      'Filter by cycle ID to see all agents for one specific decision',
      'Each agent has a colored label so you can quickly scan the reasoning chain',
      'This is how you audit WHY the bot made a specific trade',
    ],
    highlight: 'If a trade loses money, come here to understand what went wrong.',
  },
  {
    title: 'Learning Page',
    icon: GraduationCap,
    content: [
      'The bot learns from every trade — this page shows how',
      'Reflections — After each trade closes, the AI reviews what went right/wrong',
      'Hypotheses — For losing trades, the AI forms testable theories about why it lost',
      'Strategy Updates — When hypotheses are validated, the bot updates its own trading rules',
      'Current Parameters — The live settings the bot uses (stop-loss %, confidence threshold, etc.)',
    ],
    highlight: 'Every night at midnight UTC, the bot reviews all trades and rewrites its rules.',
  },
  {
    title: 'Settings Page',
    icon: Settings,
    content: [
      'Claude Model — Choose which Claude model powers the agents (Sonnet = recommended)',
      'Trading Pairs — Which cryptos to analyze (default: BTC-USD, ETH-USD)',
      'Cycle Interval — How often to run analysis (default: 15 minutes)',
      'Risk Parameters — Max position size, stop-loss %, take-profit %',
      'Live Trading — Switch from paper to real money (requires Robinhood + stage graduation)',
    ],
    highlight: 'WARNING: The Live Trading toggle uses real money. Only available after proving profitability.',
  },
  {
    title: 'The 3 Stages',
    icon: GraduationCap,
    content: [
      'Stage 1: PAPER — Trade with $10,000 fake money. Must win >55% of 100+ trades to graduate.',
      'Stage 2: MICRO — $1 real trades on Robinhood. Must stay profitable over 1,000 trades.',
      'Stage 3: GRADUATED — Scale up: $2, then $5, then $10 per trade. Only if consistently profitable.',
      'You cannot skip stages. The bot must earn its way to real money.',
      'Stage transitions require your manual approval on the Dashboard.',
    ],
    highlight: 'You are currently in Stage 1 (Paper). The bot is proving itself with fake money.',
  },
]

export default function HelpModal() {
  const [isOpen, setIsOpen] = useState(false)
  const [currentPage, setCurrentPage] = useState(0)

  const page = pages[currentPage]
  const Icon = page.icon

  return (
    <>
      {/* Help button */}
      <button
        onClick={() => { setIsOpen(true); setCurrentPage(0) }}
        className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-accent/10 text-accent hover:bg-accent/20 transition-colors text-sm"
      >
        <HelpCircle className="w-4 h-4" />
        How it works
      </button>

      {/* Modal overlay */}
      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
          <div className="bg-gray-900 border border-gray-700 rounded-xl shadow-2xl w-full max-w-lg mx-4 max-h-[85vh] flex flex-col">
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-gray-800">
              <div className="flex items-center gap-2">
                <Icon className="w-5 h-5 text-accent" />
                <h2 className="font-bold text-lg">{page.title}</h2>
              </div>
              <button
                onClick={() => setIsOpen(false)}
                className="p-1 rounded hover:bg-gray-800 text-gray-400"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Content */}
            <div className="flex-1 overflow-y-auto p-4 space-y-3">
              {page.content.map((line, i) => (
                <p key={i} className="text-sm text-gray-300 leading-relaxed">
                  {line}
                </p>
              ))}

              {page.highlight && (
                <div className="mt-4 px-3 py-2 bg-accent/10 border border-accent/30 rounded-lg">
                  <p className="text-sm text-accent font-medium">{page.highlight}</p>
                </div>
              )}
            </div>

            {/* Footer with navigation */}
            <div className="flex items-center justify-between p-4 border-t border-gray-800">
              <div className="text-xs text-gray-500">
                {currentPage + 1} of {pages.length}
              </div>

              {/* Page dots */}
              <div className="flex gap-1.5">
                {pages.map((_, i) => (
                  <button
                    key={i}
                    onClick={() => setCurrentPage(i)}
                    className={`w-2 h-2 rounded-full transition-colors ${
                      i === currentPage ? 'bg-accent' : 'bg-gray-700 hover:bg-gray-600'
                    }`}
                  />
                ))}
              </div>

              <div className="flex gap-2">
                {currentPage > 0 && (
                  <button
                    onClick={() => setCurrentPage(currentPage - 1)}
                    className="px-3 py-1.5 rounded-lg bg-gray-800 text-gray-300 text-sm hover:bg-gray-700"
                  >
                    Back
                  </button>
                )}
                {currentPage < pages.length - 1 ? (
                  <button
                    onClick={() => setCurrentPage(currentPage + 1)}
                    className="px-3 py-1.5 rounded-lg bg-accent text-white text-sm hover:bg-blue-600"
                  >
                    Next
                  </button>
                ) : (
                  <button
                    onClick={() => setIsOpen(false)}
                    className="px-3 py-1.5 rounded-lg bg-accent text-white text-sm hover:bg-blue-600"
                  >
                    Got it!
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  )
}
