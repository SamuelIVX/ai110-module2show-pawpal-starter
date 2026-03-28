from pawpal_system import Owner, Pet, Task, Scheduler

# --- Setup ---
owner = Owner(name="Jordan", available_minutes=60)

mochi = Pet(name="Mochi", species="dog")
luna  = Pet(name="Luna",  species="cat")

mochi.add_task(Task(title="Morning walk",      duration_minutes=20, priority="high",   frequency="daily"))
mochi.add_task(Task(title="Flea medication",   duration_minutes=5,  priority="high",   frequency="weekly"))
mochi.add_task(Task(title="Fetch / play",      duration_minutes=15, priority="medium", frequency="daily"))
luna.add_task( Task(title="Feeding (wet food)",duration_minutes=5,  priority="high",   frequency="daily"))
luna.add_task( Task(title="Brush fur",         duration_minutes=10, priority="low",    frequency="as-needed"))

owner.add_pet(mochi)
owner.add_pet(luna)

scheduler = Scheduler(owner=owner)

# ── Demo: Recurring tasks ──────────────────────────────────────────────────────
print("=" * 58)
print("  RECURRING TASK DEMO")
print("=" * 58)

walk = mochi.tasks[0]       # Morning walk  (daily)
flea = mochi.tasks[1]       # Flea medication (weekly)
brush = luna.tasks[1]       # Brush fur (as-needed)

print(f"\nBefore completing tasks — Mochi has {len(mochi.get_tasks())} task(s):")
for t in mochi.get_tasks():
    print(f"  - {t.title} | due {t.due_date} | freq={t.frequency} | done={t.completed}")

# Complete the daily "Morning walk"
next_walk = scheduler.mark_task_complete(walk)
print(f"\nCompleted '{walk.title}' (daily).")
print(f"  Next occurrence created: '{next_walk.title}' due {next_walk.due_date}")

# Complete the weekly "Flea medication"
next_flea = scheduler.mark_task_complete(flea)
print(f"\nCompleted '{flea.title}' (weekly).")
print(f"  Next occurrence created: '{next_flea.title}' due {next_flea.due_date}")

# Complete the as-needed "Brush fur"
next_brush = scheduler.mark_task_complete(brush)
print(f"\nCompleted '{brush.title}' (as-needed).")
print(f"  Next occurrence created: {next_brush}")  # should be None

print(f"\nAfter completing tasks — Mochi has {len(mochi.get_tasks())} task(s):")
for t in mochi.get_tasks():
    status = "done" if t.completed else "todo"
    print(f"  - [{status}] {t.title} | due {t.due_date}")

# ── Schedule now only shows pending tasks ──────────────────────────────────────
print("\n" + "=" * 58)
print("  SCHEDULE AFTER COMPLETIONS (pending tasks only)")
print("=" * 58)
schedule = scheduler.generate_schedule()
for i, t in enumerate(schedule.planned_tasks, 1):
    print(f"  {i}. [{t.priority.upper():<6}] {t.title} (due {t.due_date})")
print(f"\n  Time used: {schedule.total_minutes_used} / {owner.available_minutes} min")
print("=" * 58)
