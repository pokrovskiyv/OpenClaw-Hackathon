# TASK-16: ClawdTalk Voice Channel
> Status: TODO → Goal: configure ClawdTalk, pre-auth flow, escalation triggers, Telegram channel

## Context

Section 8 defines the voice channel architecture. ClawdTalk replaces the human operator on the first line: receives calls, verifies identity, collects incident data, passes structured claim to the 6-agent pipeline.

**Architecture:**
```
Client calls → ClawdTalk / Telnyx (STT/TTS) → WebSocket client
→ OpenClaw Gateway → Main Voice Orchestrator
→ Pre-auth (Caller ID + PIN + policy check)
→ 6-agent pipeline → Voice summary to client
```

**Pre-authentication (3 steps):**
1. Caller ID — identify client by phone number
2. PIN — client states PIN set during policy registration
3. Policy check — confirm policy is active
Any failure → transfer to live operator.

**Escalation triggers (8 types):**
| Trigger | Bot Action |
|---------|-----------|
| Client requests operator | Immediate transfer |
| Injuries present | Transfer with collected data |
| Identity unverified | Transfer |
| Policy not found/expired | Status message, transfer |
| Complex case | Transfer with "attention needed" flag |
| 3+ failed comprehension attempts | Transfer with apology |
| Stress or aggression | Empathetic transfer |

**Key principle:** Client ALWAYS has the right to a live operator — no explanations, no waiting, no re-identification.

**Operational improvements:**
| Parameter | Before | After |
|-----------|--------|-------|
| Intake time | 15-25 min | 3-5 min |
| Availability | 8:00-17:00 | 24/7 |
| Input errors | Frequent | Minimal |
| Queue | Yes | No (bot in parallel) |

**Telegram channel (Section 8.6):** Text channel producing same input JSON as voice → feeds into pipeline. Post-MVP implementation.

## Current State

- Voice agent prompt exists at: `src/workspace/skills/oma-claims-pipeline/references/roles/voice.md`
- OpenClaw config (src/openclaw.json) has voice agent defined
- Pre-auth script exists: `src/workspace/skills/oma-claims-pipeline/scripts/preauth_check.py`
- Call integration guide exists: `docs/call-integration.md`
- Test customers exist in: `src/workspace/customers/`
- ClawdTalk client NOT yet installed/configured

## Agent Team

| Agent | subagent_type | Role |
|-------|--------------|------|
| Platform Ops | openclawer | Install ClawdTalk skill, configure gateway, voice routing, escalation triggers, Telegram bot |
| Onboarding | oma-onboarding | Verify OpenClaw installation health, customer data, skill installation |
| Prompt Engineer | prompt-engineer | Review voice.md, ensure customer_message fields are channel-agnostic across all pipeline agents |

## Work Plan

1. **oma-onboarding** (first — health check):
   - Run path_doctor.py to verify OpenClaw installation
   - Verify customer data layout (src/workspace/customers/index.json)
   - Verify oma-claims-pipeline skill is installed with all role references
   - Check admin privileges are set correctly

2. **openclawer** (main work, after health check):
   - Step 1: Install clawdtalk-client skill (setup.sh + scripts/connect.sh start)
   - Step 2: Verify gateway config: chatCompletions.enabled=true, sessions_send in tools allow list
   - Step 3: Configure voice agent routing: incoming call → voice agent → pre-auth → pipeline → summary
   - Step 4: Configure all 8 escalation triggers in voice orchestrator
   - Step 5: Set up Telegram bot channel (already in openclaw.json, needs testing)
   - Step 6: Configure WhatsApp Business templates for async notifications
   - Step 7: Test end-to-end: call → pre-auth → pipeline → voice summary

3. **prompt-engineer** (parallel, if needed):
   - Review voice.md for completeness
   - Verify all 6 pipeline agent prompts include customer_message with voice_text and chat_text
   - Ensure messages are channel-agnostic

## Key Files

- `src/workspace/skills/oma-claims-pipeline/references/roles/voice.md` — voice agent prompt
- `src/workspace/skills/oma-claims-pipeline/scripts/preauth_check.py` — pre-auth script
- `src/workspace/skills/oma-claims-pipeline/references/voice-integration.md` — voice integration blueprint
- `src/openclaw.json` — gateway and channel configuration
- `docs/call-integration.md` — 11-section integration guide
- `src/workspace/customers/` — test customers
- `docs/business-analysis.md` — Section 8 (lines 837-896)

## Acceptance Criteria

- [ ] ClawdTalk client installed (scripts/connect.sh status shows connected)
- [ ] Gateway config verified: chatCompletions enabled, sessions_send allowed
- [ ] Pre-auth flow configured: Caller ID → PIN → policy check
- [ ] Pre-auth succeeds for test customer (policy OMA-2026-44551)
- [ ] All 8 escalation triggers configured
- [ ] Client can always request live operator (immediate transfer)
- [ ] Telegram bot channel responds to test messages
- [ ] Voice call flow: greeting → safety check → pre-auth → data collection → pipeline → summary
- [ ] No channel-specific markup in customer_message fields

## Verification

```bash
# Verify ClawdTalk connection
cd /path/to/openclaw && scripts/connect.sh status
# Verify gateway config
python3 -c "import json; c=json.load(open('src/openclaw.json')); print('chatCompletions:', c.get('chatCompletions'))"
# Test pre-auth
python3 src/workspace/skills/oma-claims-pipeline/scripts/preauth_check.py --customer tg_200001
```

## Constraints

- Voice channel is a separate layer — does NOT modify pipeline logic
- Pre-auth failure → immediate transfer to human (no retry loops)
- Client always has right to live operator at any point
- Do NOT modify runner.py, loop.py, evaluator.py, improver.py
