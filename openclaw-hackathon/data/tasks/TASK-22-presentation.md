# TASK-22: Hackathon Strategy + Presentation
> Status: TODO → Goal: draft slides, Q&A prep, demo script
> Blocked by: TASK-24 (Demo UI needed for live demo portion)

## Context

Section 15 defines the hackathon presentation strategy. 10 minutes per team: 5 minutes presentation + 5 minutes Q&A.

**Judging criteria:**
| Criterion | Weight | What's Evaluated |
|-----------|--------|-----------------|
| Business Thinking | 50% | Defending each decision from insurance business perspective, domain understanding |
| System Thinking | 50% | End-to-end working system, logical multi-agent design, resilience |

**5-minute presentation structure:**
| Slide | Time | Content | Key Message |
|-------|------|---------|-------------|
| 1. Problem | 0:00-0:30 | Manual 6-step process, delays, errors, 8:00-17:00 | "6 people, 6 handoffs, 3-5 days per claim" |
| 2. Demo | 0:30-1:30 | Live TC-001 run via CLI → JSON output per agent | "30 seconds, 7 agents, full audit trail" |
| 3. Architecture | 1:30-2:30 | Pipeline flow, Claims Manager, self-improving loop | "The system gets better automatically" |
| 4. Business Case | 2:30-3:00 | ROI: "Same 6 people handle 2.5× volume", Ohio compliance | "167% ROI year one, no layoffs" |
| 5. Secret Addition | 3:00-3:30 | Agents reason from principles, not templates | "Add any business rule — system adapts" |
| Wrap-up | 3:30-5:00 | Two competitive advantages + Q&A prep | Manager + Loop — two differentiators, not six |

**Q&A prep:**
- "How do you handle fraud?" → demo TC-005 (staged accident), show fraud_score breakdown
- "What about Ohio regulations?" → cite Section 4 PRD (ORC 3901.21, OAC 3901-1-54)
- "How do you adapt to Secret Addition?" → show improver.py cycle, backup mechanism
- "Is ROI realistic?" → scaling table 5.5.6, conservative framing

**Competitive advantages:**
| Advantage | Why Differentiating |
|-----------|-------------------|
| Claims Manager | 7th agent evaluates the other 6 — built-in QC |
| Self-improving loop | Manager → Improver → updated prompts — closed loop |
| Voice channel | Full client journey 24/7 |
| 36 scenarios + 387 assertions | Automatic benchmark: 40% assertions + 60% LLM judge Opus |
| Human-in-the-loop | AI prepares data, human decides on complex cases |
| Model separation | Haiku for workers, Sonnet for management |

**Key from HACKATHON.md:** "Brilliant reasoning behind an unfinished system beats a polished one you can't explain."

## Current State

- PRD section 15 has full strategy documented
- Demo requires TASK-24 (Demo UI) for visual portion
- CLI demo can work independently (python3 loop.py --run-once)
- No slide deck, presentation notes, or Q&A cards created yet

## Agent Team

| Agent | subagent_type | Role |
|-------|--------------|------|
| Domain Expert | insurance-analyst | Prepare Ohio regulatory talking points, ROI defense, business case backing |
| Writer | general-purpose | Draft slide content, Q&A scripts, demo flow, timing plan |

## Work Plan

1. **insurance-analyst** (research first):
   - Compile concise business talking points:
     - Ohio regulatory compliance summary (OAC 3901-1-54 timelines, bad faith, total loss)
     - ROI defense: 167% year 1, same 6 people handle 2.5× volume
     - Fraud detection uplift: 100% screening vs sample-based (~60% → ~85%)
     - Secret Addition framing: Blind Assessment as elegant resolution of 4 conflicting priorities
   - Produce 1-page Q&A reference card

2. **general-purpose** (after research):
   - Draft 6-slide content (one section per slide from table above)
   - Each slide: 1 headline, 3-5 bullet points, 1 key message
   - Write Q&A scripts for 4 expected questions
   - Create demo flow:
     - Which scenario to run live (TC-001 for speed, TC-005 for fraud)
     - What to point at in the output
     - How to show the Demo UI (TASK-24)
     - How to show Blind Assessment (Role Switcher)
   - Timing plan: allocate seconds per slide, buffer for transitions
   - Create `docs/PRESENTATION.md` with all content
   - Create `docs/QA_PREP.md` with Q&A scripts

3. **Produce deliverables:**
   - `docs/PRESENTATION.md` — slide deck content with notes
   - `docs/QA_PREP.md` — answers to 15+ expected jury questions
   - `docs/DEMO_SCRIPT.md` — step-by-step demo flow with commands

## Key Files

- `docs/PRESENTATION.md` — NEW file to create
- `docs/QA_PREP.md` — NEW file to create
- `docs/DEMO_SCRIPT.md` — NEW file to create
- `docs/business-analysis.md` — Section 15 (lines 1133-1200)
- `HACKATHON.md` — competition rules and judging criteria

## Acceptance Criteria

- [ ] 6-slide presentation outline with content fits in 5 minutes
- [ ] Each slide has one clear message (not overloaded)
- [ ] Business case leads with "Same 6 people handle 2.5× volume" (not "we replace workers")
- [ ] Secret Addition answer demonstrates Blind Assessment Architecture reasoning
- [ ] Demo script shows actual pipeline output (not screenshots)
- [ ] Q&A prep covers: fraud (TC-005), Ohio regulations, Secret Addition, ROI
- [ ] Timing plan adds up to ≤ 5:00 with buffer
- [ ] Demo flow includes both CLI output AND Demo UI (if TASK-24 done)
- [ ] Two differentiators highlighted: Claims Manager + Self-improving Loop

## Verification

```bash
# Verify demo runs in < 30 seconds
cd openclaw-hackathon
time python3 loop.py --run-once --scenario TC-001
# Verify all docs created
ls docs/PRESENTATION.md docs/QA_PREP.md docs/DEMO_SCRIPT.md
```

## Constraints

- Blocked by TASK-24 (Demo UI) for visual demo portion — CLI demo works independently
- Presentation in English (international judges)
- Focus on TWO differentiators, not six (Manager + Loop)
- ROI framing: "capacity expansion" not "job elimination"
- "Brilliant reasoning > polished demo you can't explain"
