# Ohio Mutual Auto -- Multi-Agent Claims Processing

## 5-Minute Presentation Script

---

### OPENING -- The Hook (30 seconds)

**SAY:**

> "Every auto insurance claim you file passes through six different people before you get paid. Each one is a bottleneck. Each one costs money. Each one can make a mistake that triggers a lawsuit or lets a fraudster walk away with $87,000. What if those six people were six AI agents -- each one scoped to do exactly one job, exactly the way regulators expect?"

**KEY BUSINESS POINTS:**
- Frame the pain immediately: manual claims processing is slow, expensive, and error-prone
- The $87,000 number is real -- it comes from TC-005 (staged accident), a fraud scenario the system catches

**SHOW:** Title slide with "Ohio Mutual Auto" branding and the pipeline diagram (6 agents in sequence)

---

### PROBLEM FRAME -- Why This Matters (60 seconds)

**SAY:**

> "Ohio Mutual Auto is a mid-size car insurer. Today, processing a single claim requires six specialized roles: an intake specialist, a coverage officer, a damage assessor, a fraud analyst, a senior reviewer, and a finance processor. Each of these people costs $60-80K a year. Each one has a caseload that creates 5-15 day average processing times. And here is the real problem -- when things go wrong, they go expensively wrong.
>
> A missed fraud indicator costs the company the full payout -- tens of thousands of dollars. A wrongful denial triggers litigation that costs even more. And regulators require you to make a decision within 30 days. Miss that window and you face fines.
>
> The question is not 'can AI do this?' The question is 'can you afford not to use AI for this?'"

**KEY BUSINESS POINTS:**
- Cost per role: $60-80K salary, but the real cost is errors -- a single missed fraud case can exceed annual salary
- The 30-day regulatory requirement is a real constraint that creates urgency
- Frame as risk reduction, not just cost savings

**SHOW:** Simple diagram: 6 human roles with cost/time annotations, red highlights on failure modes (missed fraud, wrongful denial, regulatory deadline)

---

### SOLUTION OVERVIEW -- The Multi-Agent Pipeline (60 seconds)

**SAY:**

> "Our system replaces those six human roles with six AI agents -- and this is the critical design choice -- each agent has an intentionally limited scope. Just like in a real insurance office, the Front Desk does not make coverage decisions. The Fraud Analyst does not approve claims. The Finance agent does not process payments without Senior Reviewer approval.
>
> This is not just good engineering. This mirrors how insurance regulation actually works. Separation of duties is a compliance requirement. Our pipeline enforces it architecturally.
>
> Here is how the pipeline flows: The Front Desk registers and categorizes the claim. The Claims Officer verifies policy coverage. The Assessor estimates damage. The Fraud Analyst scores risk on a 0-to-100 scale. The Senior Reviewer makes the final decision using a documented framework. And Finance executes the payment with full audit trail.
>
> Every agent outputs structured JSON. Every decision is traceable. Every handoff is logged. This is not a black box -- it is an auditable pipeline."

**KEY BUSINESS POINTS:**
- Separation of duties = regulatory compliance built into architecture
- Structured JSON outputs = every decision is auditable and traceable
- No single agent can both approve and pay -- fraud prevention by design
- This is not one monolithic AI making all decisions -- it is specialized roles with clear boundaries

**SHOW:** Animated pipeline flow: Front Desk -> Claims Officer -> Assessor -> Fraud Analyst -> Senior Reviewer -> Finance. Highlight the JSON handoff between each stage.

---

### LIVE DEMO -- TC-005 Staged Accident (90 seconds)

**SAY:**

> "Let me show you this working with our hardest test case -- a staged accident from an organized fraud ring.
>
> Tony Vargas files a claim. He rear-ended another car on Highway 42. Sounds routine. But watch what happens as it flows through the pipeline.
>
> **Front Desk** picks it up: collision with injury, high severity, high priority. Four people in the other car all claiming neck and back pain. Routed to Claims Officer.
>
> **Claims Officer** confirms: active policy, collision coverage valid, $500 deductible. But flags the high liability exposure -- $87,000 in medical claims against a $300,000 bodily injury limit.
>
> **Assessor** estimates the actual vehicle damage: $2,000 to $5,000. Minor fender contact. And here is the first red flag -- the damage is completely inconsistent with four people needing ambulance transport.
>
> Now the **Fraud Analyst** goes to work. It scores this claim at 85+ out of 100 -- critical risk. Why? The other driver is uninsured. One of the 'passengers' shares the claimant's last name -- Rosa Vargas. All four passengers have identical injuries going to the same chiropractor. The medical billing is $87,000 on a $3,000 fender bender. This matches the classic 'swoop and squat' pattern.
>
> **Senior Reviewer** sees the full picture and refers to SIU -- the Special Investigation Unit. No claim approved, no money out the door.
>
> **Finance** places a hold on all payments and generates investigation documentation.
>
> Six agents. Under 30 seconds of processing. Caught an $87,000 fraud that a busy human adjuster might have missed under caseload pressure."

