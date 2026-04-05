import { ReactNode, useEffect } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { LayoutDashboard, ArrowLeftRight, Brain, GraduationCap, Settings, Zap } from 'lucide-react'
import StatusBadge from './StatusBadge'
import HelpModal from './HelpModal'
import { useWebSocket } from '../hooks/useWebSocket'
import { useActivityFeed } from '../hooks/useActivityFeed'

const navItems = [
  { path: '/', label: 'Dashboard', icon: LayoutDashboard, countKey: null },
  { path: '/trades', label: 'Trades', icon: ArrowLeftRight, countKey: 'trades' as const },
  { path: '/agents', label: 'Agents', icon: Brain, countKey: 'agents' as const },
  { path: '/learning', label: 'Learning', icon: GraduationCap, countKey: 'learning' as const },
  { path: '/settings', label: 'Settings', icon: Settings, countKey: null },
]

export default function Layout({ children }: { children: ReactNode }) {
  const location = useLocation()
  const { connected } = useWebSocket()
  const { counts, clearCount } = useActivityFeed()

  // Clear count when visiting a page
  useEffect(() => {
    const current = navItems.find(n => n.path === location.pathname)
    if (current?.countKey) {
      clearCount(current.countKey)
    }
  }, [location.pathname, clearCount])

  return (
    <div className="flex h-screen">
      {/* Sidebar */}
      <aside className="w-64 bg-gray-900 border-r border-gray-800 flex flex-col">
        <div className="p-4 border-b border-gray-800">
          <div className="flex items-center gap-2">
            <Zap className="w-6 h-6 text-accent" />
            <h1 className="text-lg font-bold">Trade Machine</h1>
          </div>
          <p className="text-xs text-gray-500 mt-1">Autonomous Crypto Trader</p>
        </div>

        <nav className="flex-1 p-3 space-y-1">
          {navItems.map(({ path, label, icon: Icon, countKey }) => {
            const active = location.pathname === path
            const count = countKey ? counts[countKey] : 0
            return (
              <Link
                key={path}
                to={path}
                className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors ${
                  active
                    ? 'bg-accent/10 text-accent'
                    : 'text-gray-400 hover:text-gray-200 hover:bg-gray-800'
                }`}
              >
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

        <div className="p-4 border-t border-gray-800 space-y-3">
          <HelpModal />
          <StatusBadge />
          <div className="flex items-center gap-2 text-xs text-gray-500">
            <span className={`w-2 h-2 rounded-full ${connected ? 'bg-green-500' : 'bg-red-500'}`} />
            {connected ? 'Connected' : 'Disconnected'}
          </div>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-auto p-6">
        {children}
      </main>
    </div>
  )
}
