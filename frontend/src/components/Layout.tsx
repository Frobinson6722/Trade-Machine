import { ReactNode, useEffect } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { LayoutDashboard, Brain, MoreHorizontal, Zap, Sun, Moon } from 'lucide-react'
import StatusBadge from './StatusBadge'
import HelpModal from './HelpModal'
import { useWebSocket } from '../hooks/useWebSocket'
import { useActivityFeed } from '../hooks/useActivityFeed'
import { useTheme } from '../hooks/useTheme'

const navItems = [
  { path: '/', label: 'Dashboard', icon: LayoutDashboard, countKey: null },
  { path: '/agents', label: 'Decisions', icon: Brain, countKey: 'trades' as const },
  { path: '/more', label: 'More', icon: MoreHorizontal, countKey: null },
]

export default function Layout({ children }: { children: ReactNode }) {
  const location = useLocation()
  const { connected } = useWebSocket()
  const { counts, clearCount } = useActivityFeed()
  const { theme, toggleTheme } = useTheme()

  useEffect(() => {
    const current = navItems.find(n => n.path === location.pathname)
    if (current?.countKey) clearCount(current.countKey)
  }, [location.pathname, clearCount])

  return (
    <div className="flex h-screen bg-surface-primary">
      <aside className="w-64 flex flex-col bg-surface-secondary border-r border-border">
        <div className="p-4 border-b border-border">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Zap className="w-6 h-6 text-accent" />
              <h1 className="text-lg font-bold text-primary">Trade Machine</h1>
            </div>
            <button onClick={toggleTheme} className="p-1.5 rounded-lg text-muted hover:bg-surface-hover transition-colors"
              title={theme === 'light' ? 'Dark mode' : 'Light mode'}>
              {theme === 'light' ? <Moon className="w-4 h-4" /> : <Sun className="w-4 h-4" />}
            </button>
          </div>
          <p className="text-xs mt-1 text-faint">Autonomous Crypto Trader</p>
        </div>

        <nav className="flex-1 p-3 space-y-0.5">
          {navItems.map(({ path, label, icon: Icon, countKey }) => {
            const active = location.pathname === path
            const count = countKey ? counts[countKey] : 0
            return (
              <Link key={path} to={path}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors
                  ${active ? 'bg-[var(--accent-subtle)] text-accent' : 'text-muted hover:text-primary hover:bg-surface-hover'}`}>
                <Icon className="w-4 h-4" />
                {label}
                {count > 0 && (
                  <span className="ml-auto bg-accent text-white text-[10px] font-bold min-w-[18px] h-[18px] flex items-center justify-center rounded-full px-1">
                    {count > 99 ? '99+' : count}
                  </span>
                )}
              </Link>
            )
          })}
        </nav>

        <div className="p-4 border-t border-border space-y-3">
          <HelpModal />
          <StatusBadge />
          <div className="flex items-center gap-2 text-xs text-faint">
            <span className={`w-2 h-2 rounded-full ${connected ? 'bg-green-500' : 'bg-red-500'}`} />
            {connected ? 'Connected' : 'Disconnected'}
          </div>
        </div>
      </aside>

      <main className="flex-1 overflow-auto p-6 bg-surface-primary">
        {children}
      </main>
    </div>
  )
}
