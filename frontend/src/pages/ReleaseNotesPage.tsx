import { FileText, Zap, Brain, BarChart3, Eye, Sun, BookOpen, TrendingUp, Shield } from 'lucide-react'

interface Release {
  version: string
  date: string
  title: string
  icon: typeof Zap
  highlights: string[]
  details: string[]
}

const releases: Release[] = [
  {
    version: '0.7.0',
    date: 'April 5, 2026',
    title: 'Light Mode, Full-Screen Guide & Release Notes',
    icon: Sun,
    highlights: [
      'Added light mode with warm Claude-inspired color palette',
      'Help guide is now full-screen with light background for readability',
      'Added this Release Notes page to track product evolution',
    ],
    details: [
      'Theme toggle (sun/moon icon) in the sidebar header',
      'Light mode uses warm stone/amber tones — not harsh white',
      'Theme preference saved to localStorage',
      'Help guide updated with XRP/DOGE references and pattern info',
    ],
  },
  {
    version: '0.6.0',
    date: 'April 5, 2026',
    title: 'Historical Data, Pattern Library & XRP/DOGE',
    icon: TrendingUp,
    highlights: [
      'Engine now loads 7/30/90/365-day historical price data for each coin',
      'Built-in library of 21 trading patterns with crowd psychology explanations',
      'Switched from BTC/ETH to XRP/DOGE for high-volatility trading',
    ],
    details: [
      'Multi-timeframe analysis: agents see long-term trends, not just snapshots',
      'Support/resistance levels calculated from real historical data',
      'Patterns include: double top/bottom, head & shoulders, bull/bear flags, cup & handle, Bollinger squeeze, RSI divergence, FOMO breakouts, panic capitulation, and more',
      'Each pattern explains the mass psychology behind it (fear, greed, FOMO)',
      'Market Analyst prompt redesigned to use patterns + history + indicators together',
    ],
  },
  {
    version: '0.5.0',
    date: 'April 5, 2026',
    title: 'Live Activity Feed & Tab Badges',
    icon: Eye,
    highlights: [
      'Real-time activity feed on Dashboard showing what the engine is doing',
      'Counter badges on Trades/Agents/Learning tabs for new activity',
      'Feed persists across page navigation',
    ],
    details: [
      'Activity categorized into DATA, ANALYSIS, RESEARCH, ACTION phases',
      'Newest events appear at the top',
      'Real WebSocket events from engine — no more fake simulated data',
      'Engine broadcasts cycle start, data fetch, errors, and completions',
      'Badge counts clear when you visit the page',
    ],
  },
  {
    version: '0.4.0',
    date: 'April 5, 2026',
    title: 'Interactive Help Guide with Visual Mockups',
    icon: BookOpen,
    highlights: [
      '8-page walkthrough explaining every feature with visual mockups',
      'Annotated mini-components showing what each page looks like',
      'Agent pipeline visualization showing the 12-agent flow',
    ],
    details: [
      'Dashboard mockup: control bar, P&L cards, equity curve',
      'Trade table mockup with expandable agent reasoning',
      'Learning timeline mockup with reflections, hypotheses, strategy updates',
      'Stage progression visualization',
      'Accessible from "How it works" button in sidebar',
    ],
  },
  {
    version: '0.3.0',
    date: 'April 5, 2026',
    title: 'Claude-Only Engine & Dashboard Improvements',
    icon: Brain,
    highlights: [
      'Removed OpenAI and Google — engine runs exclusively on Anthropic Claude',
      'Dashboard shows status banners, loading spinners, toast notifications',
      'Free CoinGecko API for market data (no Robinhood needed for paper trading)',
    ],
    details: [
      'Default model: Claude Sonnet 4 for analysis, Claude Haiku 4.5 for quick tasks',
      'Settings page shows Claude model selector only',
      '.env file loads automatically via python-dotenv',
      'SSL certificate fix for macOS',
      'Auth removed from session endpoints for local use',
    ],
  },
  {
    version: '0.2.0',
    date: 'April 5, 2026',
    title: 'Self-Learning Trading Engine',
    icon: Shield,
    highlights: [
      'Three-stage risk escalation: Paper → $1 Micro → Graduated scaling',
      'Per-trade reflection: AI reviews every trade outcome',
      'Hypothesis engine: reverse-engineers losses, tests theories against history',
      'Nightly learner: rewrites trading rules at midnight based on what it learned',
    ],
    details: [
      'Stage Manager enforces graduation criteria before real money',
      'Paper: must win >55% of 100+ trades to graduate',
      'Micro: $1 real trades, must stay profitable over 1,000 trades',
      'Graduated: $2 → $5 → $10, only if consistently profitable',
      'Memory system provides context from past trades to all agents',
    ],
  },
  {
    version: '0.1.0',
    date: 'April 5, 2026',
    title: 'Initial Build — Full Trading Platform',
    icon: Zap,
    highlights: [
      '105 files across engine/, backend/, and frontend/',
      '12 AI agents: 4 analysts, 2 researchers, 3 risk debators, research manager, trader, portfolio manager',
      'LangGraph orchestration for multi-agent debate pipeline',
      'React dashboard with equity curves, trade history, agent reasoning',
    ],
    details: [
      'Engine: Multi-agent analysis using LangGraph StateGraph',
      'Backend: FastAPI + SQLAlchemy + SQLite + WebSocket',
      'Frontend: React 18 + TypeScript + Vite + Tailwind + Recharts',
      'Paper trading with virtual $10,000 balance',
      'Real-time WebSocket updates to dashboard',
      '5 pages: Dashboard, Trades, Agents, Learning, Settings',
    ],
  },
]

export default function ReleaseNotesPage() {
  return (
    <div className="space-y-6 max-w-3xl">
      <div className="flex items-center gap-3">
        <FileText className="w-6 h-6 text-accent" />
        <h2 className="text-2xl font-bold text-primary">Release Notes</h2>
      </div>
      <p className="text-sm text-muted">A running record of every major change to Trade Machine.</p>

      <div className="space-y-6">
        {releases.map((release, idx) => {
          const Icon = release.icon
          return (
            <div key={release.version} className="card">
              <div className="flex items-start gap-3">
                <div className="p-2 rounded-lg bg-[var(--accent-subtle)]">
                  <Icon className="w-5 h-5 text-accent" />
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-1">
                    <span className="text-xs font-bold px-2 py-0.5 rounded-full bg-[var(--accent-subtle)] text-accent">
                      v{release.version}
                    </span>
                    <span className="text-xs text-faint">{release.date}</span>
                    {idx === 0 && (
                      <span className="text-xs font-bold px-2 py-0.5 rounded-full bg-green-500/15 text-green-700">LATEST</span>
                    )}
                  </div>
                  <h3 className="font-semibold text-lg text-primary mb-2">{release.title}</h3>

                  <div className="space-y-1.5 mb-3">
                    {release.highlights.map((h, i) => (
                      <div key={i} className="flex items-start gap-2">
                        <span className="text-xs mt-0.5 text-accent">●</span>
                        <span className="text-sm font-medium text-secondary">{h}</span>
                      </div>
                    ))}
                  </div>

                  <details className="text-xs text-muted">
                    <summary className="cursor-pointer hover:underline">Technical details</summary>
                    <ul className="mt-2 space-y-1 ml-3">
                      {release.details.map((d, i) => (
                        <li key={i} className="list-disc">{d}</li>
                      ))}
                    </ul>
                  </details>
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
