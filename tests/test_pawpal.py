from datetime import date, timedelta

from pawpal_system import Owner, Pet, Task, Scheduler


# ── Helpers ────────────────────────────────────────────────────────────────────

def make_owner(minutes: int = 60) -> Owner:
    """Return a simple owner with one empty pet attached."""
    owner = Owner(name="Jordan", available_minutes=minutes)
    owner.add_pet(Pet(name="Mochi", species="dog"))
    return owner

def add_task(owner: Owner, title: str, duration: int, priority: str,
             frequency: str = "daily") -> Task:
    """Create a Task, add it to the first pet, and return it."""
    task = Task(title=title, duration_minutes=duration, priority=priority,
                frequency=frequency)
    owner.pets[0].add_task(task)
    return task


# ── Original tests (kept) ──────────────────────────────────────────────────────

def test_mark_complete_changes_status():
    """mark_complete() must flip completed from False to True."""
    task = Task(title="Morning walk", duration_minutes=20, priority="high")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    """Each add_task() call must grow the pet's task list by one."""
    pet = Pet(name="Mochi", species="dog")
    assert len(pet.get_tasks()) == 0
    pet.add_task(Task(title="Feeding", duration_minutes=5, priority="high"))
    assert len(pet.get_tasks()) == 1
    pet.add_task(Task(title="Walk", duration_minutes=20, priority="medium"))
    assert len(pet.get_tasks()) == 2


def test_scheduler_orders_tasks_by_priority():
    """Planned tasks must appear high → medium → low regardless of insertion order."""
    owner = Owner(name="Jordan", available_minutes=60)
    pet = Pet(name="Mochi", species="dog")
    pet.add_task(Task(title="Low task",    duration_minutes=5, priority="low"))
    pet.add_task(Task(title="High task",   duration_minutes=5, priority="high"))
    pet.add_task(Task(title="Medium task", duration_minutes=5, priority="medium"))
    owner.add_pet(pet)

    schedule = Scheduler(owner=owner).generate_schedule()
    priorities = [t.priority for t in schedule.planned_tasks]
    assert priorities == ["high", "medium", "low"]


def test_scheduler_skips_tasks_that_exceed_budget():
    """A task too long for the budget must land in skipped_tasks, not planned_tasks."""
    owner = Owner(name="Jordan", available_minutes=10)
    pet = Pet(name="Luna", species="cat")
    pet.add_task(Task(title="Long walk",  duration_minutes=30, priority="high"))
    pet.add_task(Task(title="Quick feed", duration_minutes=5,  priority="medium"))
    owner.add_pet(pet)

    schedule = Scheduler(owner=owner).generate_schedule()
    assert any(t.title == "Quick feed" for t in schedule.planned_tasks)
    assert any(t.title == "Long walk"  for t in schedule.skipped_tasks)


# ── Sorting ────────────────────────────────────────────────────────────────────

def test_duration_tiebreaker_shorter_task_scheduled_first():
    """
    Among tasks of equal priority, the shorter one must be scheduled first.
    Both tasks are HIGH; the 5-min task should appear before the 20-min task.
    """
    owner = make_owner(60)
    add_task(owner, "Short high", duration=5,  priority="high")
    add_task(owner, "Long high",  duration=20, priority="high")

    schedule = Scheduler(owner=owner).generate_schedule()
    titles = [t.title for t in schedule.planned_tasks]
    assert titles.index("Short high") < titles.index("Long high")


def test_sort_by_duration_returns_ascending_order():
    """sort_by_duration() must return tasks shortest-first regardless of insertion order."""
    owner = make_owner()
    t30 = add_task(owner, "Long",   duration=30, priority="medium")
    t5  = add_task(owner, "Short",  duration=5,  priority="medium")
    t15 = add_task(owner, "Medium", duration=15, priority="medium")

    sorted_tasks = Scheduler(owner=owner).sort_by_duration([t30, t5, t15])
    durations = [t.duration_minutes for t in sorted_tasks]
    assert durations == [5, 15, 30]


# ── Recurrence ─────────────────────────────────────────────────────────────────

def test_daily_task_next_occurrence_is_tomorrow():
    """next_occurrence() on a daily task must return a task due today + 1 day."""
    today = date.today()
    task = Task(title="Walk", duration_minutes=20, priority="high",
                frequency="daily", due_date=today)
    next_task = task.next_occurrence()

    assert next_task is not None
    assert next_task.due_date == today + timedelta(days=1)
    assert next_task.completed is False


def test_weekly_task_next_occurrence_is_next_week():
    """next_occurrence() on a weekly task must return a task due today + 7 days."""
    today = date.today()
    task = Task(title="Flea med", duration_minutes=5, priority="high",
                frequency="weekly", due_date=today)
    next_task = task.next_occurrence()

    assert next_task is not None
    assert next_task.due_date == today + timedelta(weeks=1)


def test_as_needed_task_has_no_next_occurrence():
    """next_occurrence() on an as-needed task must return None — it does not auto-recur."""
    task = Task(title="Vet visit", duration_minutes=60, priority="high",
                frequency="as-needed")
    assert task.next_occurrence() is None


