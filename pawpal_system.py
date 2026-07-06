"""PawPal+ system classes.

Model: an Owner has Pets; each Pet owns its own Tasks. The Scheduler reads all
of the owner's pets' tasks and packs them, by priority, into the owner's free
time windows to produce a daily plan.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Pet:
    id: int  # stable identity; two pets can share a name, not an id
    name: str
    breed: str
    age: int
    medications: list[str] = field(default_factory=list)
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a task to this pet; increases len(self.tasks)."""
        task.pet = self
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Detach a task from this pet if it's present."""
        if task in self.tasks:
            self.tasks.remove(task)


@dataclass
class Owner:
    name: str
    pets: list[Pet] = field(default_factory=list)
    # Free windows in the day as (start, end) minutes since midnight,
    # e.g. [(480, 510), (1050, 1200)] == 08:00-08:30 and 17:30-20:00.
    # 480 = 8:00 AM, 1200 = 8:00 PM.
    availability: list[tuple[int, int]] = field(default_factory=list)


@dataclass
class Task:
    category: str
    priority: int  # higher = more urgent
    duration: int  # minutes; used to pack tasks into the day's time budget
    pet: Pet | None = None  # set automatically when attached via Pet.add_task
    done: bool = False

    def mark_complete(self) -> None:
        """Mark this task complete; completed tasks are left out of the plan."""
        self.done = True


@dataclass
class Scheduler:
    """Per-owner scheduler. Reads every pet's tasks and builds a daily plan."""

    owner: Owner

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this scheduler's owner."""
        self.owner.pets.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        """Remove a pet (and its tasks) from the owner by matching id."""
        # Tasks live on the pet, so removing the pet drops its tasks with it.
        self.owner.pets = [p for p in self.owner.pets if p.id != pet.id]

    def get_daily_tasks(self) -> list[tuple[int, Task]]:
        """Build today's plan: gather every pet's still-pending tasks, sort by
        priority, then greedily place each into the first of the owner's
        availability (start, end) blocks that still has room for its duration,
        skipping any task that fits in no remaining block. Returns
        (start_minute, task) pairs in chronological order, where start_minute
        is minutes since midnight (e.g. 480 == 8:00 AM)."""
        all_tasks = [
            task
            for pet in self.owner.pets
            for task in pet.tasks
            if not task.done
        ]

        # Availability blocks in chronological order. `cursor` tracks the next
        # free minute inside each block; `end` is its hard stop.
        blocks = sorted(self.owner.availability)
        cursors = [start for start, _ in blocks]
        ends = [end for _, end in blocks]

        by_priority = sorted(all_tasks, key=lambda t: t.priority, reverse=True)

        placed: list[tuple[int, Task]] = []
        for task in by_priority:
            for i, end in enumerate(ends):
                if cursors[i] + task.duration <= end:
                    placed.append((cursors[i], task))
                    cursors[i] += task.duration
                    break
            # No block had room -> task is skipped for today.

        placed.sort(key=lambda pair: pair[0])
        return placed
