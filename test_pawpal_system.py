"""Tests for PawPal+ core behaviors. Run with: python -m pytest"""

from pawpal_system import Pet, Task


def test_mark_complete_changes_status():
    """Task Completion: mark_complete() flips the task's status to done."""
    task = Task(category="Walk", priority=8, duration=30)
    assert task.done is False

    task.mark_complete()

    assert task.done is True


def test_adding_task_increases_pet_task_count():
    """Task Addition: adding a task to a pet increases that pet's task count."""
    rex = Pet(id=1, name="Rex", breed="Labrador", age=3)
    assert len(rex.tasks) == 0

    rex.add_task(Task(category="Walk", priority=8, duration=30))

    assert len(rex.tasks) == 1
