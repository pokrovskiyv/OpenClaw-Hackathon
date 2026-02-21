# TASK-14: Post-Pipeline Notification + Payment
> Status: TODO → Goal: configure notification channels, update Finance prompt, add customer_message fields

## Context

Section 7.6 defines the post-pipeline flow: after Finance makes its decision, the system must notify the client and initiate payment (or denial).

**Step 1 — Customer Notification:**
| Channel | Mechanism | Timeline |
|---------|----------|----------|
| Phone (ClawdTalk) | Voice summary immediately after pipeline (if client on line) | Immediate |
| Telegram | Structured message with decision, amount, next steps | 1-5 minutes |
| Letter (denial/investigate) | Formal notification citing policy provision + appeal rights | Per OAC 3901-1-54 |

**Step 2 — Payment Execution:**
- **Auto-approved** (decision=approved, amount < $10K, fraud_score < 21): Finance forms payment order → payment system (out of prototype scope)
- **HITL claims** (investigate/referred/amount > $25K): AI decision = recommendation → human approves/adjusts → execution
- **Payment deadline:** 10 days from decision (OAC 3901-1-54(F))

**Step 3 — Subrogation (if applicable):**
- Finance sets `subrogation.applicable = true` when at-fault party data exists
- Demand includes client's deductible (OAC 3901-1-54(H)(10))
- Filed within 30 days to at-fault insurer
- Blocked when insured's fault >= 51% (ORC 2315.33)

**Prototype limitation:** Finance forms decision and calculation but does NOT execute the transaction. Payment system integration is out of hackathon scope.

## Current State

- Finance agent produces payment decisions but no customer_message fields
- No notification channel configuration exists
- Subrogation output exists in Finance but needs enrichment
- OpenClaw channels (Telegram, WhatsApp) are configured in src/openclaw.json

## Agent Team

| Agent | subagent_type | Role |
|-------|--------------|------|
| Platform Ops | openclawer | Configure notification channels in OpenClaw — Telegram templates, WhatsApp Business messages, post-pipeline routing |
| Prompt Engineer | prompt-engineer | Update finance.md to add customer_message fields (voice_text + chat_text), denial letter content, subrogation demand fields |
| Domain Expert | insurance-analyst | Verify Ohio regulatory requirements for denial notifications, payment timelines, subrogation rules |

## Work Plan

1. **insurance-analyst** (research first):
   - Document Ohio requirements for denial notifications:
     - Must cite specific policy provision (OAC 3901-1-54)
     - Must be in plain language understandable to non-specialist
     - Must include appeal rights and process
   - Verify payment timelines: 10 days from decision (OAC 3901-1-54(F))
   - Verify subrogation: deductible inclusion, 30-day filing, 51% bar
   - Produce compliance checklist for notifications

2. **prompt-engineer** (after research):
   - Add to finance.md output format:
     ```json
     "customer_message": {
       "voice_text": "Your claim has been approved for $X...",
       "chat_text": "**Claim Decision:** Approved\n**Amount:** $X\n**Next Steps:** ...",
       "formal_letter": "Dear [claimant]... [only for denials/investigations]"
     }
     ```
   - Add auto-approval routing logic:
     - decision=approved AND amount < $10K AND fraud_score < 21 → auto-pay
     - Otherwise → HITL queue
   - Add denial letter template (cite policy provision, appeal rights)
   - Add subrogation demand fields: demand_deadline (30 days), demand_amount, target_insurer
   - Ensure customer_message is channel-agnostic (no Telegram/WhatsApp markup)

3. **openclawer** (parallel with prompt-engineer):
   - Read src/openclaw.json for existing channel config
   - Configure notification templates:
     - `claim_approved` — Telegram/WhatsApp template
     - `claim_denied` — Telegram/WhatsApp template
     - `claim_investigating` — Telegram/WhatsApp template
     - `payment_notification` — payment confirmation
   - Configure post-pipeline routing: which channel, timing
   - Handle WhatsApp 24-hour messaging window constraint

4. **Bash**: Verify changes:
   ```bash
   cd openclaw-hackathon
   python3 loop.py --run-once --scenario TC-001
   python3 benchmark.py --no-llm-judge  # No regression
   ```

## Key Files

- `agents/finance.md` — PRIMARY edit target (add customer_message)
- `src/openclaw.json` — notification channel config
- `runner.py` — verify Finance output includes new fields
- `test_cases/all_scenarios.json` — may need assertions for customer_message
- `docs/business-analysis.md` — Section 7.6 (lines 783-811)

## Acceptance Criteria

- [ ] Finance output includes customer_message with voice_text and chat_text
- [ ] Denial notifications cite specific policy provisions
- [ ] Denial notifications include appeal rights
- [ ] Auto-approval criteria: approved + < $10K + fraud_score < 21
- [ ] Subrogation demand includes client's deductible
- [ ] Subrogation demand_deadline = 30 days from payment
- [ ] Subrogation blocked when insured fault >= 51%
- [ ] Notification templates configured for Telegram/WhatsApp
- [ ] customer_message is channel-agnostic (no platform-specific markup)
- [ ] No regression in benchmark score

## Verification

```bash
cd openclaw-hackathon
python3 loop.py --run-once --scenario TC-001  # approved → check customer_message
python3 loop.py --run-once --scenario TC-004  # denied → check denial letter
python3 benchmark.py --no-llm-judge
```

## Constraints

- Finance does NOT execute transactions — only forms decisions and messages
- customer_message text must be understandable to non-specialist
- Do NOT add Telegram/WhatsApp markup to agent prompts — keep channel-agnostic
