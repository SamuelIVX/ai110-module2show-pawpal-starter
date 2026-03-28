from pawpal_system import Owner, Pet, Task, Scheduler

# --- Setup ---
owner = Owner(name="Jordan", available_minutes=60)

mochi = Pet(name="Mochi", species="dog")
luna = Pet(name="Luna", species="cat")

# Mochi's tasks
mochi.add_task(Task(title="Morning walk", duration_minutes=20, priority="high", frequency="daily"))
mochi.add_task(Task(title="Flea medication", duration_minutes=5, priority="high", frequency="weekly"))
mochi.add_task(Task(title="Fetch / play session", duration_minutes=15, priority="medium", frequency="daily"))

# Luna's tasks
luna.add_task(Task(title="Brush fur", duration_minutes=10, priority="low", frequency="weekly"))
luna.add_task(Task(title="Feeding (wet food)", duration_minutes=5, priority="high", frequency="daily"))

owner.add_pet(mochi)
owner.add_pet(luna)

# --- Generate schedule ---
scheduler = Scheduler(owner=owner)
schedule = scheduler.generate_schedule()

# --- Print results ---
print("=" * 50)
print(f"  PawPal+ Daily Schedule for {owner.name}")
print(f"  Time budget: {owner.available_minutes} min")
print("=" * 50)

print("\nPLANNED TASKS:")
if schedule.planned_tasks:
    for i, task in enumerate(schedule.planned_tasks, start=1):
        print(f"  {i}. {task.title}")
        print(f"       Priority : {task.priority.upper()}")
        print(f"       Duration : {task.duration_minutes} min")
        print(f"       Frequency: {task.frequency}")
else:
    print("  No tasks scheduled.")

print(f"\n  Total time used: {schedule.total_minutes_used} / {owner.available_minutes} min")

if schedule.skipped_tasks:
    print("\nSKIPPED (not enough time):")
    for task in schedule.skipped_tasks:
        print(f"  - {task.title} ({task.duration_minutes} min, {task.priority} priority)")

print("\nREASONING:")
print(f"  {schedule.reasoning}")
print("=" * 50)
