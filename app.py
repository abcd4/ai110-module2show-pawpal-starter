import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")
st.caption("Plan your pets' care tasks into a daily schedule.")

# Our Task uses an integer priority (higher = more urgent); the UI uses words.
PRIORITY_MAP = {"low": 1, "medium": 5, "high": 10}


def fmt(minutes: int) -> str:
    """Turn minutes-since-midnight into a readable clock time (480 -> 8:00 AM)."""
    hour, minute = divmod(minutes, 60)
    suffix = "AM" if hour < 12 else "PM"
    hour12 = hour % 12 or 12
    return f"{hour12}:{minute:02d} {suffix}"


# --- Session state: keep the OWNER once, then reuse it across reruns ----------
# Streamlit re-runs this whole file on every click, so we guard with `not in`
# to avoid wiping our data. Everything (pets, tasks) hangs off the owner, so
# the owner is the only thing we need to persist.
if "owner" not in st.session_state:
    owner = Owner(
        name="Jordan",
        availability=[(480, 720), (1020, 1200)],  # 8AM-12PM and 5PM-8PM
    )
    owner.pets.append(Pet(id=1, name="Mochi", breed="dog", age=1))
    st.session_state.owner = owner

owner = st.session_state.owner
scheduler = Scheduler(owner=owner)  # stateless wrapper, fine to rebuild each run

# --- Owner --------------------------------------------------------------------
st.subheader("Owner")
owner.name = st.text_input("Owner name", value=owner.name)

st.divider()

# --- Add a pet ----------------------------------------------------------------
st.subheader("Pets")

with st.form("add_pet_form", clear_on_submit=True):
    new_name = st.text_input("Pet name")
    new_species = st.selectbox("Species", ["dog", "cat", "other"])
    new_age = st.number_input("Age (years)", min_value=0, max_value=30, value=1)
    if st.form_submit_button("Add pet") and new_name:
        # Give the new pet a unique id, then let the scheduler store it.
        next_id = max((p.id for p in owner.pets), default=0) + 1
        scheduler.add_pet(Pet(id=next_id, name=new_name, breed=new_species, age=int(new_age)))
        # The owner lives in session_state, so this new pet persists and shows
        # up automatically when Streamlit re-runs the script.

if owner.pets:
    st.write("Your pets: " + ", ".join(f"{p.name} ({p.breed})" for p in owner.pets))
else:
    st.info("No pets yet. Add one above.")

st.divider()

# --- Add tasks (to the chosen pet) -------------------------------------------
st.subheader("Tasks")

if not owner.pets:
    st.info("Add a pet first, then you can give it tasks.")
else:
    # Select by index and look the pet up from session state. Passing the Pet
    # objects directly makes Streamlit hand back a *copy*, so tasks added to it
    # would be lost on the next rerun.
    pet_index = st.selectbox(
        "Add tasks for which pet?",
        range(len(owner.pets)),
        format_func=lambda i: owner.pets[i].name,
    )
    pet = owner.pets[pet_index]

    col1, col2, col3 = st.columns(3)
    with col1:
        task_title = st.text_input("Task title", value="Walk")
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col3:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

    if st.button("Add task"):
        pet.add_task(
            Task(category=task_title, priority=PRIORITY_MAP[priority], duration=int(duration))
        )

    if pet.tasks:
        st.write(f"{pet.name}'s tasks:")
        st.table(
            [
                {
                    "task": t.category,
                    "duration (min)": t.duration,
                    "priority": t.priority,
                    "done": t.done,
                }
                for t in pet.tasks
            ]
        )
    else:
        st.info(f"No tasks for {pet.name} yet. Add one above.")

st.divider()

# --- Generate the daily plan (across all pets) -------------------------------
st.subheader("Today's Schedule")
windows = ", ".join(f"{fmt(s)}-{fmt(e)}" for s, e in owner.availability)
st.caption(f"Available: {windows}")

# Clicking the button only returns True on that one rerun, so we save the
# plan into session_state and render it below on every rerun. Otherwise the
# schedule would flash once and vanish the next time you touch the page.
if st.button("Generate schedule"):
    st.session_state.plan = scheduler.get_daily_tasks()

if "plan" in st.session_state:
    plan = st.session_state.plan
    if not plan:
        st.info("Nothing to schedule yet — add some tasks first.")
    else:
        for start, task in plan:
            st.write(
                f"**{fmt(start)}** — {task.category} for {task.pet.name} "
                f"({task.duration} min) · priority {task.priority}"
            )

        # Show anything that didn't fit into the available windows.
        scheduled = {id(t) for _, t in plan}
        all_tasks = [t for p in owner.pets for t in p.tasks]
        skipped = [t for t in all_tasks if id(t) not in scheduled]
        if skipped:
            st.warning(
                "Couldn't fit today: " + ", ".join(t.category for t in skipped)
            )
