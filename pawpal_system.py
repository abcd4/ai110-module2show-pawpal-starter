"""PawPal+ system class skeletons.

Skeleton generated from diagrams/uml.mmd. Method bodies are stubs to be
filled in during implementation.
"""

from dataclasses import dataclass, field


@dataclass
class Pet:
    name: str
    breed: str
    age: int
    medications: list[str] = field(default_factory=list)


@dataclass
class Owner:
    name: str
    pets: list[Pet] = field(default_factory=list)


@dataclass
class Task:
    category: str
    pet: Pet
    priority: int


@dataclass
class Scheduler:
    tasks: list[Task] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        ...

    def remove_pet(self, pet: Pet) -> None:
        ...

    def add_task(self, task: Task) -> None:
        ...

    def remove_task(self, task: Task) -> None:
        ...

    def get_daily_tasks(self) -> list[Task]:
        ...