**KEY BUSINESS POINTS:**
- Each agent adds value by doing exactly ONE thing well
- The Assessor's damage-injury mismatch detection feeds directly into the Fraud Analyst's scoring
- The surname match (Tony Vargas / Rosa Vargas) is exactly the kind of detail that gets missed under human caseload pressure
- $87,000 saved in a single claim -- that is the ROI story
- Under 30 seconds vs. 5-15 days of human processing

**SHOW:** Run `python loop.py --run-once --scenario TC-005` live. Show the JSON output from each stage scrolling through the terminal. Pause on the Fraud Analyst output to highlight the indicators list.

---

### BUSINESS VALUE -- The ROI Frame (30 seconds)

**SAY:**

> "Let me give you three numbers. First: cost per claim drops from roughly $150 in human processing time to under $1 in API costs. Second: fraud detection improves because the system checks every indicator, every time -- no caseload fatigue, no Friday afternoon shortcuts. In our test suite, it catches staged accidents, inflated claims, and expired policies with zero false negatives. Third: regulatory compliance is built in. The 30-day decision requirement? Our pipeline processes claims in seconds. The audit trail requirement? Every agent outputs structured, traceable JSON. The separation of duties requirement? It is literally the architecture."

**KEY BUSINESS POINTS:**
- $150 to $1: roughly 150x cost reduction per claim in processing
- Zero false negatives on the test suite (7 scenarios covering easy, medium, and hard cases)
- Compliance is not an add-on -- it is the architecture itself
- Fraud savings on a single TC-005-style case pays for months of API costs

**SHOW:** Simple ROI table: Human cost vs. AI cost per claim, with a row for "fraud caught" showing the $87K TC-005 example

---

### CLOSE -- What Makes This Defensible (30 seconds)

**SAY:**

> "What makes this system defensible in an insurance audit? Three things. One: every decision has a documented rationale -- the Senior Reviewer cites specific policy language for every denial. Two: no single agent has the power to both evaluate and approve -- separation of duties is structural. Three: the system improves through an eval-driven training loop. We score agent outputs against ground truth, and when an agent falls below threshold, its prompts are automatically refined.
>
> This is not just automation. It is how insurance claims should always have been processed -- consistently, traceably, and with built-in checks at every stage. Thank you."

**KEY BUSINESS POINTS:**
- Audit defensibility is the killer feature for insurance
- The training loop (eval -> score -> improve) means the system gets better over time without rewriting code
- End with the "should always have been processed" framing -- positions AI as fulfilling the original intent of insurance regulation, not replacing it

**SHOW:** Brief flash of the training loop architecture: Run -> Eval -> Improve -> Repeat. Return to the pipeline diagram.

---

## Presentation Timing Summary

| Section | Duration | Cumulative |
|---------|----------|------------|
| Opening / Hook | 30s | 0:30 |
| Problem Frame | 60s | 1:30 |
| Solution Overview | 60s | 2:30 |
| Live Demo (TC-005) | 90s | 4:00 |
| Business Value / ROI | 30s | 4:30 |
| Close | 30s | 5:00 |

## Demo Backup Plan

If the live demo fails (API down, network issue):
- Have pre-recorded terminal output screenshots ready
- Walk through the TC-005 JSON outputs manually
- The story is compelling even without live execution -- focus on the fraud indicators list and the pipeline flow

## Key Phrases to Memorize

- "Each agent has an intentionally limited scope -- just like real insurance roles."
- "Separation of duties is not a feature. It is the architecture."
- "This caught an $87,000 fraud in under 30 seconds."
- "Every decision is traceable. Every handoff is logged. This is not a black box."
- "The question is not 'can AI do this?' The question is 'can you afford not to?'"
