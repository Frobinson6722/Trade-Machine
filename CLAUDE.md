# Trade Machine

Autonomous crypto trading bot. Rules-based engine (no LLM costs for trades).

## Architecture

- **Backend:** FastAPI + SQLAlchemy + SQLite (`backend/`)
- **Engine:** Pure math trading engine (`engine/rules_engine.py`)
- **Frontend:** React 18 + TypeScript + Vite + Tailwind (`frontend/`)
- **Data:** CoinGecko free API for prices, no paid APIs needed

## How to Run

```bash
cd ~/Trade-Machine
kill $(lsof -ti:8000) 2>/dev/null
PYTHONPATH=. python3 -m uvicorn backend.main:app --port 8000 --log-level warning &
cd frontend && npm run dev
```

Open http://localhost:3000, click Start.

## Trading Strategy

Rules-based engine using RSI, MACD, Bollinger Bands, Volume, SMA trends.
- Scores each signal, needs score >= 3 to buy
- Take profit: 0.5% | Stop loss: 0.4% | Trailing stop after 0.15% gain
- 60-second scan cycles on XRP-USD
- Learning loop every 10 cycles adjusts thresholds based on win rate
- Lessons saved to `reflections` table in DB
- Zero API cost per trade

## User Preferences

- **Timestamps:** Always EST (America/New_York)
- **UI:** Minimal. Dashboard = big P&L number + trade list. No noise.
- **Costs:** Must stay under $1.50/day. Currently $0/day (rules-based).
- **Coins:** XRP-USD primary
- **No emojis** in code or UI

## Key Files

| File | Purpose |
|------|---------|
| `engine/rules_engine.py` | Core trading logic, scoring, trailing stops, learning loop |
| `engine/dataflows/technical_indicators.py` | RSI, MACD, Bollinger, ATR, SMA calculations |
| `engine/dataflows/free_market_provider.py` | CoinGecko price data with caching |
| `engine/execution/paper_trader.py` | Paper trading simulator |
| `backend/services/trade_logger.py` | Persists trades to DB, handles BUY/SELL events |
| `backend/services/engine_bridge.py` | Connects FastAPI to RulesEngine |
| `frontend/src/pages/Dashboard.tsx` | Main UI — P&L total + trade list |
| `frontend/src/pages/AgentsPage.tsx` | Trade Decisions view |
| `frontend/src/pages/MorePage.tsx` | Settings, API costs, learning, release notes |

## Database

SQLite at `./trade_machine.db`. Key tables:
- `trades` — every BUY/SELL with P&L
- `reflections` — lessons learned from each trade
- `strategy_updates` — threshold changes from learning loop

## Dev Branch

Develop on: `claude/push-trade-machine-VALeg`

## Known Issues

- User's Mac terminal adds `^[[200~` when pasting — must type commands manually
- Backend logs flood terminal if not using `--log-level warning`
- On engine restart, stale open trades auto-close at $0 P&L
