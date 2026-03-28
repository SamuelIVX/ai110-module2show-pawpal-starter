import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# ── Owner & Pet setup ──────────────────────────────────────────────────────────
st.subheader("Owner & Pet Info")

owner_name = st.text_input("Owner name", value="Jordan")
available_minutes = st.number_input(
    "Time available today (minutes)", min_value=1, max_value=480, value=60
)
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

# Initialize Owner and Pet once per session.
# The "not in" guard prevents resetting state on every Streamlit re-run.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name=owner_name, available_minutes=available_minutes)

if "pet" not in st.session_state:
    pet = Pet(name=pet_name, species=species)
    st.session_state.owner.add_pet(pet)   # attach pet to owner
    st.session_state.pet = pet

st.divider()

# ── Task entry ─────────────────────────────────────────────────────────────────
st.subheader("Tasks")

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

if st.button("Add task"):
    # Create a real Task object and add it to the pet via its method.
    # This keeps all task data inside the Pet, which the Scheduler reads later.
    new_task = Task(
        title=task_title,
        duration_minutes=int(duration),
        priority=priority,
    )
    st.session_state.pet.add_task(new_task)
    st.success(f'Added "{task_title}" to {st.session_state.pet.name}\'s task list.')

# Display current tasks pulled from the Pet object (single source of truth)
current_tasks = st.session_state.pet.get_tasks()
if current_tasks:
    st.write(f"**{st.session_state.pet.name}'s tasks:**")
    st.table([t.to_dict() for t in current_tasks])
else:
    st.info("No tasks yet. Add one above.")

st.divider()

# ── Schedule generation ────────────────────────────────────────────────────────
st.subheader("Build Schedule")

if st.button("Generate schedule"):
    owner = st.session_state.owner
    # Sync the available_minutes from the UI input before scheduling
    owner.available_minutes = int(available_minutes)

    scheduler = Scheduler(owner=owner)
    schedule = scheduler.generate_schedule()

    if not schedule.planned_tasks and not schedule.skipped_tasks:
        st.warning("No tasks found. Add some tasks above first.")
    else:
        st.success("Schedule generated!")
        st.markdown(schedule.summary())
