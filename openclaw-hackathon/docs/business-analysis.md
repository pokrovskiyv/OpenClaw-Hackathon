# Ohio Mutual Auto — Business Context & Evaluation Metrics

## Who Is Ohio Mutual Auto and What's the Problem

Ohio Mutual Auto is a regional car insurance carrier. Their claims process is
entirely manual: a customer calls in an accident, and the claim travels through
six people before anything is decided. Each handoff introduces delay, human
error, and inconsistency.

The pipeline today looks like this:
- A front desk agent takes the initial call and categorizes the claim
- A claims officer checks whether the policy actually covers this event
- An assessor estimates the repair or replacement cost
- A fraud analyst reviews for suspicious patterns
- A senior reviewer makes the final approval decision
- A finance clerk executes the payment

Six people. Sequential. No automation. Each step waits for the previous one.
This is expensive, slow, and error-prone — and at scale, the errors compound.

The system described here automates this pipeline using six AI agents, one per
role, running sequentially and passing context forward.

---

## Key Business Priorities

The following five priorities drive every design decision in the system. They
are ordered from highest to lowest business risk — the further up the list, the
more expensive the mistake.

---

### 🔴 Priority 1: Fraud Detection

**What it is:** Identifying organized fraud schemes before money goes out the
door. Common patterns include inflated medical bills, coordinated passenger
injury claims, staged accidents ("swoop-and-squat" where one driver cuts off
another to manufacture a rear-end collision), and damage that doesn't match the
reported incident.

**Why it matters:** A single successfully prosecuted staged accident claim costs
the insurer $50,000–$150,000 in payments, plus investigation and legal costs.
At the industry level, auto insurance fraud accounts for roughly 15% of all
claims payouts in the US. That cost is passed directly to honest policyholders
as premium increases — which means fraud undermines both the company's finances
and its customer trust.

**Cost of missing it:** Direct financial loss on that claim, a precedent that
attracts repeat offenders to the same carrier, and potential regulatory scrutiny
if fraud patterns go undetected systematically.

---

### 🟠 Priority 2: Coverage Validation

**What it is:** Verifying that the claimed event is actually covered by the
policy. This means checking that the policy was active on the date of loss, that
the type of coverage (collision, comprehensive, liability, etc.) applies to this
type of incident, and that no exclusions have been triggered — for example, a
policy that excludes coverage when the vehicle is used for commercial purposes.

**Why it matters:** Paying a claim that is not covered by the policy is a pure
financial loss with no recovery path. Worse, it creates legal exposure: if the
company pays for something not in the contract, it may set a precedent that
undermines future denials. On the other side, denying a valid claim creates
regulatory risk and bad faith litigation.

**Cost of missing it:** The company absorbs a loss it was never contractually
obligated to cover, or faces a lawsuit for wrongfully denying one it was.

---

### 🟠 Priority 3: Coverage Routing

**What it is:** When multiple types of coverage could apply to the same incident,
selecting the one that best serves the policyholder. For example, a glass
replacement claim might be processable under collision coverage (with a $500
deductible) or comprehensive coverage (with a $50 deductible). The right answer
for the customer is obvious; the wrong system routes it mechanically or not at
all.

**Why it matters:** Customers who receive optimal coverage outcomes — paying the
lowest deductible they're entitled to — are less likely to dispute the claim,
more likely to renew, and less likely to generate legal complaints. Poor routing
reduces customer retention and increases dispute volume, both of which have
measurable financial consequences.

**Cost of missing it:** The customer pays more out-of-pocket than they should,
generates a complaint, escalates to a supervisor, or files a regulatory
complaint. Each of these costs more to resolve than routing correctly in the
first place.

---

### 🟡 Priority 4: Damage Assessment

**What it is:** Accurately estimating the cost of repair or replacement.
This includes determining whether a vehicle has crossed the total loss threshold
— the point where repair cost exceeds a defined percentage of the vehicle's
actual cash value (ACV). In most US states, that threshold is 75% of ACV.
When the threshold is crossed, the correct outcome is to declare total loss and
pay ACV rather than authorize repairs.

**Why it matters:** Overestimating damage means overpaying. Underestimating
invites a bad faith lawsuit from the customer when the repair shop comes back
with a higher bill. Failing to declare total loss when the threshold is crossed
is a regulatory violation in many jurisdictions.

