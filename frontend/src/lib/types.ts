// TypeScript interfaces matching backend Pydantic schemas

export interface Trade {
  id: number
  cycle_id: string
  pair: string
  side: string
  size_usd: number
  entry_price: number
  exit_price: number | null
  stop_loss: number | null
  take_profit: number | null
  status: string
  pnl: number | null
  pnl_pct: number | null
  stage: string
  mode: string
  exit_trigger: string | null
  opened_at: string
  closed_at: string | null
}

export interface TradeListResponse {
  trades: Trade[]
  total: number
}

export interface AgentLog {
  id: number
  cycle_id: string
  agent_name: string
  agent_type: string
  content: string
  created_at: string
}

export interface AgentLogListResponse {
  logs: AgentLog[]
  total: number
}

export interface Position {
  pair: string
  entry_price: number
  current_price: number
  quantity: number
  unrealized_pnl: number
  unrealized_pnl_pct: number
}

export interface Portfolio {
  total_value: number
  cash_balance: number
  positions: Position[]
  unrealized_pnl: number
  realized_pnl: number
}

export interface EquityCurvePoint {
  timestamp: string
  value: number
}

export interface Reflection {
  id: number
  pair: string
  reflection_text: string
  tags: string[]
  trade_outcome: string
  created_at: string
}

export interface Hypothesis {
  id: number
  pair: string
  hypothesis: string
  status: string
  test_results: string | null
  rule_change: string | null
  created_at: string
}

export interface StrategyUpdate {
  id: number
  description: string
  parameter_changes: Record<string, unknown>
  old_values: Record<string, unknown> | null
  created_at: string
}

export interface LearningData {
  reflections: Reflection[]
  hypotheses: Hypothesis[]
  strategy_updates: StrategyUpdate[]
  current_parameters: Record<string, unknown>
}

export interface SessionStatus {
  running: boolean
  paused: boolean
  mode: string
  stage: {
    current_stage: string
    graduated_level: number | null
    trade_size_usd: number | null
    trades_completed: number
    win_rate: number
    total_pnl: number
    graduation_check: {
      eligible: boolean
      details: string
    }
  }
  positions: Record<string, unknown>
  stats: {
    total: number
    wins: number
    losses: number
    win_rate: number
    total_pnl: number
    avg_pnl: number
  }
}

export interface Settings {
  llm_provider: string
  llm_model: string
  trading_pairs: string[]
  cycle_interval_seconds: number
  max_position_size_pct: number
  max_portfolio_allocation_pct: number
  default_stop_loss_pct: number
  default_take_profit_pct: number
  current_stage: string
  mode: string
}

export interface WSMessage {
  type: 'trade_update' | 'agent_activity' | 'pnl_tick' | 'status_change' | 'heartbeat' | 'pong'
  data?: Record<string, unknown>
}
