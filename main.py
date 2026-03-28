from pawpal_system import Owner, Pet, Task, Scheduler

# --- Setup ---
owner = Owner(name="Jordan", available_minutes=60)

mochi = Pet(name="Mochi", species="dog")
luna  = Pet(name="Luna",  species="cat")

mochi.add_task(Task(title="Morning walk",       duration_minutes=20, priority="high",   frequency="daily"))
mochi.add_task(Task(title="Fetch / play",       duration_minutes=15, priority="medium", frequency="daily"))

# CONFLICT 1: same task added twice for the same pet on the same day
mochi.add_task(Task(title="Morning walk",       duration_minutes=20, priority="high",   frequency="daily"))

luna.add_task( Task(title="Feeding (wet food)", duration_minutes=5,  priority="high",   frequency="daily"))

# CONFLICT 2: a task so long it can never fit in the 60-minute budget
luna.add_task( Task(title="Full grooming spa",  duration_minutes=90, priority="low",    frequency="weekly"))

owner.add_pet(mochi)
owner.add_pet(luna)

scheduler = Scheduler(owner=owner)
schedule  = scheduler.generate_schedule()

# ── Print conflicts ────────────────────────────────────────────────────────────
print("=" * 58)
print("  CONFLICT DETECTION DEMO")
print("=" * 58)

if schedule.conflicts:
    print(f"\n⚠️  {len(schedule.conflicts)} conflict(s) found:\n")
    for warning in schedule.conflicts:
        print(f"  WARNING: {warning}")
else:
    print("\n  No conflicts detected.")

# ── Print schedule ─────────────────────────────────────────────────────────────
print("\n" + "=" * 58)
print("  SCHEDULE (scheduler continues despite warnings)")
print("=" * 58)
print("\nPLANNED:")
for i, t in enumerate(schedule.planned_tasks, 1):
    print(f"  {i}. [{t.priority.upper():<6}] {t.duration_minutes:>3} min  {t.title}")

if schedule.skipped_tasks:
    print("\nSKIPPED:")
    for t in schedule.skipped_tasks:
        print(f"  - {t.title} ({t.duration_minutes} min)")

print(f"\n  Time used: {schedule.total_minutes_used} / {owner.available_minutes} min")
print("=" * 58)