def test_mark_task_complete_creates_next_occurrence_for_daily():
    """
    After Scheduler.mark_task_complete() on a daily task the pet should have
    one completed task and one new pending task — total count increases by one.
    """
    owner = make_owner()
    task = add_task(owner, "Walk", duration=20, priority="high", frequency="daily")
    initial_count = len(owner.pets[0].get_tasks())

    Scheduler(owner=owner).mark_task_complete(task)

    tasks = owner.pets[0].get_tasks()
    assert len(tasks) == initial_count + 1
    assert task.completed is True
    assert any(t.title == "Walk" and not t.completed for t in tasks)


def test_mark_task_complete_no_recurrence_for_as_needed():
    """Completing an as-needed task must NOT add a new task to the pet."""
    owner = make_owner()
    task = add_task(owner, "Vet visit", duration=60, priority="high",
                    frequency="as-needed")
    initial_count = len(owner.pets[0].get_tasks())

    Scheduler(owner=owner).mark_task_complete(task)

    assert len(owner.pets[0].get_tasks()) == initial_count   # no new task


# ── Filtering ──────────────────────────────────────────────────────────────────

def test_filter_by_completion_excludes_done_tasks():
    """filter_tasks(completed=False) must return only pending tasks."""
    owner = make_owner()
    done_task    = add_task(owner, "Done",    duration=5,  priority="low")
    pending_task = add_task(owner, "Pending", duration=10, priority="medium")
    done_task.mark_complete()

    result = Scheduler(owner=owner).filter_tasks(
        owner.get_all_tasks(), completed=False
    )
    assert pending_task in result
    assert done_task not in result


def test_filter_by_pet_name_returns_only_that_pets_tasks():
    """filter_tasks(pet_name='Mochi') must exclude tasks belonging to other pets."""
    owner = Owner(name="Jordan", available_minutes=60)
    mochi = Pet(name="Mochi", species="dog")
    luna  = Pet(name="Luna",  species="cat")
    mochi_task = Task(title="Walk Mochi", duration_minutes=20, priority="high")
    luna_task  = Task(title="Feed Luna",  duration_minutes=5,  priority="high")
    mochi.add_task(mochi_task)
    luna.add_task(luna_task)
    owner.add_pet(mochi)
    owner.add_pet(luna)

    result = Scheduler(owner=owner).filter_tasks(
        owner.get_all_tasks(), pet_name="Mochi"
    )
    assert mochi_task in result
    assert luna_task not in result


# ── Conflict detection ─────────────────────────────────────────────────────────

def test_conflict_detected_for_duplicate_task_title():
    """Adding the same task title twice for the same pet must produce a conflict warning."""
    owner = make_owner()
    add_task(owner, "Morning walk", duration=20, priority="high")
    add_task(owner, "Morning walk", duration=20, priority="high")  # duplicate

    schedule = Scheduler(owner=owner).generate_schedule()
    assert any("duplicate" in w.lower() for w in schedule.conflicts)


def test_conflict_detected_for_impossible_task():
    """A task longer than available_minutes must produce a conflict warning."""
    owner = make_owner(minutes=30)
    add_task(owner, "Full grooming", duration=90, priority="low")

    schedule = Scheduler(owner=owner).generate_schedule()
    assert any("can never be scheduled" in w for w in schedule.conflicts)


def test_no_conflicts_for_clean_task_list():
    """A normal task list with no duplicates or overlong tasks must have no conflicts."""
    owner = make_owner()
    add_task(owner, "Walk",    duration=20, priority="high")
    add_task(owner, "Feeding", duration=5,  priority="high")

    schedule = Scheduler(owner=owner).generate_schedule()
    assert schedule.conflicts == []


# ── Edge cases ─────────────────────────────────────────────────────────────────

def test_pet_with_no_tasks_produces_empty_schedule():
    """An owner whose only pet has no tasks must get an empty planned schedule."""
    owner = Owner(name="Jordan", available_minutes=60)
    owner.add_pet(Pet(name="Mochi", species="dog"))

    schedule = Scheduler(owner=owner).generate_schedule()
    assert schedule.planned_tasks == []
    assert schedule.skipped_tasks == []


def test_owner_with_no_pets_produces_empty_schedule():
    """An owner with no pets at all must get an empty schedule without crashing."""
    owner = Owner(name="Jordan", available_minutes=60)

    schedule = Scheduler(owner=owner).generate_schedule()
    assert schedule.planned_tasks == []


def test_all_tasks_completed_produces_empty_planned_list():
    """If every task is already completed, planned_tasks must be empty."""
    owner = make_owner()
    task = add_task(owner, "Walk", duration=20, priority="high")
    task.mark_complete()

    schedule = Scheduler(owner=owner).generate_schedule()
    assert schedule.planned_tasks == []


def test_task_that_exactly_fills_budget_is_planned():
    """A task whose duration equals available_minutes must be planned, not skipped."""
    owner = make_owner(minutes=20)
    add_task(owner, "Walk", duration=20, priority="high")

    schedule = Scheduler(owner=owner).generate_schedule()
    assert len(schedule.planned_tasks) == 1
    assert schedule.skipped_tasks == []
