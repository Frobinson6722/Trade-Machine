import { XAxis, YAxis, Tooltip, ResponsiveContainer, Area, AreaChart } from 'recharts'
import type { EquityCurvePoint } from '../lib/types'

interface Props {
  data: EquityCurvePoint[]
}

export default function EquityCurve({ data }: Props) {
  if (!data.length) {
    return (
      <div className="card h-64 flex items-center justify-center text-muted">
        No equity data yet. Start trading to see your equity curve.
      </div>
    )
  }

  const formatted = data.map((p) => ({
    time: new Date(p.timestamp).toLocaleDateString(),
    value: p.value,
  }))

  const startValue = formatted[0]?.value ?? 0
  const endValue = formatted[formatted.length - 1]?.value ?? 0
  const isProfit = endValue >= startValue

  return (
    <div className="card">
      <h3 className="text-sm font-medium text-muted mb-4">Equity Curve</h3>
      <ResponsiveContainer width="100%" height={250}>
        <AreaChart data={formatted}>
          <defs>
            <linearGradient id="equityGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={isProfit ? 'var(--profit)' : 'var(--loss)'} stopOpacity={0.3} />
              <stop offset="100%" stopColor={isProfit ? 'var(--profit)' : 'var(--loss)'} stopOpacity={0} />
            </linearGradient>
          </defs>
          <XAxis dataKey="time" tick={{ fontSize: 11, fill: 'var(--text-faint)' }} />
          <YAxis tick={{ fontSize: 11, fill: 'var(--text-faint)' }} domain={['auto', 'auto']} />
          <Tooltip
            contentStyle={{
              backgroundColor: 'var(--bg-secondary)',
              border: '1px solid var(--border-primary)',
              borderRadius: 8,
              color: 'var(--text-primary)',
            }}
            labelStyle={{ color: 'var(--text-muted)' }}
            formatter={(value: number) => [`$${value.toFixed(2)}`, 'Portfolio']}
          />
          <Area
            type="monotone"
            dataKey="value"
            stroke={isProfit ? 'var(--profit)' : 'var(--loss)'}
            fill="url(#equityGrad)"
            strokeWidth={2}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}
