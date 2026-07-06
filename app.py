from datetime import time as dtime

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

    col4, col5, col6 = st.columns(3)
    with col4:
        # A fixed time is optional: it's what powers sorting and conflict
        # detection. Untimed tasks still get packed into the daily plan.
        has_time = st.checkbox("Set a fixed time")
    with col5:
        picked = st.time_input("Time", value=dtime(8, 0), disabled=not has_time)
    with col6:
        frequency = st.selectbox("Repeats", ["one-time", "daily", "weekly"])

    if st.button("Add task"):
        pet.add_task(
            Task(
                category=task_title,
                priority=PRIORITY_MAP[priority],
                duration=int(duration),
                # Store the time as the "HH:MM" string the Scheduler expects.
                time=picked.strftime("%H:%M") if has_time else None,
                frequency=None if frequency == "one-time" else frequency,
            )
        )

    if pet.tasks:
        st.write(f"{pet.name}'s tasks:")
        st.table(
            [
                {
                    "task": t.category,
                    "time": t.time or "—",
                    "duration (min)": t.duration,
                    "priority": t.priority,
                    "repeats": t.frequency or "one-time",
                    "done": "✅" if t.done else "⏳",
                }
                for t in pet.tasks
            ]
        )

        # --- Mark a task complete (demonstrates recurrence) -------------------
        # Completing a daily/weekly task spawns its next occurrence on the pet.
        pending = [t for t in pet.tasks if not t.done]
        if pending:
            labels = [
                f"{t.category}"
                + (f" @ {t.time}" if t.time else "")
                + (f" ({t.frequency})" if t.frequency else "")
                for t in pending
            ]
            done_idx = st.selectbox(
                "Mark a task complete",
                range(len(pending)),
                format_func=lambda i: labels[i],
                key="complete_select",
            )
            if st.button("Complete task"):
                spawned = pending[done_idx].mark_complete()
                if spawned is not None:
                    st.success(
                        f"Done! Next '{spawned.category}' scheduled for "
                        f"{spawned.due_date} ({spawned.frequency})."
                    )
                else:
                    st.success("Marked complete.")
    else:
        st.info(f"No tasks for {pet.name} yet. Add one above.")

st.divider()

# --- All tasks across pets: conflicts, sorting, filtering --------------------
st.subheader("All Tasks")

# Conflict warnings first — a pet owner needs to see clashes before anything
# else, and st.warning (not st.error) reads as "worth a look," not "broken."
conflicts = scheduler.detect_conflicts()
if conflicts:
    st.warning(f"⚠️ {len(conflicts)} scheduling conflict(s) found:")
    for msg in conflicts:
        st.warning(msg)
else:
    st.success("✅ No scheduling conflicts.")

# Filter controls: by pet, and by completion status. These map straight onto
# Scheduler.filter_tasks(pet_name=..., done=...).
fcol1, fcol2 = st.columns(2)
with fcol1:
    pet_choice = st.selectbox(
        "Filter by pet", ["All pets"] + [p.name for p in owner.pets]
    )
with fcol2:
    status_choice = st.radio(
        "Status", ["All", "Pending", "Done"], horizontal=True
    )

pet_name = None if pet_choice == "All pets" else pet_choice
done = {"All": None, "Pending": False, "Done": True}[status_choice]
filtered = scheduler.filter_tasks(pet_name=pet_name, done=done)

# Sort the filtered set chronologically. sort_by_time() sorts across every
# pet, so we intersect it with the filtered set to honor both at once.
keep = {id(t) for t in filtered}
sorted_tasks = [t for t in scheduler.sort_by_time() if id(t) in keep]

if sorted_tasks:
    st.table(
        [
            {
                "time": t.time or "—",
                "task": t.category,
                "pet": t.pet.name if t.pet else "—",
                "duration (min)": t.duration,
                "priority": t.priority,
                "done": "✅" if t.done else "⏳",
            }
            for t in sorted_tasks
        ]
    )
else:
    st.info("No tasks match this filter.")

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
