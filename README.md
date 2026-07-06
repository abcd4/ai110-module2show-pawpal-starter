# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## ✨ Features

PawPal+ manages care tasks across **multiple pets** for a single owner. The
scheduling intelligence lives in the `Scheduler` and `Task` classes; the
Streamlit UI in `app.py` is a thin layer over them.

| # | Feature | Where it lives | What it does |
|---|---------|----------------|--------------|
| 1 | **Priority-based daily planning** | `Scheduler.get_daily_tasks()` | Gathers every pet's pending tasks, sorts them by priority (highest first), then greedily packs each into the first free availability window with room for its duration. Tasks that fit nowhere are reported as "couldn't fit today." |
| 2 | **Sorting by time** | `Scheduler.sort_by_time()` | Returns all tasks in chronological order by their `HH:MM` time; untimed tasks sort to the end. |
| 3 | **Filtering** | `Scheduler.filter_tasks(pet_name, done)` | Narrows tasks by pet name (case-insensitive) and/or completion status. No arguments returns everything. |
| 4 | **Conflict warnings** | `Scheduler.detect_conflicts()` | All-pairs overlap check across pending, timed tasks. Flags any two whose `[start, start+duration)` intervals overlap — catching partial overlaps, not just identical start times — and returns plain-language warnings instead of crashing. |
| 5 | **Daily / weekly recurrence** | `Task.mark_complete()` | Completing a `daily` or `weekly` task auto-spawns its next occurrence on the same pet, dated one interval later. One-time tasks simply complete. |

All five operate **across every pet the owner has**, not a single pet's list.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
# e.g.:
# Daily plan for Biscuit (Golden Retriever):
#   08:00 — Morning walk (30 min) [priority: high]
#   09:00 — Feeding (10 min) [priority: high]
#   ...
```


Today's Schedule for Sam
(available: 8:00 AM-8:30 AM, 5:30 PM-8:00 PM)
--------------------------------------------
  8:00 AM — Give medication for Rex (5 min) [priority: 10]
  8:05 AM — Feeding for Rex (10 min) [priority: 9]
  5:30 PM — Morning walk for Rex (40 min) [priority: 8]
  6:10 PM — Enrichment play for Bella (30 min) [priority: 6]
  6:40 PM — Grooming for Bella (45 min) [priority: 2]


## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest


# Run with coverage:
pytest --cov
```

Sample test output:

```
============================= test session starts ==============================
platform darwin -- Python 3.12.4, pytest-9.1.1, pluggy-1.6.0
rootdir: /Users/nicoleonye/ai110-module2show-pawpal-starter
collected 2 items

test_pawpal_system.py::test_mark_complete_changes_status PASSED          [ 50%]
test_pawpal_system.py::test_adding_task_increases_pet_task_count PASSED  [100%]

============================== 2 passed in 0.01s ===============================
```

## 📐 Smarter Scheduling

Beyond the basic priority-packing plan, PawPal+ adds four "smarter scheduling"
behaviors. Each is a small, independently testable method on Scheduler (or
Task) so you can pick the behavior you need at call time.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | Scheduler.sort_by_time() | Returns every pet's tasks in chronological order by their HH:MM time attribute; untimed tasks sort last. |
| Filtering | Scheduler.filter_tasks(pet_name=None, done=None) | Narrows tasks by pet name (case-insensitive) and/or completion status; no args returns all tasks. |
| Conflict handling | Scheduler.detect_conflicts() | Compares every pair of pending, timed tasks and returns warning strings for any whose `[start, start+duration)` intervals overlap — warns, never crashes. |
| Recurring tasks | Task.mark_complete() → Task._spawn_next_occurrence() | Completing a "daily"/"weekly" task auto-creates the next occurrence (via timedelta) on the same pet and returns it. |

### Sorting behavior — Scheduler.sort_by_time()
Sorts tasks by their zero-padded "HH:MM" time string using
key=lambda t: (t.time is None, t.time or ""), so timed tasks come first in
clock order and untimed tasks fall to the end. This is separate from
get_daily_tasks(), which orders by priority to pack the day.

### Filtering behavior — Scheduler.filter_tasks(...)
One method covers both "show me just this pet's tasks" (pet_name="Rex") and
"show me only pending / only completed tasks" (done=False / done=True).
Arguments left as None are not filtered on, so combinations work naturally.

### Conflict detection logic — Scheduler.detect_conflicts()
Uses an all-pairs check (itertools.combinations) over pending, timed tasks.
Two tasks conflict when each starts strictly before the other ends, so it
catches partial overlaps (a 40-min walk at 17:30 clashes with an 18:00 task),
not just identical start times. Returns a list of human-readable warning
strings (empty when the day is clear) rather than raising.

### Recurring task logic — Task.mark_complete()
Marking a recurring task complete flips done = True and then spawns the next
occurrence: a fresh Task with the same fields but due_date advanced by
timedelta(days=1) (daily) or timedelta(weeks=1) (weekly), attached to the
same pet. One-time tasks (frequency=None) just complete and return None.



## Testing PawPal+ Pt. 2
python -m pytest
Sorting

test_sort_by_time_returns_chronological_order — tasks added out of order come back sorted earliest-to-latest by "HH:MM" time.
test_sort_by_time_places_untimed_tasks_last — tasks with no time (None) are pushed to the end, after all timed tasks.
Recurrence
3. test_daily_task_completion_spawns_next_day_occurrence — completing a "daily" task creates a new task due +1 day, attached to the same pet, done=False, and appended to the pet's task list.
4. test_one_time_task_completion_spawns_nothing — completing a task with no frequency returns None and adds no new task.

Conflict detection
5. test_detect_conflicts_flags_tasks_at_the_same_time — two pending tasks at the identical time produce exactly one warning.
6. test_adjacent_tasks_do_not_conflict — back-to-back tasks that only touch at the boundary (08:00–08:30 and 08:30–09:00) are not flagged.
7. test_completed_tasks_are_ignored_by_conflict_detection — a done task doesn't conflict with a pending one; only pending timed tasks count.

Edge case: empty world
8. test_pet_with_no_tasks_returns_empty_results — a pet with no tasks returns [] from sort_by_time, filter_tasks, detect_conflicts, and get_daily_tasks without crashing.


Output: 
(base) nicoleonye@MacBook-Pro-3 ai110-module2show-pawpal-starter % python -m pytest 
============================= test session starts ==============================
platform darwin -- Python 3.12.4, pytest-9.1.1, pluggy-1.6.0
rootdir: /Users/nicoleonye/ai110-module2show-pawpal-starter
collected 10 items                                                             

test_pawpal_system.py ..                                                 [ 20%]
tests/test_pawpal.py ........                                            [100%]

============================== 10 passed in 0.01s ==============================


Condidence level: 3

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
