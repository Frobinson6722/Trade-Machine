"""Reflection store — tagged storage for agent reflections and lessons learned."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)


class ReflectionStore:
    """Stores and retrieves agent reflections, indexed by tags for similarity lookup."""

    def __init__(self):
        self.reflections: list[dict[str, Any]] = []

    def store(
        self,
        pair: str,
        reflection: str,
        tags: list[str],
        trade_outcome: str,
        agent_name: str = "system",
    ) -> dict[str, Any]:
        """Store a new reflection with searchable tags."""
        entry = {
            "id": len(self.reflections),
            "pair": pair,
            "reflection": reflection,
            "tags": tags,
            "trade_outcome": trade_outcome,
            "agent_name": agent_name,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self.reflections.append(entry)
        logger.info(f"Stored reflection for {pair} with tags: {tags}")
        return entry

    def search(
        self,
        pair: str | None = None,
        tags: list[str] | None = None,
        outcome: str | None = None,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        """Search reflections by pair, tags, or outcome.

        Returns the most relevant reflections (most tag matches first).
        """
        results = []
        for r in self.reflections:
            score = 0
            if pair and r["pair"] == pair:
                score += 2
            if tags:
                matching_tags = set(tags) & set(r["tags"])
                score += len(matching_tags)
            if outcome and r["trade_outcome"] == outcome:
                score += 1

            if score > 0:
                results.append((score, r))

        results.sort(key=lambda x: x[0], reverse=True)
        return [r for _, r in results[:limit]]

    def get_lessons_for_pair(self, pair: str, limit: int = 5) -> list[str]:
        """Get formatted lesson strings for a specific pair."""
        relevant = self.search(pair=pair, limit=limit)
        return [r["reflection"] for r in relevant]

    def get_all(self) -> list[dict[str, Any]]:
        return list(self.reflections)

    def get_recent(self, limit: int = 10) -> list[dict[str, Any]]:
        return self.reflections[-limit:]
