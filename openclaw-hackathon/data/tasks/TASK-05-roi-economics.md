# TASK-05: ROI and Economics
> Status: DOC → Goal: validate salary data, verify ROI formulas, stress-test scaling table

## Context

Section 5.5 of the PRD provides a detailed economic analysis of the AI pipeline's ROI. This is the primary business case for the hackathon presentation. Key narrative: "Same 6 people handle 2.5x volume without hiring" — not "we replace workers."

Key numbers:
- Average Ohio claims adjuster salary: $52,000/year (BLS)
- Full cost per employee: $72,800/year (1.4x multiplier)
- API cost: ~$0.50/claim (6 Haiku + 1 Sonnet)
- ClawdTalk Pro: $7,000/year
- Distribution: 70% full auto, 20% partial, 10% full human
- Direct savings: $662,700/year (avoided hiring + field visits)
- ROI year 1: ~167% (with $75K implementation cost)
- ROI steady-state: ~860%
- Indirect: +$140K/year prevented fraud losses

Per-stage ROI breakdown (6 stages):
| Stage | Current Cost | AI+HITL Cost | Savings |
|-------|-------------|-------------|---------|
| Front Desk | $72,800 | $23,840 | $48,960 |
| Claims Officer | $72,800 | $31,120 | $41,680 |
| Assessor | $87,800 | $44,900 | $42,900 |
| Fraud Analyst | $72,800 | $22,840 | $49,960 |
| Senior Reviewer | $72,800 | $37,400 | $35,400 |
| Finance | $72,800 | $15,560 | $57,240 |

Scaling table (Section 5.5.6):
| Volume | Manual Staff | AI+HITL Staff | API Cost | Savings |
|--------|-------------|--------------|----------|---------|
| 500/mo | 3 | 1.5 | $3K | $109K |
| 1,000/mo | 6 | 2.2 | $6K | $277K |
| 2,500/mo | 15 | 3.5 | $15K | $837K |
| 5,000/mo | 30 | 5.0 | $30K | $1.8M |

Re-staffing plan: 6 current employees retrained to higher-value roles (CX specialist, coverage QA, field adjuster, SIU investigator, quality lead, auditor).

## Current State

- Section 5.5 is comprehensive with tables and formulas
- BLS salary data needs verification for 2025-2026 Ohio
- API pricing needs check against current Anthropic pricing
- Scaling table assumes linear API cost growth and sublinear HITL growth

## Agent Team

| Agent | subagent_type | Role |
|-------|--------------|------|
| Domain Expert | insurance-analyst | Verify BLS salary data for Ohio, validate industry benchmarks (fraud detection rates, processing times) |
| Pipeline Analyst | eval-analyst | Cross-check API costs against actual pipeline runs, verify processing time claims |

## Work Plan

1. **insurance-analyst**: Verify salary and industry data:
   - BLS median for claims adjusters in Ohio (SOC 13-1031)
   - 1.4x multiplier for full employee cost (Midwest USA standard)
   - $0.50/claim API cost — check against Anthropic Haiku/Sonnet pricing
   - 70/20/10 automation distribution — compare with industry benchmarks
   - Fraud detection rate improvement 60% → 85% — check NICB/CAIF data
   - 15-25 min manual intake time — validate against industry

2. **eval-analyst**: Verify technical claims:
   - Run `python3 loop.py --run-once --scenario TC-001` and measure actual execution time
   - Calculate actual API cost per claim from token usage
   - Verify the 30-second claim from PRD matches reality
   - Check if 36 scenarios × 30 seconds = ~18 min full run is accurate

3. **Document**: Produce findings with corrected numbers if any are off

## Key Files

- `docs/business-analysis.md` — Section 5.5 (lines 383-559)
- `lib/config.py` — model configuration and pricing
- `runner.py` — pipeline execution (timing data)

## Acceptance Criteria

- [ ] BLS salary data verified or corrected with source
- [ ] API cost per claim recalculated with current Anthropic pricing
- [ ] Actual pipeline execution time measured and compared to 30-second claim
- [ ] Scaling table stress-tested for logical consistency
- [ ] ROI formulas independently verified (inputs → outputs)
- [ ] Re-staffing plan validated as realistic

## Constraints

- Do NOT modify code — this is a verification task
- If numbers are off, document the corrected values
