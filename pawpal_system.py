"""PawPal+ system class skeletons.

Skeleton generated from diagrams/uml.mmd. Method bodies are stubs to be
filled in during implementation.
"""

from dataclasses import dataclass, field


@dataclass
class Pet:
    id: int  # stable identity; two pets can share a name, not an id
    name: str
    breed: str
    age: int
    medications: list[str] = field(default_factory=list)


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
    pet: Pet
    priority: int  # higher = more urgent
    duration: int  # minutes; used to pack tasks into the day's time budget


@dataclass
class Scheduler:
    """Per-owner scheduler. Pets live on the owner; the scheduler reaches
    them through self.owner.pets and manages the owner's tasks."""

    owner: Owner
    tasks: list[Task] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Register a pet on the owner (self.owner.pets)."""
        ...

    def remove_pet(self, pet: Pet) -> None:
        """Remove a pet from the owner and cascade-remove its tasks so no
        task is left pointing at a pet that no longer exists."""
        ...

    def add_task(self, task: Task) -> None:
        ...

    def remove_task(self, task: Task) -> None:
        ...

    def get_daily_tasks(self) -> list[Task]:
        """Build today's plan: sort tasks by priority, then greedily place
        each task into the first of self.owner.availability's (start, end)
        blocks that still has room for its duration, skipping any task that
        fits in no remaining block."""
        ...
