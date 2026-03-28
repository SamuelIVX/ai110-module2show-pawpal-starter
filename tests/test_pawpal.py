from pawpal_system import Owner, Pet, Task, Scheduler


# --- Test: Task completion ---

def test_mark_complete_changes_status():
    task = Task(title="Morning walk", duration_minutes=20, priority="high")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


# --- Test: Task addition ---

def test_add_task_increases_pet_task_count():
    pet = Pet(name="Mochi", species="dog")
    assert len(pet.get_tasks()) == 0
    pet.add_task(Task(title="Feeding", duration_minutes=5, priority="high"))
    assert len(pet.get_tasks()) == 1
    pet.add_task(Task(title="Walk", duration_minutes=20, priority="medium"))
    assert len(pet.get_tasks()) == 2


# --- Bonus: Scheduler respects priority order ---

def test_scheduler_orders_tasks_by_priority():
    owner = Owner(name="Jordan", available_minutes=60)
    pet = Pet(name="Mochi", species="dog")
    pet.add_task(Task(title="Low task", duration_minutes=5, priority="low"))
    pet.add_task(Task(title="High task", duration_minutes=5, priority="high"))
    pet.add_task(Task(title="Medium task", duration_minutes=5, priority="medium"))
    owner.add_pet(pet)

    schedule = Scheduler(owner=owner).generate_schedule()
    priorities = [t.priority for t in schedule.planned_tasks]
    assert priorities == ["high", "medium", "low"]


# --- Bonus: Scheduler skips tasks that exceed time budget ---

def test_scheduler_skips_tasks_that_exceed_budget():
    owner = Owner(name="Jordan", available_minutes=10)
    pet = Pet(name="Luna", species="cat")
    pet.add_task(Task(title="Long walk", duration_minutes=30, priority="high"))
    pet.add_task(Task(title="Quick feed", duration_minutes=5, priority="medium"))
    owner.add_pet(pet)

    schedule = Scheduler(owner=owner).generate_schedule()
    assert any(t.title == "Quick feed" for t in schedule.planned_tasks)
    assert any(t.title == "Long walk" for t in schedule.skipped_tasks)
