"""Trade journal — structured log of every trade with full agent reasoning."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)


class TradeJournal:
    """Records every trade with entry/exit, reasoning, and outcome."""

    def __init__(self):
        self.entries: list[dict[str, Any]] = []

    def record_entry(
        self,
        pair: str,
        action: str,
        entry_price: float,
        size_usd: float,
        stop_loss: float | None,
        take_profit: float | None,
        agent_reasoning: dict[str, str],
        stage: str,
        cycle_id: str,
    ) -> dict[str, Any]:
        """Record a new trade entry."""
        entry = {
            "cycle_id": cycle_id,
            "pair": pair,
            "action": action,
            "entry_price": entry_price,
            "size_usd": size_usd,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "agent_reasoning": agent_reasoning,
            "stage": stage,
            "opened_at": datetime.now(timezone.utc).isoformat(),
            "status": "open",
            "exit_price": None,
            "pnl": None,
            "pnl_pct": None,
            "closed_at": None,
            "reflection": None,
        }
        self.entries.append(entry)
        logger.info(f"Journal: recorded {action} entry for {pair} @ ${entry_price:,.2f}")
        return entry

    def record_exit(
        self,
        cycle_id: str,
        exit_price: float,
        pnl: float,
        pnl_pct: float,
        trigger: str = "manual",
    ) -> dict[str, Any] | None:
        """Record a trade exit and calculate outcome."""
        for entry in reversed(self.entries):
            if entry["cycle_id"] == cycle_id and entry["status"] == "open":
                entry["exit_price"] = exit_price
                entry["pnl"] = pnl
                entry["pnl_pct"] = pnl_pct
                entry["closed_at"] = datetime.now(timezone.utc).isoformat()
                entry["status"] = "closed"
                entry["exit_trigger"] = trigger
                logger.info(f"Journal: recorded exit for {entry['pair']} (P&L: ${pnl:+,.2f})")
                return entry
        return None

    def add_reflection(self, cycle_id: str, reflection: str) -> None:
        """Attach a reflection to a closed trade."""
        for entry in reversed(self.entries):
            if entry["cycle_id"] == cycle_id:
                entry["reflection"] = reflection
                break

    def get_recent_trades(self, limit: int = 20) -> list[dict[str, Any]]:
        return self.entries[-limit:]

    def get_trades_by_pair(self, pair: str) -> list[dict[str, Any]]:
        return [e for e in self.entries if e["pair"] == pair]

    def get_losing_trades(self, limit: int = 10) -> list[dict[str, Any]]:
        return [e for e in self.entries if e.get("pnl", 0) and e["pnl"] < 0][-limit:]

    def get_winning_trades(self, limit: int = 10) -> list[dict[str, Any]]:
        return [e for e in self.entries if e.get("pnl", 0) and e["pnl"] > 0][-limit:]

    def get_todays_trades(self) -> list[dict[str, Any]]:
        today = datetime.now(timezone.utc).date().isoformat()
        return [
            e for e in self.entries
            if e.get("opened_at", "").startswith(today)
        ]

    def get_stats(self) -> dict[str, Any]:
        closed = [e for e in self.entries if e["status"] == "closed"]
        if not closed:
            return {"total": 0, "win_rate": 0, "total_pnl": 0}

        wins = sum(1 for t in closed if t.get("pnl", 0) > 0)
        total_pnl = sum(t.get("pnl", 0) for t in closed)

        return {
            "total": len(closed),
            "open": len(self.entries) - len(closed),
            "wins": wins,
            "losses": len(closed) - wins,
            "win_rate": wins / len(closed),
            "total_pnl": total_pnl,
            "avg_pnl": total_pnl / len(closed),
        }
