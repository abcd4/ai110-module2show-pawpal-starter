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

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
