"""Behavior tests for the PawPal+ Scheduler.

Run from the repo root with:  python -m pytest tests/test_pawpal.py
(`python -m pytest` puts the repo root on sys.path, so the import below works.)

Each test follows Arrange / Act / Assert: build a small world, run one
behavior, then check exactly one thing about the result.
"""

from datetime import date, timedelta

from pawpal_system import Owner, Pet, Scheduler, Task


# ---------------------------------------------------------------------------
# Sorting correctness
# ---------------------------------------------------------------------------

def test_sort_by_time_returns_chronological_order():
    """sort_by_time() orders tasks by their "HH:MM" time, earliest first."""
    # Arrange: one pet with three tasks added OUT of time order on purpose,
    # so a passing test proves the sort ran (not just insertion order).
    rex = Pet(id=1, name="Rex", breed="Labrador", age=3)
    rex.add_task(Task(category="Dinner", priority=5, duration=15, time="17:15"))
    rex.add_task(Task(category="Walk", priority=8, duration=30, time="08:30"))
    rex.add_task(Task(category="Lunch", priority=6, duration=20, time="12:00"))

    owner = Owner(name="Sam", pets=[rex])
    scheduler = Scheduler(owner=owner)

    # Act
    ordered = scheduler.sort_by_time()

    # Assert: pull the times back out and confirm they climb.
    assert [t.time for t in ordered] == ["08:30", "12:00", "17:15"]


def test_sort_by_time_places_untimed_tasks_last():
    """Tasks with no time (time is None) fall to the end of the sorted list."""
    rex = Pet(id=1, name="Rex", breed="Labrador", age=3)
    rex.add_task(Task(category="Vet", priority=9, duration=60))  # time=None
    rex.add_task(Task(category="Walk", priority=8, duration=30, time="08:30"))

    scheduler = Scheduler(owner=Owner(name="Sam", pets=[rex]))

    ordered = scheduler.sort_by_time()

    # The timed task comes first; the untimed one is pushed to the back.
    assert ordered[0].time == "08:30"
    assert ordered[-1].time is None


# ---------------------------------------------------------------------------
# Recurrence logic
# ---------------------------------------------------------------------------

def test_daily_task_completion_spawns_next_day_occurrence():
    """Completing a "daily" task creates a fresh task, due one day later,
    attached to the same pet and not yet done."""
    # Arrange: a daily task with an explicit due_date so we can check the math.
    rex = Pet(id=1, name="Rex", breed="Labrador", age=3)
    today = date(2026, 7, 6)
    walk = Task(
        category="Walk", priority=8, duration=30,
        frequency="daily", due_date=today,
    )
    rex.add_task(walk)

    # Act: mark_complete() returns the spawned occurrence (or None).
    next_walk = walk.mark_complete()

    # Assert: the original is done; a new one exists for tomorrow.
    assert walk.done is True
    assert next_walk is not None
    assert next_walk.due_date == today + timedelta(days=1)
    assert next_walk.done is False
    assert next_walk.pet is rex           # attached to the same pet
    assert next_walk in rex.tasks         # and appended to its task list
    assert len(rex.tasks) == 2            # original + spawned


def test_one_time_task_completion_spawns_nothing():
    """A task with no frequency returns None on completion (no recurrence)."""
    rex = Pet(id=1, name="Rex", breed="Labrador", age=3)
    bath = Task(category="Bath", priority=4, duration=45)  # frequency=None
    rex.add_task(bath)

    result = bath.mark_complete()

    assert result is None
    assert len(rex.tasks) == 1  # nothing new was added


# ---------------------------------------------------------------------------
# Conflict detection
# ---------------------------------------------------------------------------

def test_detect_conflicts_flags_tasks_at_the_same_time():
    """Two pending tasks scheduled at the identical time overlap, so
    detect_conflicts() reports exactly one warning."""
    rex = Pet(id=1, name="Rex", breed="Labrador", age=3)
    rex.add_task(Task(category="Walk", priority=8, duration=30, time="08:00"))
    rex.add_task(Task(category="Meds", priority=9, duration=10, time="08:00"))

    scheduler = Scheduler(owner=Owner(name="Sam", pets=[rex]))

    warnings = scheduler.detect_conflicts()

    assert len(warnings) == 1


def test_adjacent_tasks_do_not_conflict():
    """Back-to-back tasks that only touch at the boundary (08:00-08:30 and
    08:30-09:00) must NOT be flagged — overlap uses strict inequality."""
    rex = Pet(id=1, name="Rex", breed="Labrador", age=3)
    rex.add_task(Task(category="Walk", priority=8, duration=30, time="08:00"))
    rex.add_task(Task(category="Feed", priority=6, duration=30, time="08:30"))

    scheduler = Scheduler(owner=Owner(name="Sam", pets=[rex]))

    assert scheduler.detect_conflicts() == []


def test_completed_tasks_are_ignored_by_conflict_detection():
    """A done task at the same time as a pending one is not a conflict —
    detect_conflicts() only considers still-pending, timed tasks."""
    rex = Pet(id=1, name="Rex", breed="Labrador", age=3)
    done_walk = Task(category="Walk", priority=8, duration=30, time="08:00")
    done_walk.done = True
    rex.add_task(done_walk)
    rex.add_task(Task(category="Meds", priority=9, duration=10, time="08:00"))

    scheduler = Scheduler(owner=Owner(name="Sam", pets=[rex]))

    assert scheduler.detect_conflicts() == []


# ---------------------------------------------------------------------------
# Edge case: empty world
# ---------------------------------------------------------------------------

def test_pet_with_no_tasks_returns_empty_results():
    """A pet with no tasks must not crash the read-only queries."""
    rex = Pet(id=1, name="Rex", breed="Labrador", age=3)
    scheduler = Scheduler(owner=Owner(name="Sam", pets=[rex], availability=[(480, 600)]))

    assert scheduler.sort_by_time() == []
    assert scheduler.filter_tasks() == []
    assert scheduler.detect_conflicts() == []
    assert scheduler.get_daily_tasks() == []
