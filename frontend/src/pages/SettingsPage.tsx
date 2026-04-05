import { useState, useEffect } from 'react'
import { useSettings, useUpdateSettings, useStartSession, useStopSession } from '../hooks/useApi'
import { Settings as SettingsIcon, AlertTriangle } from 'lucide-react'

export default function SettingsPage() {
  const { data: settings, isLoading } = useSettings()
  const updateSettings = useUpdateSettings()
  const startSession = useStartSession()
  const stopSession = useStopSession()

  const [form, setForm] = useState({
    llm_model: 'claude-sonnet-4-20250514',
    trading_pairs: 'BTC-USD,ETH-USD',
    cycle_interval_seconds: 900,
    max_position_size_pct: 5,
    max_portfolio_allocation_pct: 25,
    default_stop_loss_pct: 3,
    default_take_profit_pct: 6,
  })

  const [showLiveConfirm, setShowLiveConfirm] = useState(false)

  useEffect(() => {
    if (settings) {
      setForm({
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
      llm_provider: 'anthropic',
      llm_model: form.llm_model,
      trading_pairs: form.trading_pairs.split(',').map((s) => s.trim()),
      cycle_interval_seconds: form.cycle_interval_seconds,
      max_position_size_pct: form.max_position_size_pct,
      max_portfolio_allocation_pct: form.max_portfolio_allocation_pct,
      default_stop_loss_pct: form.default_stop_loss_pct,
      default_take_profit_pct: form.default_take_profit_pct,
    })
  }

  if (isLoading) return <div className="text-faint">Loading settings...</div>

  return (
    <div className="space-y-6 max-w-2xl">
      <div className="flex items-center gap-3">
        <SettingsIcon className="w-6 h-6 text-accent" />
        <h2 className="text-2xl font-bold text-primary">Settings</h2>
      </div>

      {/* Claude Model */}
      <div className="card space-y-3">
        <h3 className="font-medium">Claude AI Configuration</h3>
        <p className="text-xs text-faint">Powered by Anthropic Claude. Set your API key in the .env file.</p>
        <div>
          <label className="text-sm text-muted block mb-1">Claude Model</label>
          <select
            className="input w-full"
            value={form.llm_model}
            onChange={(e) => setForm({ ...form, llm_model: e.target.value })}
          >
            <option value="claude-sonnet-4-20250514">Claude Sonnet 4 (recommended)</option>
            <option value="claude-opus-4-20250514">Claude Opus 4 (most capable)</option>
            <option value="claude-haiku-4-5-20251001">Claude Haiku 4.5 (fastest)</option>
          </select>
        </div>
      </div>

      {/* Trading Settings */}
      <div className="card space-y-3">
        <h3 className="font-medium">Trading Configuration</h3>
        <div>
          <label className="text-sm text-muted block mb-1">Trading Pairs (comma-separated)</label>
          <input
            className="input w-full"
            value={form.trading_pairs}
            onChange={(e) => setForm({ ...form, trading_pairs: e.target.value })}
          />
        </div>
        <div>
          <label className="text-sm text-muted block mb-1">
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
            <label className="text-sm text-muted block mb-1">Max Position Size (%)</label>
            <input
              type="number"
              className="input w-full"
              value={form.max_position_size_pct}
              onChange={(e) => setForm({ ...form, max_position_size_pct: Number(e.target.value) })}
            />
          </div>
          <div>
            <label className="text-sm text-muted block mb-1">Max Portfolio Allocation (%)</label>
            <input
              type="number"
              className="input w-full"
              value={form.max_portfolio_allocation_pct}
              onChange={(e) => setForm({ ...form, max_portfolio_allocation_pct: Number(e.target.value) })}
            />
          </div>
          <div>
            <label className="text-sm text-muted block mb-1">Default Stop Loss (%)</label>
            <input
              type="number"
              className="input w-full"
              value={form.default_stop_loss_pct}
              onChange={(e) => setForm({ ...form, default_stop_loss_pct: Number(e.target.value) })}
            />
          </div>
          <div>
            <label className="text-sm text-muted block mb-1">Default Take Profit (%)</label>
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
      <div className="card border-red-300">
        <div className="flex items-center gap-2 mb-3">
          <AlertTriangle className="w-5 h-5 text-red-500" />
          <h3 className="font-medium text-red-600">Live Trading</h3>
        </div>
        <p className="text-sm text-muted mb-3">
          Current mode: <span className="font-medium text-primary font-semibold">{settings?.mode ?? 'paper'}</span>
          {' | '}
          Stage: <span className="font-medium text-primary font-semibold">{settings?.current_stage ?? 'paper'}</span>
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
            <p className="text-sm text-red-700 font-medium">
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
                className="px-4 py-2 rounded-lg bg-surface-tertiary text-secondary"
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
