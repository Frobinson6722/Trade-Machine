import { ReactNode, useEffect } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { LayoutDashboard, ArrowLeftRight, Brain, GraduationCap, Settings, Zap, Sun, Moon, FileText } from 'lucide-react'
import StatusBadge from './StatusBadge'
import HelpModal from './HelpModal'
import { useWebSocket } from '../hooks/useWebSocket'
import { useActivityFeed } from '../hooks/useActivityFeed'
import { useTheme } from '../hooks/useTheme'

const navItems = [
  { path: '/', label: 'Dashboard', icon: LayoutDashboard, countKey: null },
  { path: '/trades', label: 'Trades', icon: ArrowLeftRight, countKey: 'trades' as const },
  { path: '/agents', label: 'Agents', icon: Brain, countKey: 'agents' as const },
  { path: '/learning', label: 'Learning', icon: GraduationCap, countKey: 'learning' as const },
  { path: '/release-notes', label: 'Release Notes', icon: FileText, countKey: null },
  { path: '/settings', label: 'Settings', icon: Settings, countKey: null },
]

export default function Layout({ children }: { children: ReactNode }) {
  const location = useLocation()
  const { connected } = useWebSocket()
  const { counts, clearCount } = useActivityFeed()
  const { theme, toggleTheme } = useTheme()
  const isLight = theme === 'light'

  useEffect(() => {
    const current = navItems.find(n => n.path === location.pathname)
    if (current?.countKey) {
      clearCount(current.countKey)
    }
  }, [location.pathname, clearCount])

  return (
    <div className="flex h-screen">
      {/* Sidebar */}
      <aside className={`w-64 border-r flex flex-col ${
        isLight
          ? 'bg-stone-100 border-stone-200 text-stone-800'
          : 'bg-gray-900 border-gray-800'
      }`}>
        <div className={`p-4 border-b ${isLight ? 'border-stone-200' : 'border-gray-800'}`}>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Zap className={`w-6 h-6 ${isLight ? 'text-amber-600' : 'text-accent'}`} />
              <h1 className="text-lg font-bold">Trade Machine</h1>
            </div>
            <button
              onClick={toggleTheme}
              className={`p-1.5 rounded-lg transition-colors ${
                isLight ? 'hover:bg-stone-200 text-stone-500' : 'hover:bg-gray-800 text-gray-400'
              }`}
              title={isLight ? 'Switch to dark mode' : 'Switch to light mode'}
            >
              {isLight ? <Moon className="w-4 h-4" /> : <Sun className="w-4 h-4" />}
            </button>
          </div>
          <p className={`text-xs mt-1 ${isLight ? 'text-stone-400' : 'text-gray-500'}`}>
            Autonomous Crypto Trader
          </p>
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
                    ? isLight
                      ? 'bg-amber-100 text-amber-700'
                      : 'bg-accent/10 text-accent'
                    : isLight
                      ? 'text-stone-500 hover:text-stone-800 hover:bg-stone-200'
                      : 'text-gray-400 hover:text-gray-200 hover:bg-gray-800'
                }`}
              >
                <Icon className="w-4 h-4" />
                {label}
                {count > 0 && (
                  <span className={`ml-auto text-white text-[10px] font-bold min-w-[18px] h-[18px] flex items-center justify-center rounded-full px-1 ${
                    isLight ? 'bg-amber-600' : 'bg-accent'
                  }`}>
                    {count > 99 ? '99+' : count}
                  </span>
                )}
              </Link>
            )
          })}
        </nav>

        <div className={`p-4 border-t space-y-3 ${isLight ? 'border-stone-200' : 'border-gray-800'}`}>
          <HelpModal />
          <StatusBadge />
          <div className={`flex items-center gap-2 text-xs ${isLight ? 'text-stone-400' : 'text-gray-500'}`}>
            <span className={`w-2 h-2 rounded-full ${connected ? 'bg-green-500' : 'bg-red-500'}`} />
            {connected ? 'Connected' : 'Disconnected'}
          </div>
        </div>
      </aside>

      {/* Main content */}
      <main className={`flex-1 overflow-auto p-6 ${isLight ? 'bg-stone-50' : ''}`}>
        {children}
      </main>
    </div>
  )
}
