from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import List, Optional


PRIORITY_MAP = {"low": 1, "medium": 2, "high": 3}


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str                    # "low", "medium", "high"
    frequency: str = "daily"         # "daily", "weekly", "as-needed"
    completed: bool = False
    due_date: date = field(default_factory=date.today)

    def priority_rank(self) -> int:
        """Convert priority string to int for sorting (high=3, medium=2, low=1)."""
        return PRIORITY_MAP.get(self.priority, 0)

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def next_occurrence(self) -> Optional["Task"]:
        """
        Return a new pending Task scheduled for the next occurrence based on frequency.
        Returns None for 'as-needed' tasks since they don't recur on a fixed schedule.
        """
        if self.frequency == "daily":
            next_due = self.due_date + timedelta(days=1)
        elif self.frequency == "weekly":
            next_due = self.due_date + timedelta(weeks=1)
        else:
            return None  # "as-needed" tasks do not auto-recur

        return Task(
            title=self.title,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            frequency=self.frequency,
            completed=False,
            due_date=next_due,
        )

    def to_dict(self) -> dict:
        """Serialize this task to a plain dictionary."""
        return {
            "title": self.title,
            "duration_minutes": self.duration_minutes,
            "priority": self.priority,
            "frequency": self.frequency,
            "completed": self.completed,
            "due_date": self.due_date.isoformat(),
        }


@dataclass
class Pet:
    name: str
    species: str            # "dog", "cat", "other"
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task to this pet's task list."""
        self.tasks.append(task)

    def get_tasks(self) -> List[Task]:
        """Return all tasks assigned to this pet."""
        return self.tasks

    def complete_task(self, task: Task) -> Optional[Task]:
        """
        Mark a task complete and, if it recurs, add the next occurrence to this pet's list.
        Returns the newly created Task, or None if the task does not recur.
        """
        task.mark_complete()
        next_task = task.next_occurrence()
        if next_task:
            self.add_task(next_task)
        return next_task

    def to_dict(self) -> dict:
        """Serialize this pet and its tasks to a plain dictionary."""
        return {
            "name": self.name,
            "species": self.species,
            "tasks": [t.to_dict() for t in self.tasks],
        }


@dataclass
class Owner:
    name: str
    available_minutes: int
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's roster."""
        self.pets.append(pet)

    def get_all_tasks(self) -> List[Task]:
        """Collect and return every task across all pets."""
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.get_tasks())
        return all_tasks

    def get_tasks_for_pet(self, pet_name: str) -> List[Task]:
        """Return tasks belonging to the pet with the given name (case-insensitive)."""
        for pet in self.pets:
            if pet.name.lower() == pet_name.lower():
                return pet.get_tasks()
        return []

    def to_dict(self) -> dict:
        """Serialize this owner and all their pets to a plain dictionary."""
        return {
            "name": self.name,
            "available_minutes": self.available_minutes,
            "pets": [p.to_dict() for p in self.pets],
        }


@dataclass
class Schedule:
    planned_tasks: List[Task] = field(default_factory=list)
    skipped_tasks: List[Task] = field(default_factory=list)
    total_minutes_used: int = 0
    reasoning: str = ""

    def summary(self) -> str:
        """Return a formatted string of the schedule for display in the UI."""
        lines = ["### Today's Plan\n"]

        if self.planned_tasks:
            for task in self.planned_tasks:
                status = "✓" if task.completed else "○"
                lines.append(
                    f"  {status} [{task.priority.upper()}] {task.title} — {task.duration_minutes} min"
                )
        else:
            lines.append("  No tasks scheduled.")

        lines.append(f"\n**Total time:** {self.total_minutes_used} min")

        if self.skipped_tasks:
            lines.append("\n### Skipped (not enough time)")
            for task in self.skipped_tasks:
                lines.append(f"  - {task.title} ({task.duration_minutes} min)")

        lines.append(f"\n### Reasoning\n{self.reasoning}")
        return "\n".join(lines)


class Scheduler:
    def __init__(self, owner: Owner):
        """Initialize the scheduler with an owner whose pets and tasks will be scheduled."""
        self.owner = owner

    def generate_schedule(self) -> Schedule:
        """
        Retrieve all tasks from the owner's pets, filter out completed ones,
        sort by priority, fit within available_minutes, and return a Schedule.
        """
        all_tasks = self.owner.get_all_tasks()

        if not all_tasks:
            return Schedule(reasoning="No tasks found across any pets.")

        pending = [t for t in all_tasks if not t.completed]
        ranked = self._rank_tasks(pending)

        planned = []
        skipped = []
        minutes_remaining = self.owner.available_minutes

        for task in ranked:
            if task.duration_minutes <= minutes_remaining:
                planned.append(task)
                minutes_remaining -= task.duration_minutes
            else:
                skipped.append(task)

        total_used = self.owner.available_minutes - minutes_remaining
        reasoning = self._build_reasoning(planned, skipped, total_used)

        return Schedule(
            planned_tasks=planned,
            skipped_tasks=skipped,
            total_minutes_used=total_used,
            reasoning=reasoning,
        )

    def mark_task_complete(self, task: Task) -> Optional[Task]:
        """
        Find which pet owns the task, delegate completion to Pet.complete_task(),
        and return the next occurrence if one was created.
        """
        for pet in self.owner.pets:
            if task in pet.get_tasks():
                return pet.complete_task(task)
        return None

    def sort_by_duration(self, tasks: List[Task]) -> List[Task]:
        """Return tasks sorted by duration ascending (shortest first)."""
        return sorted(tasks, key=lambda t: t.duration_minutes)

    def filter_tasks(
        self,
        tasks: List[Task],
        completed: bool = None,
        pet_name: str = None,
    ) -> List[Task]:
        """
        Return a filtered subset of tasks.

        - completed=True  → only completed tasks
        - completed=False → only pending tasks
        - completed=None  → no filter on completion status
        - pet_name        → only tasks belonging to that pet (case-insensitive)
        """
        result = tasks

        if completed is not None:
            result = [t for t in result if t.completed == completed]

        if pet_name is not None:
            pet_tasks = self.owner.get_tasks_for_pet(pet_name)
            result = [t for t in result if t in pet_tasks]

        return result

    def _rank_tasks(self, tasks: List[Task]) -> List[Task]:
        """Sort by priority descending; break ties by duration ascending (shorter tasks first)."""
        return sorted(tasks, key=lambda t: (-t.priority_rank(), t.duration_minutes))

    def _build_reasoning(
        self, planned: List[Task], skipped: List[Task], total_used: int
    ) -> str:
        """Build a human-readable explanation of why tasks were included or skipped."""
        lines = [
            f"Tasks were sorted by priority (high → low) and scheduled greedily "
            f"within {self.owner.available_minutes} minutes available today."
        ]
        if planned:
            titles = ", ".join(t.title for t in planned)
            lines.append(f"Included ({len(planned)}): {titles}.")
        if skipped:
            titles = ", ".join(t.title for t in skipped)
            lines.append(
                f"Skipped ({len(skipped)}) due to time constraints: {titles}."
            )
        lines.append(f"Total time used: {total_used} min.")
        return " ".join(lines)
