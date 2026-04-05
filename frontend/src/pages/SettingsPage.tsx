import { useState, useEffect } from 'react'
import { useSettings, useUpdateSettings, useStartSession, useStopSession } from '../hooks/useApi'
import { Settings as SettingsIcon, AlertTriangle } from 'lucide-react'

export default function SettingsPage() {
  const { data: settings, isLoading } = useSettings()
  const updateSettings = useUpdateSettings()
  const startSession = useStartSession()
  const stopSession = useStopSession()

  const [form, setForm] = useState({
    llm_provider: 'openai',
    llm_model: 'gpt-4o',
    trading_pairs: 'BTC-USD,ETH-USD',
    cycle_interval_seconds: 900,
    max_position_size_pct: 5,
    max_portfolio_allocation_pct: 25,
    default_stop_loss_pct: 3,
    default_take_profit_pct: 6,
  })

  const [showLiveConfirm, setShowLiveConfirm] = useState(false)
  const [authToken, setAuthToken] = useState('')

  useEffect(() => {
    if (settings) {
      setForm({
        llm_provider: settings.llm_provider,
        llm_model: settings.llm_model,
        trading_pairs: settings.trading_pairs.join(','),
        cycle_interval_seconds: settings.cycle_interval_seconds,
        max_position_size_pct: settings.max_position_size_pct,
        max_portfolio_allocation_pct: settings.max_portfolio_allocation_pct,
        default_stop_loss_pct: settings.default_stop_loss_pct,
        default_take_profit_pct: settings.default_take_profit_pct,
      })
    }
  }, [settings])

  const handleSave = () => {
    updateSettings.mutate({
      llm_provider: form.llm_provider,
      llm_model: form.llm_model,
      trading_pairs: form.trading_pairs.split(',').map((s) => s.trim()),
      cycle_interval_seconds: form.cycle_interval_seconds,
      max_position_size_pct: form.max_position_size_pct,
      max_portfolio_allocation_pct: form.max_portfolio_allocation_pct,
      default_stop_loss_pct: form.default_stop_loss_pct,
      default_take_profit_pct: form.default_take_profit_pct,
    })
  }

  const handleSaveToken = () => {
    localStorage.setItem('auth_token', authToken)
  }

  if (isLoading) return <div className="text-gray-500">Loading settings...</div>

  return (
    <div className="space-y-6 max-w-2xl">
      <div className="flex items-center gap-3">
        <SettingsIcon className="w-6 h-6 text-accent" />
        <h2 className="text-2xl font-bold">Settings</h2>
      </div>

      {/* Auth Token */}
      <div className="card space-y-3">
        <h3 className="font-medium">Authentication</h3>
        <div>
          <label className="text-sm text-gray-400 block mb-1">Auth Token</label>
          <div className="flex gap-2">
            <input
              type="password"
              className="input flex-1"
              value={authToken}
              onChange={(e) => setAuthToken(e.target.value)}
              placeholder="Enter your auth token..."
            />
            <button className="btn-primary" onClick={handleSaveToken}>Save</button>
          </div>
        </div>
      </div>

      {/* LLM Settings */}
      <div className="card space-y-3">
        <h3 className="font-medium">LLM Configuration</h3>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="text-sm text-gray-400 block mb-1">Provider</label>
            <select
              className="input w-full"
              value={form.llm_provider}
              onChange={(e) => setForm({ ...form, llm_provider: e.target.value })}
            >
              <option value="openai">OpenAI</option>
              <option value="anthropic">Anthropic</option>
              <option value="google">Google</option>
            </select>
          </div>
          <div>
            <label className="text-sm text-gray-400 block mb-1">Model</label>
            <input
              className="input w-full"
              value={form.llm_model}
              onChange={(e) => setForm({ ...form, llm_model: e.target.value })}
            />
          </div>
        </div>
      </div>

      {/* Trading Settings */}
      <div className="card space-y-3">
        <h3 className="font-medium">Trading Configuration</h3>
        <div>
          <label className="text-sm text-gray-400 block mb-1">Trading Pairs (comma-separated)</label>
          <input
            className="input w-full"
            value={form.trading_pairs}
            onChange={(e) => setForm({ ...form, trading_pairs: e.target.value })}
          />
        </div>
        <div>
          <label className="text-sm text-gray-400 block mb-1">
            Cycle Interval (seconds): {form.cycle_interval_seconds}
          </label>
          <input
            type="range"
            min={60}
            max={3600}
            step={60}
            value={form.cycle_interval_seconds}
            onChange={(e) => setForm({ ...form, cycle_interval_seconds: Number(e.target.value) })}
            className="w-full"
          />
        </div>
      </div>

      {/* Risk Settings */}
      <div className="card space-y-3">
        <h3 className="font-medium">Risk Parameters</h3>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="text-sm text-gray-400 block mb-1">Max Position Size (%)</label>
            <input
              type="number"
              className="input w-full"
              value={form.max_position_size_pct}
              onChange={(e) => setForm({ ...form, max_position_size_pct: Number(e.target.value) })}
            />
          </div>
          <div>
            <label className="text-sm text-gray-400 block mb-1">Max Portfolio Allocation (%)</label>
            <input
              type="number"
              className="input w-full"
              value={form.max_portfolio_allocation_pct}
              onChange={(e) => setForm({ ...form, max_portfolio_allocation_pct: Number(e.target.value) })}
            />
          </div>
          <div>
            <label className="text-sm text-gray-400 block mb-1">Default Stop Loss (%)</label>
            <input
              type="number"
              className="input w-full"
              value={form.default_stop_loss_pct}
              onChange={(e) => setForm({ ...form, default_stop_loss_pct: Number(e.target.value) })}
            />
          </div>
          <div>
            <label className="text-sm text-gray-400 block mb-1">Default Take Profit (%)</label>
            <input
              type="number"
              className="input w-full"
              value={form.default_take_profit_pct}
              onChange={(e) => setForm({ ...form, default_take_profit_pct: Number(e.target.value) })}
            />
          </div>
        </div>
      </div>

      {/* Save Button */}
      <button className="btn-primary w-full" onClick={handleSave}>
        {updateSettings.isPending ? 'Saving...' : 'Save Settings'}
      </button>

      {/* Live Trading Toggle */}
      <div className="card border-red-900">
        <div className="flex items-center gap-2 mb-3">
          <AlertTriangle className="w-5 h-5 text-red-500" />
          <h3 className="font-medium text-red-400">Live Trading</h3>
        </div>
        <p className="text-sm text-gray-400 mb-3">
          Current mode: <span className="font-medium text-white">{settings?.mode ?? 'paper'}</span>
          {' | '}
          Stage: <span className="font-medium text-white">{settings?.current_stage ?? 'paper'}</span>
        </p>

        {!showLiveConfirm ? (
          <button
            className="btn-danger"
            onClick={() => setShowLiveConfirm(true)}
            disabled={settings?.mode === 'live'}
          >
            {settings?.mode === 'live' ? 'Live Mode Active' : 'Switch to Live Trading'}
          </button>
        ) : (
          <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4 space-y-3">
            <p className="text-sm text-red-300 font-medium">
              WARNING: You are about to enable LIVE trading with real funds.
              This will execute real trades on Robinhood.
            </p>
            <div className="flex gap-2">
              <button
                className="btn-danger"
                onClick={() => {
                  startSession.mutate({ mode: 'live' })
                  setShowLiveConfirm(false)
                }}
              >
                Confirm: Go Live
              </button>
              <button
                className="px-4 py-2 rounded-lg bg-gray-800 text-gray-300"
                onClick={() => setShowLiveConfirm(false)}
              >
                Cancel
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
