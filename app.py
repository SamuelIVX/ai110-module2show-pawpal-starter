import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")
st.caption("A smart daily care planner for your pet.")

# ── Owner & Pet setup ──────────────────────────────────────────────────────────
st.subheader("Owner & Pet Info")

col_a, col_b = st.columns(2)
with col_a:
    owner_name = st.text_input("Owner name", value="Jordan")
    available_minutes = st.number_input(
        "Time available today (minutes)", min_value=1, max_value=480, value=60
    )
with col_b:
    pet_name = st.text_input("Pet name", value="Mochi")
    species = st.selectbox("Species", ["dog", "cat", "other"])

# Initialize Owner and Pet once per session.
# The "not in" guard prevents resetting state on every Streamlit re-run.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name=owner_name, available_minutes=available_minutes)

if "pet" not in st.session_state:
    pet = Pet(name=pet_name, species=species)
    st.session_state.owner.add_pet(pet)
    st.session_state.pet = pet

st.divider()

# ── Task entry ─────────────────────────────────────────────────────────────────
st.subheader("Add a Task")

col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
with col4:
    frequency = st.selectbox("Frequency", ["daily", "weekly", "as-needed"])

if st.button("Add task", type="primary"):
    new_task = Task(
        title=task_title,
        duration_minutes=int(duration),
        priority=priority,
        frequency=frequency,
    )
    st.session_state.pet.add_task(new_task)
    st.success(f'Added "{task_title}" to {st.session_state.pet.name}\'s task list.')

# ── Current task list — sorted by duration for easy scanning ───────────────────
current_tasks = st.session_state.pet.get_tasks()

if current_tasks:
    st.markdown(f"**{st.session_state.pet.name}'s tasks** ({len(current_tasks)} total)")

    scheduler_preview = Scheduler(owner=st.session_state.owner)
    sorted_tasks = scheduler_preview.sort_by_duration(current_tasks)

    # Filter controls
    filter_col1, filter_col2 = st.columns(2)
    with filter_col1:
        show_completed = st.checkbox("Show completed tasks", value=True)
    with filter_col2:
        sort_label = st.radio(
            "Sort task list by", ["Duration (shortest first)", "As added"],
            horizontal=True
        )

    display_tasks = sorted_tasks if "Duration" in sort_label else current_tasks
    if not show_completed:
        display_tasks = scheduler_preview.filter_tasks(display_tasks, completed=False)

    if display_tasks:
        st.table([
            {
                "Title": t.title,
                "Duration (min)": t.duration_minutes,
                "Priority": t.priority.upper(),
                "Frequency": t.frequency,
                "Done": "✓" if t.completed else "○",
            }
            for t in display_tasks
        ])
    else:
        st.info("No tasks match the current filter.")
else:
    st.info("No tasks yet. Add one above.")

st.divider()

# ── Schedule generation ────────────────────────────────────────────────────────
st.subheader("Generate Today's Schedule")
st.caption(
    "Tasks are sorted by priority (high → low). "
    "Among equal-priority tasks, shorter ones are scheduled first."
)

if st.button("Generate schedule", type="primary"):
    owner = st.session_state.owner
    owner.available_minutes = int(available_minutes)   # sync from UI input

    scheduler = Scheduler(owner=owner)
    schedule = scheduler.generate_schedule()

    # ── Conflict warnings — shown first so owner sees them immediately ─────────
    if schedule.conflicts:
        st.error(f"⚠️ {len(schedule.conflicts)} conflict(s) detected — review before following this schedule:")
        for warning in schedule.conflicts:
            st.warning(warning)
        st.divider()

    # ── Empty state ────────────────────────────────────────────────────────────
    if not schedule.planned_tasks and not schedule.skipped_tasks:
        st.info("No pending tasks found. Add some tasks above first.")

    else:
        # ── Planned tasks ──────────────────────────────────────────────────────
        st.success(
            f"Schedule ready — {len(schedule.planned_tasks)} task(s) planned, "
            f"{schedule.total_minutes_used} / {owner.available_minutes} min used."
        )

        if schedule.planned_tasks:
            st.markdown("**Planned tasks (in order):**")
            st.table([
                {
                    "Order": i,
                    "Title": t.title,
                    "Duration (min)": t.duration_minutes,
                    "Priority": t.priority.upper(),
                    "Frequency": t.frequency,
                }
                for i, t in enumerate(schedule.planned_tasks, start=1)
            ])

        # ── Skipped tasks ──────────────────────────────────────────────────────
        if schedule.skipped_tasks:
            with st.expander(f"Skipped tasks ({len(schedule.skipped_tasks)}) — not enough time"):
                st.table([
                    {
                        "Title": t.title,
                        "Duration (min)": t.duration_minutes,
                        "Priority": t.priority.upper(),
                    }
                    for t in schedule.skipped_tasks
                ])

        # ── Reasoning ──────────────────────────────────────────────────────────
        with st.expander("Why was this schedule chosen?"):
            st.markdown(schedule.reasoning)
