"""PawPal+ testing ground.

Run with: python main.py

Builds a small owner/pet/task setup and prints the daily schedule that the
Scheduler produces, so you can eyeball the prioritization + packing logic.
"""

from pawpal_system import Owner, Pet, Scheduler, Task


def fmt(minutes: int) -> str:
    """Turn minutes-since-midnight into a readable clock time (e.g. 480 -> 8:00 AM)."""
    hour, minute = divmod(minutes, 60)
    suffix = "AM" if hour < 12 else "PM"
    hour12 = hour % 12 or 12
    return f"{hour12}:{minute:02d} {suffix}"


def main() -> None:
    # --- Owner + availability -------------------------------------------------
    # Two free windows: 8:00-8:30 AM before work, 5:30-8:00 PM after.
    owner = Owner(
        name="Sam",
        availability=[(480, 510), (1050, 1200)],
    )

    # --- Pets -----------------------------------------------------------------
    rex = Pet(id=1, name="Rex", breed="Labrador", age=3, medications=["heartworm"])
    bella = Pet(id=2, name="Bella", breed="Poodle", age=5)

    scheduler = Scheduler(owner=owner)
    scheduler.add_pet(rex)
    scheduler.add_pet(bella)

    # --- Tasks (added out of time order on purpose) ---------------------------
    # Tasks belong to the pet they're for. We add them scrambled so we can see
    # sort_by_time() actually reorder them below.
    rex.add_task(Task(category="Walk", priority=8, duration=40, time="17:30"))
    rex.add_task(Task(category="Give medication", priority=10, duration=5,
                      time="08:00", frequency="daily"))
    bella.add_task(Task(category="Grooming", priority=2, duration=45, time="19:00"))
    rex.add_task(Task(category="Feeding", priority=9, duration=10, time="08:05"))
    bella.add_task(Task(category="Enrichment play", priority=6, duration=30, time="18:00"))
    # Deliberate clash: Bella's vet visit at 17:30 collides with Rex's 17:30 walk.
    bella.add_task(Task(category="Vet appointment", priority=7, duration=30, time="17:30"))

    # --- Recurring tasks: completing a daily task spawns tomorrow's ----------
    meds = rex.tasks[1]  # the daily medication task
    print(f"Rex has {len(rex.tasks)} tasks before completing meds.")
    next_meds = meds.mark_complete()  # already given this morning
    print(f"Rex has {len(rex.tasks)} tasks after — a fresh "
          f"'{next_meds.category}' was auto-created for {next_meds.due_date} "
          f"(was due {meds.due_date}).\n")

    # --- Print the plan -------------------------------------------------------
    windows = ", ".join(f"{fmt(s)}-{fmt(e)}" for s, e in owner.availability)
    print(f"Today's Schedule for {owner.name}")
    print(f"(available: {windows})")
    print("-" * 44)

    plan = scheduler.get_daily_tasks()
    for start, task in plan:
        print(f"  {fmt(start)} — {task.category} for {task.pet.name} "
              f"({task.duration} min) [priority: {task.priority}]")

    # --- Sorting: chronological view via sort_by_time() -----------------------
    print("\nAll tasks sorted by time:")
    for task in scheduler.sort_by_time():
        when = task.time or "--:--"
        print(f"  {when} — {task.category} for {task.pet.name}")

    # --- Filtering: by pet name, and by completion status ---------------------
    print("\nRex's tasks:")
    for task in scheduler.filter_tasks(pet_name="Rex"):
        print(f"  {task.category} ({task.time})")

    print("\nStill pending (not done):")
    for task in scheduler.filter_tasks(done=False):
        print(f"  {task.category} for {task.pet.name} ({task.time})")

    print("\nAlready completed:")
    for task in scheduler.filter_tasks(done=True):
        print(f"  {task.category} for {task.pet.name} ({task.time})")

    # --- Conflict detection ---------------------------------------------------
    print("\nConflict check:")
    conflicts = scheduler.detect_conflicts()
    if conflicts:
        for warning in conflicts:
            print(f"  {warning}")
    else:
        print("  No conflicts — schedule looks clear.")

    # Anything that didn't fit into the available windows.
    scheduled = {id(task) for _, task in plan}
    all_tasks = [t for pet in owner.pets for t in pet.tasks]
    skipped = [t for t in all_tasks if id(t) not in scheduled]
    if skipped:
        print("\nCouldn't fit today:")
        for task in skipped:
            print(f"  {task.category} for {task.pet.name} ({task.duration} min)")


if __name__ == "__main__":
    main()
