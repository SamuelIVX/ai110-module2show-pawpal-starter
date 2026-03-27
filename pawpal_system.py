from dataclasses import dataclass, field
from typing import List


@dataclass
class Pet:
    name: str
    species: str  # "dog", "cat", "other"

    def to_dict(self) -> dict:
        pass


@dataclass
class Owner:
    name: str
    available_minutes: int

    def to_dict(self) -> dict:
        pass


PRIORITY_MAP = {"low": 1, "medium": 2, "high": 3}


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str  # "low", "medium", "high"

    def priority_rank(self) -> int:
        """Convert priority string to int for sorting (high=3, medium=2, low=1)."""
        return PRIORITY_MAP.get(self.priority, 0)

    def to_dict(self) -> dict:
        pass


@dataclass
class Schedule:
    planned_tasks: List[Task] = field(default_factory=list)
    skipped_tasks: List[Task] = field(default_factory=list)
    total_minutes_used: int = 0
    reasoning: str = ""

    def summary(self) -> str:
        """Return a formatted string of the schedule for display in the UI."""
        pass


class Scheduler:
    def __init__(self, owner: Owner, pet: Pet, tasks: List[Task]):
        self.owner = owner
        self.pet = pet
        self.tasks = tasks

    def generate_schedule(self) -> Schedule:
        """Sort tasks by priority, fit them within the owner's time budget, return a Schedule."""
        pass

    def _rank_tasks(self) -> List[Task]:
        """Return tasks sorted by priority rank descending."""
        pass
