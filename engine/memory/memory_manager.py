"""Memory manager — coordinates all memory subsystems and provides context to agents."""

from __future__ import annotations

import logging
from typing import Any

from engine.memory.trade_journal import TradeJournal
from engine.memory.reflection_store import ReflectionStore
from engine.memory.hypothesis_engine import HypothesisEngine
from engine.memory.strategy_tracker import StrategyTracker
from engine.memory.nightly_learner import NightlyLearner

logger = logging.getLogger(__name__)


class MemoryManager:
    """Central coordinator for all memory subsystems."""

    def __init__(self):
        self.journal = TradeJournal()
        self.reflections = ReflectionStore()
        self.hypotheses = HypothesisEngine()
        self.strategy = StrategyTracker()
        self.nightly_learner = NightlyLearner(
            self.journal, self.hypotheses, self.strategy
        )

    def get_context_for_pair(self, pair: str) -> list[str]:
        """Get relevant memory context for a trading cycle on a specific pair.

        Combines recent reflections, validated hypotheses, and strategy notes.
        """
        context = []

        # Recent reflections for this pair
        lessons = self.reflections.get_lessons_for_pair(pair, limit=3)
        context.extend(lessons)

        # Validated hypotheses
        for h in self.hypotheses.get_validated()[-3:]:
            if h.get("pair") == pair or not h.get("pair"):
                context.append(f"Validated insight: {h['hypothesis']}")

        # Recent strategy changes
        for update in self.strategy.get_updates(limit=3):
            context.append(f"Strategy update: {update['description']}")

        return context

    def record_trade_entry(self, **kwargs) -> dict[str, Any]:
        """Record a new trade in the journal."""
        return self.journal.record_entry(**kwargs)

    def record_trade_exit(self, **kwargs) -> dict[str, Any] | None:
        """Record a trade exit."""
        return self.journal.record_exit(**kwargs)

    def store_reflection(
        self,
        pair: str,
        reflection: str,
        tags: list[str],
        trade_outcome: str,
    ) -> None:
        """Store a reflection from post-trade analysis."""
        self.reflections.store(pair, reflection, tags, trade_outcome)

    def store_hypotheses(self, pair: str, trade_id: str, hypotheses_text: str) -> None:
        """Parse and store hypotheses from loss analysis."""
        # Split by "HYPOTHESIS:" markers
        parts = hypotheses_text.split("HYPOTHESIS:")
        for part in parts[1:]:  # Skip the preamble
            hypothesis = part.strip().split("\n")[0].strip()
            if hypothesis:
                self.hypotheses.store_hypothesis(pair, trade_id, hypothesis)

    def get_trading_stats(self) -> dict[str, Any]:
        """Get comprehensive trading statistics."""
        journal_stats = self.journal.get_stats()
        strategy_params = self.strategy.get_current_parameters()

        return {
            **journal_stats,
            "total_reflections": len(self.reflections.get_all()),
            "total_hypotheses": len(self.hypotheses.get_all()),
            "validated_hypotheses": len(self.hypotheses.get_validated()),
            "strategy_updates": len(self.strategy.get_updates()),
            "current_strategy": strategy_params,
        }

    def get_learning_data(self) -> dict[str, Any]:
        """Get all learning-related data for the dashboard."""
        return {
            "reflections": self.reflections.get_recent(20),
            "hypotheses": self.hypotheses.get_all(),
            "strategy_updates": self.strategy.get_updates(20),
            "current_parameters": self.strategy.get_current_parameters(),
        }
