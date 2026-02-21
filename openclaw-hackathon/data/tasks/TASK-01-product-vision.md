# TASK-01: Product Vision + Problem Statement + Stakeholders
> Status: DOC → Goal: verify accuracy, enrich with domain-specific detail, validate Secret Addition resolution

## Context

This is the foundational PRD section covering product vision, problem statement, and stakeholder analysis for Ohio Mutual Auto — a regional auto insurance company in Ohio. The section includes the Secret Addition stakeholder conflicts and the Blind Assessment Architecture resolution.

Key areas to verify and enrich:
1. **Product Vision (Section 1)** — 7 AI agents automate claims processing, with Claims Manager as quality control
2. **Problem Statement (Section 2)** — Manual 6-step process with delays, errors, limited hours
3. **Stakeholders (Section 3)** — 5 external + 4 internal stakeholders with conflicting priorities
4. **Secret Addition (Section 3a)** — 4 stakeholder conflicts resolved by Blind Assessment Architecture

The Secret Addition defines 4 internal stakeholders:
- **Daniel Kowalski (COO)**: Speed — wants Assessor to access policy for faster processing ($340/claim, $4M+/year)
- **Rachel Thornton (CCO)**: Compliance — wants separation of assessment and financial data ($4.1M fine risk)
- **Marcus Chen (CX Lead)**: Transparency — wants Front Desk to give status without transfers ($4,200/year per lost customer)
- **Priya Okonkwo (Fraud Lead)**: Fraud detection — wants cross-reference of damage with policy data ($8.3M/year losses)

Conflict matrix:
- Daniel ↔ Rachel: speed vs compliance (Assessor policy access)
- Rachel ↔ Priya: data separation vs full access (fraud detection)
- Marcus ↔ Priya: transparency vs non-disclosure (fraud investigation)

Resolution: **Blind Assessment Architecture** (Section 7.2a) — field-level whitelist in runner.py satisfies all 4 simultaneously.

## Current State

- PRD sections 1-3 are written in Russian
- All stakeholder $ figures are present but need source verification
- Secret Addition conflict resolution is documented but needs validation against actual runner.py code
- English Executive Summary (Appendix A, TASK-25) covers this in English

## Agent Team

| Agent | subagent_type | Role |
|-------|--------------|------|
| Domain Expert | insurance-analyst | Verify all $ figures (fraud losses, bad faith fines, customer churn costs) against industry data. Check Ohio-specific regulatory references. |
| Pipeline Analyst | eval-analyst | Validate that the Secret Addition conflict resolution actually works in the codebase. Check runner.py whitelist, verify Blind Assessment implementation. |

## Work Plan

1. **insurance-analyst**: Research and verify the following claims:
   - $8.3M/year fraud losses (Priya) — is this realistic for a regional Ohio insurer with ~1,000 claims/month?
   - $4.1M fine risk (Rachel) — verify ORC 3901.21 penalties and *Zoppo v. Homestead* precedent
   - $340/claim delay cost (Daniel) — validate against industry data
   - $4,200/year per lost customer (Marcus) — check customer lifetime value for auto insurance
   - ~10% fraud rate in P&C — verify against CAIF/III sources
   - Bad faith punitive damages up to 2x compensatory (ORC 2315.21(D))

2. **eval-analyst**: Verify the Blind Assessment Architecture implementation:
   - Read `runner.py` — find `ASSESSOR_ALLOWED_FROM_CLAIMS_OFFICER` whitelist
   - Confirm Assessor does NOT receive: coverage_limit, deductible, coverage_type, exclusions_triggered, policy_status
   - Confirm Fraud Analyst DOES receive full policy data + blind assessment
   - Check `_redacted: true` marker is added to filtered output
   - Verify Front Desk generates `claim_status_update` field
   - Run TC-001 and TC-002 to confirm Blind Assessment works end-to-end

3. **Document findings**: Produce a findings report with:
   - Verified/corrected $ figures with sources
   - Implementation gaps (if any) between PRD and code
   - Suggested enrichments for the stakeholder section

## Key Files

- `docs/business-analysis.md` — Sections 1-3 (lines 1-102)
- `runner.py` — Blind Assessment whitelist, selective policy feeding
- `agents/front_desk.md` — claim_status_update generation
- `agents/assessor.md` — Blind Assessment compliance
- `agents/fraud_analyst.md` — Estimate-to-Limit cross-reference
- `test_cases/all_scenarios.json` — scenarios testing Blind Assessment

## Acceptance Criteria

- [ ] All 4 stakeholder $ figures verified against industry sources or clearly marked as estimates
- [ ] ORC 3901.21, OAC 3901-1-54, *Zoppo v. Homestead* references confirmed accurate
- [ ] ASSESSOR_ALLOWED_FROM_CLAIMS_OFFICER whitelist in runner.py matches PRD spec
- [ ] Assessor output for TC-001 does NOT contain coverage_limit or deductible
- [ ] Fraud Analyst output for TC-001 DOES contain Estimate-to-Limit calculation
- [ ] Front Desk output includes claim_status_update with customer-friendly language
- [ ] Conflict resolution matrix validated: all 4 stakeholders' needs are met simultaneously

## Verification

```bash
cd openclaw-hackathon
# Run pipeline for standard collision to verify Blind Assessment
python3 loop.py --run-once --scenario TC-001
# Check Assessor output doesn't contain financial fields
python3 -c "import json; d=json.load(open('logs/iter_000/TC-001/pipeline.json')); a=d['pipeline_state']['assessor']; assert 'coverage_limit' not in str(a), 'FAIL: Assessor sees coverage_limit'"
```

## Constraints

- Do NOT modify runner.py Blind Assessment logic — only verify it
- Do NOT modify training loop files (loop.py, evaluator.py, improver.py)
- If $ figures cannot be verified, note them as "estimated" rather than changing
