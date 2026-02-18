# Business Defense -- Why Each Agent Exists

## Agent-by-Agent Business Rationale

### 1. Front Desk Agent -- FNOL Intake

The Front Desk exists as a separate agent because claim intake is a distinct regulatory function. Every state requires First Notice of Loss documentation before any claim activity can begin. This agent's only job is to register the claim, validate that required information is present, and categorize the incident. It does not make coverage decisions, assess fraud, or estimate damage. This boundary matters because if intake and coverage verification were combined, a coverage denial could bias how information is collected -- the system might not fully document a claim it already "knows" will be denied, which creates legal exposure when claimants challenge the denial. Keeping intake separate ensures every claim is fully documented regardless of outcome.

### 2. Claims Officer Agent -- Coverage Verification

The Claims Officer exists because coverage determination is a factual lookup with legal consequences. Is the policy active? Does the coverage type match the incident? Are there exclusions? These are binary questions with auditable answers. This agent is separate from the Senior Reviewer because the person who verifies facts should not be the same person who makes judgment calls. If the same agent both verified coverage and decided the claim, there would be no independent check on coverage interpretation. The Claims Officer also optimizes for the claimant -- when multiple coverage paths exist (e.g., collision vs. UMPD for hit-and-run), it recommends the one with the lower deductible. This customer-favorable default is easier to enforce when it is the agent's only job.

### 3. Assessor Agent -- Damage Evaluation

The Assessor exists as a separate role because damage estimation is a technical function that requires domain-specific knowledge (parts costs, labor rates, ACV calculation, total loss thresholds) distinct from policy knowledge or fraud detection. Critically, the Assessor provides an independent damage evaluation that feeds into fraud detection -- if the Assessor and Fraud Analyst were combined, the damage estimate might be unconsciously influenced by fraud suspicion, producing biased numbers. By keeping assessment independent, the Assessor's damage-injury mismatch observations become credible evidence for the Fraud Analyst rather than circular reasoning. The 75% ACV total loss threshold is a standard the Assessor applies mechanically, removing subjective judgment from what should be a mathematical determination.

### 4. Fraud Analyst Agent -- Risk Scoring

The Fraud Analyst exists as a separate agent because fraud detection is adversarial work that requires a different mindset from claim processing. This agent applies a structured scoring rubric (0-100) across four categories -- timing, incident, damage/medical, and behavioral red flags -- with specific point values for each indicator. Separating fraud analysis from claim decision-making is essential for two reasons. First, it prevents fraud suspicion from prejudicing the claim decision before evidence is gathered. Second, it creates a documented, defensible fraud assessment that can withstand legal challenge. The Fraud Analyst uses careful language ("indicators present," "patterns consistent with") precisely because its output may become evidence in SIU investigations or court proceedings. An agent that both detects fraud and denies claims would face challenges to objectivity.

### 5. Senior Reviewer Agent -- Final Decision

The Senior Reviewer is the decision-maker and exists because someone must synthesize all upstream analysis into a single, documented decision. This agent has override authority -- it can approve a claim the Fraud Analyst flagged as moderate risk if the evidence is thin, or investigate a claim the Fraud Analyst scored as low risk if other pipeline data raises concerns. The decision matrix (coverage valid x fraud risk x damage consistency) provides a structured framework, but the Senior Reviewer also applies judgment and equity considerations. This is the only agent that can approve, deny, investigate, or refer -- consolidating the final decision in one role ensures accountability. Every denial must cite specific policy language, every approval must show the payout math, and every investigation must list specific next steps. This is where the audit trail culminates.

### 6. Finance Agent -- Payment Processing

Finance exists as a separate agent because of the fundamental internal control principle: the person who approves a payment should never be the same person who executes it. This is not just insurance regulation -- it is basic financial controls (SOX, GAAP). The Finance agent validates that Senior Reviewer approval exists, recalculates the payment amount independently, determines the payment method, identifies subrogation opportunities, and manages rental reimbursement. If Finance were part of the Senior Reviewer, a single compromised or malfunctioning agent could both approve and pay a fraudulent claim. The separation also enables financial reporting -- Finance generates documentation, tracks subrogation recovery, and calculates net claim cost, all of which are finance-department functions that should not be mixed with claims adjudication.

---

## Design Trade-offs We Made

### Why Not Fewer Agents?

We considered consolidating to 3-4 agents (intake+coverage, assessment+fraud, decision+payment). We rejected this because:

- **Regulatory risk**: Insurance regulators expect separation of duties. Combining coverage verification with claim decision eliminates an independent checkpoint. Combining fraud detection with assessment creates bias. Combining decision with payment violates financial controls.
- **Debugging difficulty**: When a 4-agent system produces a bad output, the failure could be in any of 2-3 combined responsibilities. With 6 agents, failures are immediately localized. Our eval loop scores each agent independently -- this is only possible when responsibilities are separated.
- **Prompt quality**: LLM performance degrades as prompts grow larger and more complex. A focused 100-line prompt for fraud detection outperforms a 300-line prompt that also handles assessment and coverage. Smaller scope means higher quality outputs.

The marginal API cost of 6 calls vs. 3 calls is negligible compared to the compliance, debugging, and quality benefits.

### Why Not Have Finance Be Part of Senior Reviewer?

This was the most tempting consolidation. The Senior Reviewer already calculates the payout amount -- why not have it also execute the payment? Three reasons:

1. **Separation of authorization and execution**: This is a foundational financial control. In every well-run organization, the person who says "pay $10,000" is not the same person who sends the wire. Combining these creates a single point of failure for financial fraud.
2. **Subrogation is a separate function**: Identifying and pursuing recovery from at-fault third parties (subrogation) is a finance function with its own logic, timelines, and tracking requirements. Mixing subrogation management into the claims decision agent would dilute both functions.
3. **Audit separation**: Financial auditors need to trace the chain from "decision to pay" to "payment executed" as two distinct events with two distinct authorizations. A single agent doing both produces one audit record instead of two.

### Why Strict Pipeline vs. Parallel Processing?

We use a sequential pipeline (Front Desk -> Claims Officer -> Assessor -> Fraud Analyst -> Senior Reviewer -> Finance) rather than running agents in parallel. This is intentional:

- **Information dependency**: Each agent needs the previous agent's output. The Claims Officer needs the Front Desk's categorization. The Fraud Analyst needs both the Claims Officer's coverage flags and the Assessor's damage estimate. The Senior Reviewer needs everything. True parallelism is not possible for most of the pipeline.
- **Early termination**: If the Claims Officer determines the policy is expired, the Assessor and Fraud Analyst can skip their work entirely (they output `{"action": "skip", "reason": "no_coverage"}`). This saves API costs and processing time. In parallel, you would waste those calls.
- **Audit trail ordering**: Regulators expect a logical processing sequence. A parallel execution model makes it harder to explain when each decision was made and what information was available at the time.

The one place parallelism could help is running the Assessor and Fraud Analyst simultaneously (they are somewhat independent). We chose not to do this to maintain a clean sequential audit trail and because the Fraud Analyst benefits from the Assessor's damage-injury consistency flags.

### What Human Oversight Points Exist?

The system has four explicit human intervention points:

1. **SIU Referral**: When the Fraud Analyst scores a claim at critical risk (71-100) or identifies organized fraud patterns, the Senior Reviewer routes to the Special Investigation Unit. Human investigators take over.
2. **Legal Referral**: When a claim involves attorney representation, disputed liability, or potential litigation, the Senior Reviewer routes to legal. Human attorneys handle communication.
3. **Management Escalation**: For claims exceeding certain complexity thresholds or involving reputational risk, the Senior Reviewer can route to management.
4. **Training Loop Review**: The eval-driven improvement loop scores agent outputs automatically, but the decision to accept prompt rewrites and the design of new test scenarios involves human judgment.

The system is designed for the 80/20 rule: automate the 80% of claims that follow standard patterns, and route the 20% that require human judgment to the right humans with full documentation already prepared.

---

## Architecture Defensibility Summary

| Challenge | Our Defense |
|-----------|-------------|
| "It is a black box" | Every agent outputs structured JSON with documented rationale. The full pipeline output for any claim is a complete audit trail. |
| "AI makes mistakes" | The eval loop catches regressions. Rule-based checks validate numeric ranges and required fields. Downstream agents cross-validate upstream outputs. |
| "One agent could go rogue" | No single agent can both approve and pay. Separation of duties is structural, not procedural. |
| "It cannot handle edge cases" | The system defaults to escalation for uncertainty. "Investigate" is always safer than "deny" or "approve" when the data is ambiguous. |
| "Regulators will not accept this" | The pipeline mirrors existing regulatory structure. Six roles, separation of duties, documented decisions, 30-day compliance tracking, appeal rights disclosure. The architecture is more compliant than most human operations. |
| "What about the secret addition?" | Each agent has a focused scope with clear inputs and outputs. Adding new requirements means updating the relevant agent's prompt and adding eval criteria. The architecture adapts without restructuring. |