**Cost of missing it:** Financial loss in either direction. The total loss
threshold is not a judgment call — it is a regulated requirement, and getting
it wrong exposes the company to fines, not just claims disputes.

---

### 🟢 Priority 5: Subrogation Identification

**What it is:** Determining whether a third party is legally at fault for the
loss, and if so, initiating a subrogation claim — a legal process where the
insurer pays the customer first, then recovers that amount from the at-fault
party's insurance carrier.

**Why it matters:** Subrogation is a direct revenue recovery mechanism. The
company has already paid the customer. Subrogation is how some or all of that
money comes back. Missing a valid subrogation opportunity means money that could
be recovered simply isn't.

**Cost of missing it:** No immediate crisis, but accumulated missed subrogation
across thousands of claims represents a material gap in financial recovery.
Unlike fraud or coverage errors, the mistake here is not in what was paid — it's
in what was never reclaimed.

---

## The Evaluation Metric

### Combined Evaluation Score (0–100)

Every claim run through the system produces a Combined Evaluation Score:

```
Score = Rule-Based Score × 0.40 + LLM-Judge Score × 0.60
```

This is not a single number — it is computed per agent, then averaged across
all six agents for a final pipeline score.

---

### Rule-Based Component (40% of score)

The rule-based component checks objective, verifiable properties of each
agent's output:

- **Field presence:** Did the agent return all required fields?
- **Value correctness:** Does the decision match the expected outcome (approved,
  denied, flagged)?
- **Numeric accuracy:** Does the damage estimate fall within an acceptable range?
- **Flag detection:** Did the fraud analyst flag the patterns that should have
  been detected?
- **Threshold compliance:** Did the assessor correctly identify total loss when
  repair cost exceeded 75% of ACV?

These checks are deterministic and fast. They verify *what* was produced.
A score of 100 on this component means the output had the right structure and
the right values — but says nothing about whether the reasoning behind those
values was sound.

---

### LLM-Judge Component (60% of score)

The LLM judge evaluates properties that rules cannot capture:

- **Correctness:** Did the agent reach the right conclusion given all available
  information?
- **Completeness:** Did the agent address all aspects of its role, or did it
  ignore relevant context?
- **Business logic:** Would a real claims professional approve of this decision?
  Does it follow insurance norms and company policy?
- **Format compliance:** Is the output structured correctly for downstream agents
  to consume?
- **Reasoning quality:** Is the chain of reasoning documented, defensible, and
  free of contradictions?

The LLM judge score carries more weight (60%) because it evaluates *why* a
decision was made — not just what the decision was. In insurance, an incorrect
decision made for defensible reasons is recoverable through review. An incorrect
decision made for bad or absent reasons is a systemic risk.

---

### Why This Split

Rule-based checks are fast, cheap, and deterministic — but they only catch
structural errors. An agent could return all the right fields with plausible
numbers while still applying completely wrong business logic. The LLM judge
catches this class of error.

Conversely, the LLM judge has variance — it can be lenient or strict depending
on how a judgment call is framed. Rule-based checks anchor the score to
objective ground truth. Together, the 60/40 split balances deterministic
accuracy with qualitative judgment.

---

### Passing Threshold: 85/100

A pipeline score of 85 or above is considered production-ready. Below that
threshold, any agent scoring under 90 has its system prompt automatically
revised based on the evaluation feedback, and the pipeline is retrained.

This threshold is deliberately conservative. At 85, the system is reliable
enough to process claims without human review on standard cases, while leaving
room for improvement on edge cases and ambiguous scenarios.

---

### How Business Priorities Map to the Metric

| Business Priority | What the Metric Measures |
|---|---|
| Fraud Detection | Fraud flags detected vs. expected; reasoning about suspicious patterns |
| Coverage Validation | Correct covered/denied decision; exclusion identification |
| Coverage Routing | Optimal coverage type selected; deductible minimized for customer |
| Damage Assessment | Estimate within acceptable range; total loss threshold applied correctly |
| Subrogation | Third-party liability identified; recovery action initiated |

Each business priority has both a rule-based dimension (did the right fields
appear with the right values?) and an LLM-judge dimension (was the decision
reached in a way that a professional would endorse?). The combined score
captures both.
