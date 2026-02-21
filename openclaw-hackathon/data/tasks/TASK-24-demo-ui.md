# TASK-24: Demo UI (Presentation Layer)
> Status: TODO → Goal: create Supabase tables, build supabase_sync.py, spec Lovable frontend

## Context

Section 19 defines the demo interface — a presentation layer for hackathon judges. The pipeline remains a CLI app; the UI only reads and displays results. ONE-WAY data flow only.

**Stack:**
| Component | Technology | Purpose |
|-----------|-----------|---------|
| Frontend | Lovable (React) | Pipeline and claims visualization |
| Backend | Supabase (PostgreSQL + auto-REST) | Data storage for UI |
| Integration | Python adapter (lib/supabase_sync.py) | One-way sync: pipeline → Supabase |

**Architecture:**
```
[Python Pipeline] → save_run_log() → [JSON on disk] (system of record)
      └── sync_to_supabase() → [Supabase PostgreSQL] ← [Lovable UI]
```

**Two tables:**

```sql
-- Table 1: claims
create table claims (
  id text primary key,
  scenario_name text,
  status text not null default 'pending',
  category text, severity text, priority text,
  fast_track boolean default false,
  claimant_name text, policy_number text,
  incident_date date, incident_type text,
  coverage_valid text, fraud_score integer, fraud_risk_level text,
  decision text, approved_amount numeric, payment_authorized boolean,
  iteration integer, pipeline_duration_seconds numeric,
  created_at timestamptz default now(), completed_at timestamptz,
  input_data jsonb, policy_data jsonb, pipeline_state jsonb
);

-- Table 2: agent_logs
create table agent_logs (
  id bigint generated always as identity primary key,
  claim_id text references claims(id),
  agent_name text not null, agent_order integer not null,
  output jsonb not null, elapsed_seconds numeric, success boolean,
  confidence_score integer, escalation_triggered boolean default false,
  input_quality text, routing text,
  created_at timestamptz default now()
);
create index idx_agent_logs_claim on agent_logs(claim_id, agent_order);
```

**Three screens:**

**Screen 1: Pipeline Flow** (highest priority for demo)
- Horizontal 7-agent cards with connections
- Confidence Score color: green (80+), yellow (60-79), red (<60)
- `_redacted: true` → visual blur on Assessor ← Claims Officer connection
- `action: "skip"` → grey card with "Skipped" label
- Escalation → warning icon
- Full output on click

**Screen 2: Claims Dashboard**
- Sortable table of all claims
- Color coding: severity, decision, fraud_score
- Click row → opens Pipeline Flow

**Screen 3: Role Switcher**
- 4 roles mirroring Secret Addition stakeholders:
  | Role | Stakeholder | Sees | Hidden |
  |------|------------|------|--------|
  | CX / Front Desk | Marcus Chen | Claim status, FNOL | Fraud details, financial data |
  | Fraud Analyst | Priya Okonkwo | Everything | — |
  | Senior Reviewer | Rachel Thornton | Compliance, decisions | — |
  | Claims Director | Daniel Kowalski | SLA timing, escalations | — |
- **Demo moment:** switching to CX blurs fraud_score and financial fields

**Python adapter** (lib/supabase_sync.py, ~40 lines):
- Parse pipeline_state from JSON log
- Map agent outputs to table columns
- Upsert (idempotent: re-sync doesn't duplicate)
- On connection error → log warning, pipeline unaffected

## Current State

- lib/supabase_sync.py does NOT exist (confirmed)
- Supabase project needs to be created
- Lovable frontend not started
- Pipeline output structure known from existing logs

## Agent Team

| Agent | subagent_type | Role |
|-------|--------------|------|
| General | general-purpose | Create Supabase tables, build lib/supabase_sync.py, integrate with pipeline |
| Explorer | Explore | Read pipeline output structure from existing logs |

## Work Plan

1. **Explore** (quick research):
   - Read a sample logs/iter_000/TC-001/pipeline.json
   - Document exact JSON structure of pipeline_state
   - Map fields: pipeline_state → claims table columns
   - Map fields: per-agent outputs → agent_logs table columns

2. **general-purpose** (main implementation):
   - Step 1: Create Supabase project (manual step — document instructions)
   - Step 2: Run SQL schema (the 2 tables above)
   - Step 3: Build `lib/supabase_sync.py` (~40 lines):
     ```python
     # Requirements: pip install supabase
     # Env: SUPABASE_URL, SUPABASE_KEY
     # Functions:
     #   sync_to_supabase(scenario_id, pipeline_output, iteration=0)
     #   - Parse pipeline_state
     #   - Upsert into claims (flat fields + full jsonb)
     #   - Insert agent_logs (one per agent, ordered)
     #   - Idempotent: use scenario_id as primary key
     #   - On error: log warning, don't crash pipeline
     ```
   - Step 4: Add `sync_to_supabase()` call after `save_run_log()` in runner.py
   - Step 5: Add `supabase` to requirements.txt
   - Step 6: Test: `python3 loop.py --run-once --scenario TC-001` → check Supabase dashboard

3. **Lovable frontend** (separate — produce spec document):
   - Complete screen specs with Supabase auto-REST API queries
   - Pipeline Flow: `GET /agent_logs?claim_id=eq.TC-001&order=agent_order`
   - Claims Dashboard: `GET /claims?order=created_at.desc`
   - Role Switcher: client-side field visibility rules
   - Color coding specs for confidence, severity, decision

## Key Files

- `lib/supabase_sync.py` — NEW file to create (~40 lines)
- `runner.py` — add sync_to_supabase() call after save_run_log()
- `requirements.txt` — add supabase dependency
- `logs/iter_000/TC-001/pipeline.json` — sample output for field mapping
- `docs/business-analysis.md` — Section 19 (lines 1361-1553)

## Acceptance Criteria

- [ ] lib/supabase_sync.py created and functional
- [ ] Two Supabase tables created (claims + agent_logs)
- [ ] `python3 loop.py --run-once --scenario TC-001` populates both tables
- [ ] Sync is idempotent (re-running doesn't duplicate)
- [ ] Pipeline doesn't crash if Supabase unavailable (warning only)
- [ ] Field mapping covers: category, severity, decision, fraud_score, approved_amount
- [ ] agent_logs has correct agent_order (1-7)
- [ ] confidence_score populated in agent_logs
- [ ] Lovable frontend spec document produced for all 3 screens
- [ ] No regression in benchmark score

## Verification

```bash
cd openclaw-hackathon
# Test sync
python3 loop.py --run-once --scenario TC-001
# Verify claims table has data (via supabase CLI or python)
python3 -c "
from supabase import create_client
import os
s = create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_KEY'])
data = s.table('claims').select('id,decision,approved_amount').execute()
print(data.data)
"
# Verify benchmark still passes
python3 benchmark.py --no-llm-judge
```

## Constraints

- ONE-WAY data flow only: pipeline → Supabase (never Supabase → pipeline)
- JSON on disk remains system of record
- Do NOT add Edge Functions or TypeScript
- Do NOT launch pipeline from UI
- UI is read-only presentation layer
- Do NOT modify loop.py, evaluator.py, improver.py
