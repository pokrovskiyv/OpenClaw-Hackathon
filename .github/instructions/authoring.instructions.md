```instructions
---
description: "Standard for adding new assets to this repo: skills, instructions, agents. Naming, frontmatter, and discoverability rules."
applyTo: "skills/**/*.md,.github/instructions/*.instructions.md,.github/agents/*.agent.md,agents/*.md"
---

# Authoring: skills / instructions / agents

This instruction defines the standard for adding new assets.

**Language requirement:** all assets MUST be written in English.

## Skills

Skills follow [agentskills.io](https://agentskills.io) specification.

### Location

- Skills: `skills/<skill-name>/SKILL.md`
- References: `skills/<skill-name>/references/*.md`

### MUST

- Folder name and `name` in frontmatter MUST match
- `name`: 1-64 chars, lowercase `a-z0-9-`, no `--`, no leading/trailing `-`
- `description`: 1-1024 chars, include discovery keywords
- Keep `SKILL.md` under 500 lines; move details to `references/`

### MUST NOT

- Do not copy large verbatim chunks from vendor docs
- Do not include project-specific secrets or paths

## Instructions (Copilot-specific)

### Location

- `.github/instructions/<topic>.instructions.md`

### MUST

- Frontmatter with `description` + `applyTo` glob
- Content: norms only (no step-by-step procedures)

## Agents (Copilot-specific)

### Location

- `.github/agents/<role>.agent.md`

### MUST

- Keep short: when to use, what it does, prohibitions, links
- Link to relevant skills/instructions

### MUST NOT

- Do not put step-by-step procedures (procedures belong in skills)

## Links

- Skill creator: `skills/skill-master/SKILL.md`
- Repo-wide rules: `.github/copilot-instructions.md`
```
