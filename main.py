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

    # --- Tasks (different durations + priorities) -----------------------------
    # Tasks belong to the pet they're for.
    rex.add_task(Task(category="Give medication", priority=10, duration=5))
    rex.add_task(Task(category="Feeding", priority=9, duration=10))
    rex.add_task(Task(category="Walk", priority=8, duration=40))
    bella.add_task(Task(category="Enrichment play", priority=6, duration=30))
    bella.add_task(Task(category="Grooming", priority=2, duration=45))

    # --- Print the plan -------------------------------------------------------
    windows = ", ".join(f"{fmt(s)}-{fmt(e)}" for s, e in owner.availability)
    print(f"Today's Schedule for {owner.name}")
    print(f"(available: {windows})")
    print("-" * 44)

    plan = scheduler.get_daily_tasks()
    for start, task in plan:
        print(f"  {fmt(start)} — {task.category} for {task.pet.name} "
              f"({task.duration} min) [priority: {task.priority}]")

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
