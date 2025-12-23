import json
import os
import re
from dataclasses import dataclass
from datetime import datetime
from difflib import SequenceMatcher
from typing import Dict, List, Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from .model import Task


@dataclass(frozen=True)
class GoalMemoryMatch:
    name: str
    value: float
    time: float
    score: float


class GoalMemory:
    """Persist and match previously-scored goals using inexact text matching."""

    _CONTAINS_BONUS = 0.08
    _MAX_ENTRIES = 1000

    def __init__(self, storage_path: Optional[str] = None):
        self._storage_path = storage_path or self._default_storage_path()
        self._entries: Dict[str, Dict[str, object]] = {}
        self._load()

    def _default_storage_path(self) -> str:
        base_dir = os.path.join(os.path.expanduser("~"), ".priorityplot")
        return os.path.join(base_dir, "goal_memory.json")

    def _normalize(self, text: str) -> str:
        cleaned = text.lower()
        cleaned = re.sub(r"[^\w\s]", " ", cleaned)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        return cleaned

    def _min_score_for(self, a: str, b: str) -> float:
        max_len = max(len(a), len(b))
        if max_len <= 6:
            return 0.92
        if max_len <= 12:
            return 0.86
        return 0.80

    def _load(self) -> None:
        if not os.path.exists(self._storage_path):
            return
        try:
            with open(self._storage_path, "r", encoding="utf-8") as handle:
                data = json.load(handle)
            entries = data.get("entries", [])
            for entry in entries:
                normalized = entry.get("normalized")
                if not normalized:
                    continue
                self._entries[normalized] = entry
        except Exception:
            self._entries = {}

    def _save(self) -> None:
        storage_dir = os.path.dirname(self._storage_path)
        if storage_dir:
            os.makedirs(storage_dir, exist_ok=True)
        entries = list(self._entries.values())
        entries.sort(key=lambda item: item.get("updated_at", ""), reverse=True)
        entries = entries[: self._MAX_ENTRIES]
        payload = {"entries": entries}
        tmp_path = f"{self._storage_path}.tmp"
        with open(tmp_path, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2)
        os.replace(tmp_path, self._storage_path)

    def find_match(self, task_name: str) -> Optional[GoalMemoryMatch]:
        normalized = self._normalize(task_name)
        if not normalized or not self._entries:
            return None
        exact = self._entries.get(normalized)
        if exact:
            return GoalMemoryMatch(
                name=str(exact.get("name", task_name)),
                value=float(exact.get("value", 0.0)),
                time=float(exact.get("time", 0.0)),
                score=1.0,
            )

        best_entry = None
        best_score = 0.0
        for entry in self._entries.values():
            entry_norm = entry.get("normalized", "")
            if not entry_norm:
                continue
            score = SequenceMatcher(None, normalized, entry_norm).ratio()
            if normalized in entry_norm or entry_norm in normalized:
                score = min(1.0, score + self._CONTAINS_BONUS)
            if score > best_score:
                best_score = score
                best_entry = entry

        if not best_entry:
            return None

        min_score = self._min_score_for(normalized, str(best_entry.get("normalized", "")))
        if best_score < min_score:
            return None

        return GoalMemoryMatch(
            name=str(best_entry.get("name", task_name)),
            value=float(best_entry.get("value", 0.0)),
            time=float(best_entry.get("time", 0.0)),
            score=best_score,
        )

    def update_from_tasks(self, tasks: List["Task"], save: bool = True) -> None:
        updated = False
        now = datetime.utcnow().isoformat()
        for task in tasks:
            normalized = self._normalize(task.task)
            if not normalized:
                continue
            existing = self._entries.get(normalized)
            entry = {
                "name": task.task,
                "normalized": normalized,
                "value": float(task.value),
                "time": float(task.time),
                "updated_at": now,
            }
            if existing != entry:
                self._entries[normalized] = entry
                updated = True

        if updated and save:
            self._save()
