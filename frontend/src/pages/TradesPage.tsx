import { useState } from 'react'
import { useTrades } from '../hooks/useApi'
import TradeTable from '../components/TradeTable'

export default function TradesPage() {
  const [pair, setPair] = useState<string>('')
  const [status, setStatus] = useState<string>('')
  const [page, setPage] = useState(0)
  const limit = 25

  const { data, isLoading } = useTrades({
    pair: pair || undefined,
    status: status || undefined,
    limit,
    offset: page * limit,
  })

  const totalPages = Math.ceil((data?.total ?? 0) / limit)

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Trade History</h2>

      {/* Filters */}
      <div className="flex gap-3">
        <select
          className="input"
          value={pair}
          onChange={(e) => { setPair(e.target.value); setPage(0) }}
        >
          <option value="">All Pairs</option>
          <option value="BTC-USD">BTC-USD</option>
          <option value="ETH-USD">ETH-USD</option>
          <option value="SOL-USD">SOL-USD</option>
          <option value="DOGE-USD">DOGE-USD</option>
        </select>

        <select
          className="input"
          value={status}
          onChange={(e) => { setStatus(e.target.value); setPage(0) }}
        >
          <option value="">All Statuses</option>
          <option value="open">Open</option>
          <option value="closed">Closed</option>
        </select>
      </div>

      {/* Table */}
      {isLoading ? (
        <div className="text-gray-500">Loading trades...</div>
      ) : (
        <TradeTable trades={data?.trades ?? []} />
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-2">
          <button
            className="px-3 py-1 rounded bg-gray-800 text-gray-400 hover:text-white disabled:opacity-50"
            disabled={page === 0}
            onClick={() => setPage(page - 1)}
          >
            Previous
          </button>
          <span className="text-sm text-gray-500">
            Page {page + 1} of {totalPages}
          </span>
          <button
            className="px-3 py-1 rounded bg-gray-800 text-gray-400 hover:text-white disabled:opacity-50"
            disabled={page >= totalPages - 1}
            onClick={() => setPage(page + 1)}
          >
            Next
          </button>
        </div>
      )}
    </div>
  )
}
