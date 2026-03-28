from pawpal_system import Owner, Pet, Task, Scheduler

# --- Setup ---
owner = Owner(name="Jordan", available_minutes=60)

mochi = Pet(name="Mochi", species="dog")
luna = Pet(name="Luna", species="cat")

# Tasks added intentionally OUT OF ORDER (long before short, low before high)
mochi.add_task(Task(title="Fetch / play session", duration_minutes=15, priority="medium", frequency="daily"))
mochi.add_task(Task(title="Morning walk",         duration_minutes=20, priority="high",   frequency="daily"))
mochi.add_task(Task(title="Flea medication",      duration_minutes=5,  priority="high",   frequency="weekly"))

luna.add_task(Task(title="Brush fur",             duration_minutes=10, priority="low",    frequency="weekly"))
luna.add_task(Task(title="Feeding (wet food)",    duration_minutes=5,  priority="high",   frequency="daily"))

# Mark one task complete so filtering can show the difference
mochi.tasks[2].mark_complete()   # Flea medication → completed

owner.add_pet(mochi)
owner.add_pet(luna)

scheduler = Scheduler(owner=owner)
all_tasks  = owner.get_all_tasks()

# ── Demo 1: Sort by duration (shortest → longest) ─────────────────────────────
print("=" * 55)
print("  SORT BY DURATION (shortest → longest)")
print("=" * 55)
for t in scheduler.sort_by_duration(all_tasks):
    print(f"  {t.duration_minutes:>3} min  [{t.priority.upper():<6}]  {t.title}")

# ── Demo 2: Filter — pending tasks only ───────────────────────────────────────
print("\n" + "=" * 55)
print("  FILTER: pending tasks only (completed=False)")
print("=" * 55)
for t in scheduler.filter_tasks(all_tasks, completed=False):
    print(f"  {'done' if t.completed else 'todo'}  {t.title}")

# ── Demo 3: Filter — Mochi's tasks only ───────────────────────────────────────
print("\n" + "=" * 55)
print("  FILTER: Mochi's tasks only")
print("=" * 55)
for t in scheduler.filter_tasks(all_tasks, pet_name="Mochi"):
    status = "✓" if t.completed else "○"
    print(f"  {status}  {t.title}")

# ── Demo 4: Generate schedule (tiebreaker visible) ────────────────────────────
print("\n" + "=" * 55)
print("  GENERATE SCHEDULE")
print("  (HIGH tasks: shorter Flea med skipped as completed,")
print("   shorter Feeding beats longer Morning walk in tie)")
print("=" * 55)
schedule = scheduler.generate_schedule()
print("\nPLANNED:")
for i, t in enumerate(schedule.planned_tasks, 1):
    print(f"  {i}. [{t.priority.upper():<6}] {t.duration_minutes:>3} min  {t.title}")

if schedule.skipped_tasks:
    print("\nSKIPPED:")
    for t in schedule.skipped_tasks:
        print(f"  - {t.title} ({t.duration_minutes} min)")

print(f"\n  Time used: {schedule.total_minutes_used} / {owner.available_minutes} min")
print(f"\nREASONING:\n  {schedule.reasoning}")
print("=" * 55)
