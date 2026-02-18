# Q&A Preparation -- Ohio Mutual Auto Multi-Agent Claims Pipeline

## Format Notes

Each question includes:
- **Model Answer** (2-3 sentences, emphasis on business reasoning)
- **If They Push Back** (1 sentence follow-up)

Target: 15+ questions across Business, Technical, Edge Cases, and Secret Addition categories.

---

## Business Questions

### Q1: "Why 6 agents instead of fewer?"

**Model Answer:** Each agent maps to a real insurance role that exists for regulatory and operational reasons. Separation of duties is not optional in insurance -- it is a compliance requirement. If one agent could both assess damage and approve payment, you lose the internal controls that auditors and regulators expect. Six agents means six checkpoints, each with a clear audit trail.

**If they push back:** "Fewer agents means fewer audit checkpoints. In a regulated industry, the cost of a compliance failure far exceeds the cost of an extra API call."

---

### Q2: "What happens if the AI makes a bad fraud call and denies a legitimate claim?"

**Model Answer:** First, the Fraud Analyst does not deny claims -- it only scores risk and flags indicators. The actual decision lives with the Senior Reviewer, who has override authority and is required to document rationale. For moderate-risk scores with thin evidence, the Reviewer can approve with notes. For legitimate customers, the system defaults to "investigate" rather than "deny" -- investigation is cheaper than a lawsuit from wrongful denial.

**If they push back:** "The system is designed to err toward investigation over denial, because a false denial costs more in litigation and reputation than the cost of gathering more information."

---

### Q3: "How do you handle regulatory compliance? What if a state requires specific language?"

**Model Answer:** The Senior Reviewer agent has a built-in regulatory compliance checklist: 30-day decision window, specific policy language citations for denials, appeal rights disclosure, and complete audit trail verification. State-specific language requirements can be handled by adding state regulatory templates to the agent's prompt -- the structured JSON output makes it straightforward to inject jurisdiction-specific verbiage into the claimant communication field.

**If they push back:** "The structured output format means compliance is a template problem, not an engineering problem. Adding Ohio-specific denial language is a prompt update, not a code change."

---

### Q4: "What is the ROI of this system vs. human claims adjusters?"

**Model Answer:** Three layers of ROI. Processing cost drops from roughly $150 per claim in human labor to under $1 in API costs. Fraud detection improves because the system checks every indicator every time without caseload fatigue -- our TC-005 test case catches an $87,000 staged accident. And compliance risk drops because audit trails are generated automatically, not reconstructed after the fact.

**If they push back:** "Even if you only count fraud prevention, catching one staged accident per month pays for the entire system's annual API costs many times over."

---

### Q5: "How does this handle the 30-day claim decision requirement?"

**Model Answer:** The pipeline processes a claim end-to-end in under 30 seconds, so the 30-day window is never at risk from processing time. More importantly, the Senior Reviewer's compliance checklist explicitly tracks the "within 30 days" flag and generates claimant notification letters with proper timelines. If a claim is sent to investigation, the system generates a documented extension notice, which is how human adjusters handle it too.

**If they push back:** "The bottleneck for the 30-day rule was always human caseload, not process design. Removing that bottleneck makes the deadline trivial to meet."

---

### Q6: "If a claimant gets an attorney, how does the system change?"

**Model Answer:** Attorney involvement is a routing trigger. The Senior Reviewer would flag any claim with attorney representation for legal review -- that is already in its "referred" decision option with routing to legal. In practice, attorney-represented claims require specific communication protocols, but the underlying coverage analysis, damage assessment, and fraud scoring remain the same. The system produces all the documentation an attorney would request through discovery.

**If they push back:** "Having structured, auditable outputs from every stage actually makes attorney-involved claims easier to handle, because all the documentation is already generated."

---

## System / Technical Questions

### Q7: "What if an agent hallucinates a number? How do you catch errors?"

**Model Answer:** Two safeguards. First, the evaluator scores every agent output against rule-based checks -- field matches, numeric ranges, required flags. If the Assessor estimates $500,000 in damage on a minor fender bender, the rule-based eval catches it. Second, the pipeline is sequential, so downstream agents see upstream outputs and can flag inconsistencies. The Fraud Analyst explicitly checks if damage is inconsistent with the described incident, and the Senior Reviewer cross-validates all pipeline data before deciding.

**If they push back:** "The eval-driven training loop means hallucination patterns get caught and the prompts get refined automatically. It is a self-correcting system."

---

### Q8: "Why not use one big agent instead of a pipeline?"

