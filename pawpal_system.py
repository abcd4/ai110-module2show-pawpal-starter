"""PawPal+ system classes.

Model: an Owner has Pets; each Pet owns its own Tasks. The Scheduler reads all
of the owner's pets' tasks and packs them, by priority, into the owner's free
time windows to produce a daily plan.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from itertools import combinations


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
    # Optional wall-clock time as a zero-padded "HH:MM" string (e.g. "08:30").
    # Used by Scheduler.sort_by_time(); leave None for tasks with no fixed time.
    time: str | None = None
    # Recurrence: "daily" or "weekly" spawn a fresh occurrence when completed;
    # None means it's a one-time task.
    frequency: str | None = None
    # The date this task is due. Defaults to today when not given.
    due_date: date = field(default_factory=date.today)

    def mark_complete(self) -> Task | None:
        """Mark this task complete.

        For a recurring task ("daily"/"weekly"), also spawn the next
        occurrence on the same pet and return it; for a one-time task, return
        None. Completed tasks are left out of the daily plan.
        """
        self.done = True
        return self._spawn_next_occurrence()

    def _spawn_next_occurrence(self) -> Task | None:
        """Create the next occurrence of a recurring task, dated one interval
        past this task's due_date, and attach it to the same pet."""
        intervals = {"daily": timedelta(days=1), "weekly": timedelta(weeks=1)}
        step = intervals.get(self.frequency)
        if step is None or self.pet is None:
            return None  # one-time task, or not attached to a pet yet

        # timedelta handles month/year rollovers (e.g. Jul 31 -> Aug 1).
        next_task = Task(
            category=self.category,
            priority=self.priority,
            duration=self.duration,
            time=self.time,
            frequency=self.frequency,
            due_date=self.due_date + step,
        )
        self.pet.add_task(next_task)  # sets next_task.pet and appends it
        return next_task


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

    def sort_by_time(self) -> list[Task]:
        """Return every pet's tasks ordered chronologically by their "HH:MM"
        `time` attribute.

        Zero-padded "HH:MM" strings sort correctly with plain string
        comparison ("08:30" < "09:00" < "17:15"), so the sort key is just the
        string itself. Tasks with no time (time is None) are placed last.
        """
        all_tasks = [task for pet in self.owner.pets for task in pet.tasks]
        # (t.time is None) -> False sorts before True, so timed tasks come
        # first (ordered by their "HH:MM" string); untimed tasks fall to the
        # end. The `or ""` just gives None a safe stand-in to compare.
        return sorted(all_tasks, key=lambda t: (t.time is None, t.time or ""))

    def filter_tasks(
        self, pet_name: str | None = None, done: bool | None = None
    ) -> list[Task]:
        """Return this owner's tasks, optionally narrowed by pet name and/or
        completion status.

        Pass `pet_name` to keep only that pet's tasks (case-insensitive), and
        `done=True`/`done=False` to keep only completed/pending tasks. Leaving
        an argument as None means "don't filter on it", so filter_tasks() with
        no arguments returns every task.
        """
        tasks = [task for pet in self.owner.pets for task in pet.tasks]
        if pet_name is not None:
            tasks = [
                t for t in tasks
                if t.pet is not None and t.pet.name.lower() == pet_name.lower()
            ]
        if done is not None:
            tasks = [t for t in tasks if t.done == done]
        return tasks

    @staticmethod
    def _to_minutes(hhmm: str) -> int:
        """Convert an "HH:MM" time string into minutes since midnight."""
        hour, minute = hhmm.split(":")
        return int(hour) * 60 + int(minute)

    def detect_conflicts(self) -> list[str]:
        """Lightweight conflict check across all pets' pending, timed tasks.

        Two tasks conflict when their [start, start+duration) intervals
        overlap. Returns a list of human-readable warning strings (empty if
        there are no conflicts) so callers can print them instead of crashing.
        """
        timed = [
            t
            for pet in self.owner.pets
            for t in pet.tasks
            if t.time is not None and not t.done
        ]

        warnings: list[str] = []
        for a, b in combinations(timed, 2):
            start_a = self._to_minutes(a.time)
            start_b = self._to_minutes(b.time)
            end_a, end_b = start_a + a.duration, start_b + b.duration
            # Overlap iff each starts strictly before the other ends.
            if start_a < end_b and start_b < end_a:
                warnings.append(
                    f"⚠️  Conflict: '{a.category}' for {a.pet.name} at {a.time} "
                    f"({a.duration} min) overlaps '{b.category}' for "
                    f"{b.pet.name} at {b.time} ({b.duration} min)."
                )
        return warnings

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
