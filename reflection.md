# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**
- Briefly describe your initial UML design.
A user should be able to add/remove a pet, add/remove a task for a pet, and see the day's tasks.
- What classes did you include, and what responsibilities did you assign to each?
The classes needed will be an owner class, a pet class, a task class, and a scheduler class.
  - An owner will include a name, ,pet list. It will have no methods.
  - A pet will include: name, breed, age, medications. It will have no methods.
  - A task will include: category (type of task e.g feeding, hospital, grooming), pet (the pet which the task is done for), and priority level. It will have no methods.
  - A scheduler will include: a task list. It will have be able to add/remove a pet, add/remove a task (sorting and priortization logic will be handled here)


**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.
I made several significant changes during implementation. By adding an id field to pet, I ensure that each pet is uniquely identifiable even if they share the same name. Scheduler and Owner are now linked so that add/remove pets is valid (self.owner.pets can be called). I also fixed task logic. By providing a duration in minutes, the scheduler will be able to properly allocate and prioritize according time. To further ensure the prioritizaiton logic is sound, I added a list called availbility to the owner class, which provides time increments throughout the day where the owner is busy. This is because the owner may not have just one big window of time when they are free.
---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

My scheduler detects conflicts but does not resolve them. detect_conflicts()
compares every pair of pending, timed tasks and checks whether their
`[start, start + duration)` intervals overlap, then returns a list of warning
strings. It deliberately does nothing more — it never reorders, shortens, or
drops a task to make the clash go away; it just warns the owner and lets them
decide. I chose interval-overlap detection (not just exact "HH:MM" matches) so a
40-minute walk starting at 17:30 correctly flags against an 18:00 task, but I
stopped short of auto-resolution.

This is reasonable for a pet owner: which task yields when a vet visit collides
with a walk is a human judgment call (rescheduling the vet is not something the
app should silently do), so surfacing a clear warning is more useful and less
error-prone than guessing. The cost is that the schedule can still contain
overlaps the program knowingly allows — but that is an acceptable,
human-in-the-loop tradeoff at this scale.

A related tradeoff: the check is O(n²) all-pairs. A sorted sweep-line would be
O(n log n), but for the handful of tasks in a real day the simpler, more
readable all-pairs version is worth more than the speed I'd gain.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?
I used AI tools to act as a constant collaborator, especially during the refactoring stages. As I was going through the instructions, I noticed my UML would read different than what was indicated in the instructions. When I didn't know how to move forward, asking about my options for how to approach the code were incredibly helpful. 
**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?
There were times where Claude would suggest an edits for the implementation of functions. I often found myself in positions where I agreed with one part but then had questions on another. I would offen opt for the "else" option when Claude asked if I would accept the changes made. I would then say "yes, but explain the part where _____". Based on what I understood of my implmementaion logic I would then decide whether that part of what AI suggested made the most sense.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

a. What you tested

I tested the three behaviors with the most logic: sorting, recurrence, and conflict detection. For sorting, I checked that scrambled tasks come back in chronological order and untimed ones sort last. For recurrence, that completing a "daily" task spawns a new task due the next day, while a one-time task spawns nothing. For conflicts, that two tasks at the same time flag exactly one warning, that back-to-back tasks touching at the boundary don't flag, and that completed tasks are ignored.

These mattered because they're the parts most likely to hide a subtle bug — the boundary test, for example, guards an off-by-one in my overlap check.
**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

About a 3 out of 5. All tests pass and are deterministic, but my most complex method, get_daily_tasks() (the priority-packing), has no direct test yet, and every test uses a single pet even though the system is built for multiple. Next I'd test get_daily_tasks() (priority order, skipping tasks too long to fit), add a multi-pet test, cover filter_tasks(), and run pytest --cov for a real coverage number.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
I am most satisfied getting to run the code in Streamlit. I love the deploying stage because seeing the logic actually work is like seeing a puzzle come together. 
**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
If i had another iteration, I would want to read through all of the instructions first because there were times where I felt incredibly confused when I saw a function being referenced, even though it hadn't been mentioned before and I had already passed the initial UML stage.
**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
One thing I learned about designing systems while working with AI is that you are always iterating. As you work through a problem, new questions arise, which lead to new edge cases. In order to build a strong system, you need to make sure these are considered. Thus, you need to be ready to always iterate and change your code for these cases. AI is a very useful tool when you have to navigate that ongoing change.