**Model Answer:** Three reasons. First, a single agent trying to do intake, coverage verification, damage assessment, fraud detection, decision-making, and payment processing would have a prompt so large it would degrade in quality -- large prompts dilute attention. Second, you lose the audit trail -- a regulator cannot ask "who decided coverage was valid?" if one agent made every decision. Third, you cannot improve one capability without risking regression in others. Our training loop can refine the Fraud Analyst's prompt without touching the Assessor's.

**If they push back:** "Monolithic agents fail the same way monolithic software fails -- they become impossible to debug, audit, and improve incrementally."

---

### Q9: "How do you handle a new type of claim the system has never seen?"

**Model Answer:** Each agent is designed to handle unknown scenarios by flagging rather than guessing. The Front Desk will still categorize to the nearest match and note what does not fit. The Claims Officer will flag unusual coverage questions for the Senior Reviewer. The Senior Reviewer has explicit "investigate" and "refer" options for situations that do not fit the standard decision matrix. No agent is forced to make a binary approve/deny decision on something it does not understand.

**If they push back:** "The system's default behavior for uncertainty is to escalate, not to guess. That is the same principle good human adjusters follow."

---

### Q10: "What is the human oversight model? When does a human get involved?"

**Model Answer:** Four trigger points. First, the Fraud Analyst can recommend SIU referral for critical-risk claims -- that goes to human investigators. Second, the Senior Reviewer can route to legal or management for unusual cases. Third, the training loop involves human review of eval scores to decide whether prompt improvements are appropriate. Fourth, any claim the Senior Reviewer marks as "investigate" is explicitly flagged for human follow-up. The system is designed to handle the 80% of claims that are straightforward, and escalate the 20% that need human judgment.

**If they push back:** "Full automation is not the goal. The goal is to let humans focus on the cases that actually need human judgment, instead of spending their time on routine paperwork."

---

### Q11: "How do you train and improve the agents over time?"

**Model Answer:** We built an eval-driven training loop. The evaluator scores each agent's output using both rule-based checks and LLM-as-judge scoring, weighted 40/60. If any agent scores below 90 on a test scenario, the improver rewrites that agent's prompt using the eval feedback. The loop repeats until all agents pass the 85-point threshold or hit the maximum iteration count. This means improvement is targeted, measurable, and does not require manual prompt engineering.

**If they push back:** "It is the same principle as CI/CD for software -- automated testing catches regressions, and the system self-heals when quality drops."

---

## Edge Case Questions

### Q12: "What happens if there is a mass disaster -- 500 claims at once?"

**Model Answer:** Because each claim is processed independently through the pipeline, the system scales horizontally. 500 claims means 500 independent pipeline runs, limited only by API rate limits, not by human caseload. The Front Desk agent would categorize all of them, the weather-event tag would be consistent, and the Fraud Analyst would correctly score them as low-risk because mass weather events match legitimate claim patterns. The bottleneck shifts from processing to payment authorization, which is a finance capacity question, not an AI question.

**If they push back:** "The human bottleneck in a disaster is exactly when you need this system most -- when every adjuster is overwhelmed and claims start falling through the cracks."

---

### Q13: "What if someone tries to game the fraud detection?"

**Model Answer:** The fraud scoring uses multiple independent indicators across four categories -- timing, incident, damage/medical, and behavioral. Gaming the system requires beating all four categories simultaneously. Our TC-005 test shows how the system catches a sophisticated staged accident by correlating surname matches, damage-injury mismatches, uninsured other party, and medical billing patterns. A fraudster would need to know the exact scoring rubric and engineer a claim that avoids every indicator, which is significantly harder than fooling a single human adjuster who might miss one or two signals under time pressure.

**If they push back:** "The system checks 20+ indicators on every claim, every time. A human adjuster under caseload pressure might check 5-6. The math favors the system."

---

### Q14: "How does the Finance agent know it is not processing a fraudulent approval?"

**Model Answer:** The Finance agent has a pre-payment validation checklist that requires Senior Reviewer approval, verified amounts within policy limits, correct deductible application, and confirmation that no SIU hold or investigation is pending. It cannot process payment on a claim that is under investigation or referred to SIU. The separation between who decides (Senior Reviewer) and who pays (Finance) is the same internal control that banks use -- the person who approves a loan is not the same person who wires the money.

**If they push back:** "If the Senior Reviewer is compromised, that is a prompt integrity issue we address through the eval loop. But the architectural separation means a single compromised agent cannot both approve and pay."

---

### Q15: "What about claims with partial information -- the claimant does not have all the details?"

**Model Answer:** The Front Desk agent is explicitly designed for this. It checks all required FNOL fields and lists anything missing, but it never blocks the claim from entering the pipeline. Missing information gets flagged at every stage -- the Claims Officer notes it, the Assessor accounts for it in damage ranges, and the Senior Reviewer can choose to investigate rather than deny. Incomplete claims are common in real insurance, and the system handles them the same way a good human intake specialist would -- take what you have, flag what you need, and keep the process moving.

