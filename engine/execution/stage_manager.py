"""Three-stage risk escalation manager."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class StageManager:
    """Manages the three-stage risk escalation: paper → micro → graduated."""

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.current_stage = "paper"
        self.current_graduated_level = 0  # Index into graduated sizes

        # Per-stage statistics
        self.stage_stats: dict[str, dict[str, Any]] = {
            "paper": {"trades": 0, "wins": 0, "total_pnl": 0.0},
            "micro": {"trades": 0, "wins": 0, "total_pnl": 0.0},
            "graduated": {"trades": 0, "wins": 0, "total_pnl": 0.0, "level_trades": 0},
        }

    def get_current_stage(self) -> str:
        return self.current_stage

    def get_trade_size_usd(self) -> float | None:
        """Get the fixed trade size for the current stage, or None for paper (pct-based)."""
        if self.current_stage == "paper":
            return None  # Paper uses percentage-based sizing
        elif self.current_stage == "micro":
            return self.config["stages"]["micro"]["trade_size_usd"]
        elif self.current_stage == "graduated":
            sizes = self.config["stages"]["graduated"]["sizes_usd"]
            idx = min(self.current_graduated_level, len(sizes) - 1)
            return sizes[idx]
        return None

    def record_trade(self, pnl: float) -> None:
        """Record a completed trade and check for stage graduation."""
        stats = self.stage_stats[self.current_stage]
        stats["trades"] += 1
        stats["total_pnl"] += pnl
        if pnl > 0:
            stats["wins"] += 1
        if self.current_stage == "graduated":
            stats["level_trades"] = stats.get("level_trades", 0) + 1

    def check_graduation(self) -> dict[str, Any]:
        """Check if the current stage meets graduation criteria.

        Returns a dict with 'eligible' (bool) and 'details' (str).
        """
        stats = self.stage_stats[self.current_stage]
        trades = stats["trades"]
        win_rate = stats["wins"] / trades if trades > 0 else 0

        if self.current_stage == "paper":
            stage_cfg = self.config["stages"]["paper"]
            min_trades = stage_cfg["min_trades_to_graduate"]
            min_wr = stage_cfg["min_win_rate"]

            if trades >= min_trades and win_rate >= min_wr:
                return {
                    "eligible": True,
                    "next_stage": "micro",
                    "details": f"Paper: {trades} trades, {win_rate:.1%} win rate (min: {min_trades}, {min_wr:.0%})",
                }
            return {
                "eligible": False,
                "details": f"Paper: {trades}/{min_trades} trades, {win_rate:.1%}/{min_wr:.0%} win rate",
            }

        elif self.current_stage == "micro":
            stage_cfg = self.config["stages"]["micro"]
            min_trades = stage_cfg["min_trades_to_graduate"]
            min_wr = stage_cfg["min_win_rate"]

            if trades >= min_trades and win_rate >= min_wr:
                return {
                    "eligible": True,
                    "next_stage": "graduated",
                    "details": f"Micro: {trades} trades, {win_rate:.1%} win rate",
                }
            return {
                "eligible": False,
                "details": f"Micro: {trades}/{min_trades} trades, {win_rate:.1%}/{min_wr:.0%} win rate",
            }

        elif self.current_stage == "graduated":
            stage_cfg = self.config["stages"]["graduated"]
            sizes = stage_cfg["sizes_usd"]
            trades_per = stage_cfg["trades_per_level"]
            min_wr = stage_cfg["min_win_rate"]
            level_trades = stats.get("level_trades", 0)

            if self.current_graduated_level < len(sizes) - 1:
                if level_trades >= trades_per and win_rate >= min_wr:
                    return {
                        "eligible": True,
                        "next_stage": "graduated",
                        "next_level": self.current_graduated_level + 1,
                        "next_size": sizes[min(self.current_graduated_level + 1, len(sizes) - 1)],
                        "details": f"Graduated level {self.current_graduated_level}: ready to scale up",
                    }
            return {
                "eligible": False,
                "details": f"Graduated level {self.current_graduated_level}: {level_trades}/{trades_per} trades at ${sizes[min(self.current_graduated_level, len(sizes)-1)]}",
            }

        return {"eligible": False, "details": "Unknown stage"}

    def graduate(self) -> str:
        """Advance to the next stage. Returns the new stage name."""
        check = self.check_graduation()
        if not check["eligible"]:
            raise ValueError(f"Not eligible for graduation: {check['details']}")

        if self.current_stage == "paper":
            self.current_stage = "micro"
            logger.info("STAGE GRADUATION: Paper → Micro ($1 trades)")
        elif self.current_stage == "micro":
            self.current_stage = "graduated"
            self.current_graduated_level = 0
            logger.info("STAGE GRADUATION: Micro → Graduated ($2 trades)")
        elif self.current_stage == "graduated":
            self.current_graduated_level += 1
            sizes = self.config["stages"]["graduated"]["sizes_usd"]
            size = sizes[min(self.current_graduated_level, len(sizes) - 1)]
            self.stage_stats["graduated"]["level_trades"] = 0
            logger.info(f"STAGE GRADUATION: Graduated level up → ${size} trades")

        return self.current_stage

    def get_status(self) -> dict[str, Any]:
        """Get full stage status for the dashboard."""
        stats = self.stage_stats[self.current_stage]
        trades = stats["trades"]
        win_rate = stats["wins"] / trades if trades > 0 else 0

        return {
            "current_stage": self.current_stage,
            "graduated_level": self.current_graduated_level if self.current_stage == "graduated" else None,
            "trade_size_usd": self.get_trade_size_usd(),
            "trades_completed": trades,
            "win_rate": win_rate,
            "total_pnl": stats["total_pnl"],
            "graduation_check": self.check_graduation(),
            "all_stage_stats": self.stage_stats,
        }
