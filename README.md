# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Smarter Scheduling

Beyond basic scheduling, PawPal+ includes four algorithmic features that make the planner more realistic:

**Priority + duration sorting** — Tasks are ranked by priority (high → medium → low) with duration as a tiebreaker: among tasks of equal priority, shorter ones are scheduled first. This maximises the number of tasks that fit within the time budget rather than front-loading long tasks that waste remaining minutes.

**Filtering** — `Scheduler.filter_tasks()` lets you narrow any task list by completion status (`completed=True/False`) or by pet name. Useful for views like "show only Mochi's pending tasks" without re-querying from scratch.

**Recurring tasks** — Each `Task` has a `frequency` field (`"daily"`, `"weekly"`, `"as-needed"`). When `Scheduler.mark_task_complete()` is called, it automatically creates and attaches the next occurrence to the pet using Python's `timedelta` (`+1 day` for daily, `+7 days` for weekly). As-needed tasks do not recur.

**Conflict detection** — Before returning a schedule, `Scheduler._detect_conflicts()` scans for two problems and returns human-readable warnings rather than raising exceptions: (1) duplicate task titles on the same pet for the same due date, and (2) tasks whose duration alone exceeds the owner's total time budget and can therefore never be scheduled. Warnings surface at the top of `Schedule.summary()` so the UI can display them immediately.

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