**If they push back:** "Blocking claims for missing info is the number one source of customer complaints in insurance. Our system keeps the process moving and follows up on gaps, just like a good adjuster would."

---

### Q16: "What if two agents disagree -- the Assessor says low damage but the claimant insists it is high?"

**Model Answer:** The Senior Reviewer is specifically designed to resolve conflicts between pipeline stages. It reviews all outputs, can override lower-stage recommendations with documented rationale, and has the "investigate" option to request more information -- such as an independent appraisal. The claimant's assertion does not override the Assessor's estimate, but the Reviewer can order a supplemental inspection if the gap is significant. This mirrors the real-world process where disputed estimates go to an independent appraiser.

**If they push back:** "Disagreements are expected in claims processing. The system handles them the same way a well-run claims department does -- escalation with documentation."

---

## Secret Addition Prep

### Q17: "Given the [X] context we revealed today, how does your system adapt?"

**Model Answer (Adaptable Template):** Our architecture is designed around separation of concerns, which means adapting to new requirements is a prompt-level change, not a code change. Each agent has a focused scope, so adding [X] capability means updating only the relevant agent's instructions. The pipeline structure stays the same, the eval loop validates the new behavior, and every other agent continues to function without modification. This is the advantage of multi-agent over monolithic -- you can evolve one piece without destabilizing the whole system.

**If they push back:** "We can demonstrate this by modifying a single agent prompt and re-running the eval loop. The change is isolated, testable, and does not require redeployment of the entire system."

---

### Q18: "How would you add [new regulation/requirement] to this pipeline?"

**Model Answer:** New regulations typically affect one or two stages of the pipeline. A new disclosure requirement would update the Senior Reviewer's compliance checklist and output template. A new fraud reporting mandate would update the Fraud Analyst's escalation rules. Because each agent has a structured JSON output, adding a new required field is a prompt change plus an eval rule addition. The training loop then validates that the new requirement is consistently met across all test scenarios.

**If they push back:** "Adding a regulation is literally adding a checklist item to the right agent and a validation rule to the evaluator. We can do it in minutes and prove compliance through the eval loop."

---

### Q19: "What if the secret addition requires a 7th agent?"

**Model Answer:** The pipeline architecture supports adding agents because each stage is independent -- it reads the upstream JSON and produces its own. Adding a 7th agent means defining its role, input/output schema, and eval criteria, then inserting it at the appropriate point in the pipeline. The runner, evaluator, and improver all work with any number of agents. We chose 6 because they map to real insurance roles, but the system is not hardcoded to that number.

**If they push back:** "Our loop.py processes agents in sequence from a config. Adding one is a config change and a new prompt file, not an architecture change."

---

### Q20: "How would you handle a sudden change in claims volume or complexity?"

**Model Answer:** Volume scaling is inherent -- each claim is independent, so you scale by running more pipeline instances in parallel. Complexity scaling works through the training loop -- if new test cases reveal agent weaknesses, the evaluator catches them and the improver refines the prompts. The threshold system means we can tighten quality requirements (raise the pass score from 85 to 95) without changing any code, just configuration.

**If they push back:** "The eval-driven loop is our complexity scaling mechanism. When the world gets harder, the system adapts by measuring failures and fixing prompts."

---

## Rapid-Fire Technical Questions

### Q21: "What models are you using?"

**Answer:** Claude (Anthropic) for all agents. The pipeline uses the same model for consistency, but the architecture is model-agnostic -- each agent is a prompt file, so swapping the underlying model is a config change.

---

### Q22: "What is the latency end-to-end?"

**Answer:** Under 30 seconds for a full 6-agent pipeline run. Each agent call is 2-5 seconds. This compares to 5-15 business days for human processing.

---

### Q23: "How much does it cost per claim?"

**Answer:** Under $1 in API costs for a full pipeline run. Compare to approximately $150 in human processing labor per claim. Even at high volume, the API costs are a fraction of one human adjuster's salary.

---

### Q24: "What happens if the API goes down?"

**Answer:** Claims queue until the API is available. Unlike human adjusters, the system does not lose context or forget where it left off. The 30-day regulatory window provides ample buffer for temporary outages. For production, you would add a queue (SQS, Redis) and retry logic.

---

### Q25: "How do you prevent prompt injection from claim descriptions?"

**Answer:** The claim data is passed as structured input, not concatenated into the prompt. Each agent's system prompt is separate from the user data. The structured JSON output format also acts as a natural guard -- if an agent starts producing unexpected output, the eval catches it.
