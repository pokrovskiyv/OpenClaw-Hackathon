[Skip to main content](https://docs.openclaw.ai/tools/clawhub#content-area)

[OpenClaw home page![light logo](https://mintcdn.com/clawdhub/4rYvG-uuZrMK_URE/assets/pixel-lobster.svg?fit=max&auto=format&n=4rYvG-uuZrMK_URE&q=85&s=da2032e9eac3b5d9bfe7eb96ca6a8a26)![dark logo](https://mintcdn.com/clawdhub/4rYvG-uuZrMK_URE/assets/pixel-lobster.svg?fit=max&auto=format&n=4rYvG-uuZrMK_URE&q=85&s=da2032e9eac3b5d9bfe7eb96ca6a8a26)](https://docs.openclaw.ai/)

![US](https://d3gk2c5xim1je2.cloudfront.net/flags/US.svg)

English

Search...

Ctrl K

Search...

Navigation

Skills

ClawHub

[Get started](https://docs.openclaw.ai/) [Install](https://docs.openclaw.ai/install) [Channels](https://docs.openclaw.ai/channels) [Agents](https://docs.openclaw.ai/concepts/architecture) [Tools](https://docs.openclaw.ai/tools) [Models](https://docs.openclaw.ai/providers) [Platforms](https://docs.openclaw.ai/platforms) [Gateway & Ops](https://docs.openclaw.ai/gateway) [Reference](https://docs.openclaw.ai/cli) [Help](https://docs.openclaw.ai/help)

On this page

- [ClawHub](https://docs.openclaw.ai/tools/clawhub#clawhub)
- [What ClawHub is](https://docs.openclaw.ai/tools/clawhub#what-clawhub-is)
- [How it works](https://docs.openclaw.ai/tools/clawhub#how-it-works)
- [What you can do](https://docs.openclaw.ai/tools/clawhub#what-you-can-do)
- [Who this is for (beginner-friendly)](https://docs.openclaw.ai/tools/clawhub#who-this-is-for-beginner-friendly)
- [Quick start (non-technical)](https://docs.openclaw.ai/tools/clawhub#quick-start-non-technical)
- [Install the CLI](https://docs.openclaw.ai/tools/clawhub#install-the-cli)
- [How it fits into OpenClaw](https://docs.openclaw.ai/tools/clawhub#how-it-fits-into-openclaw)
- [Skill system overview](https://docs.openclaw.ai/tools/clawhub#skill-system-overview)
- [What the service provides (features)](https://docs.openclaw.ai/tools/clawhub#what-the-service-provides-features)
- [Security and moderation](https://docs.openclaw.ai/tools/clawhub#security-and-moderation)
- [CLI commands and parameters](https://docs.openclaw.ai/tools/clawhub#cli-commands-and-parameters)
- [Common workflows for agents](https://docs.openclaw.ai/tools/clawhub#common-workflows-for-agents)
- [Search for skills](https://docs.openclaw.ai/tools/clawhub#search-for-skills)
- [Download new skills](https://docs.openclaw.ai/tools/clawhub#download-new-skills)
- [Update installed skills](https://docs.openclaw.ai/tools/clawhub#update-installed-skills)
- [Back up your skills (publish or sync)](https://docs.openclaw.ai/tools/clawhub#back-up-your-skills-publish-or-sync)
- [Advanced details (technical)](https://docs.openclaw.ai/tools/clawhub#advanced-details-technical)
- [Versioning and tags](https://docs.openclaw.ai/tools/clawhub#versioning-and-tags)
- [Local changes vs registry versions](https://docs.openclaw.ai/tools/clawhub#local-changes-vs-registry-versions)
- [Sync scanning and fallback roots](https://docs.openclaw.ai/tools/clawhub#sync-scanning-and-fallback-roots)
- [Storage and lockfile](https://docs.openclaw.ai/tools/clawhub#storage-and-lockfile)
- [Telemetry (install counts)](https://docs.openclaw.ai/tools/clawhub#telemetry-install-counts)
- [Environment variables](https://docs.openclaw.ai/tools/clawhub#environment-variables)

# [​](https://docs.openclaw.ai/tools/clawhub\#clawhub)  ClawHub

ClawHub is the **public skill registry for OpenClaw**. It is a free service: all skills are public, open, and visible to everyone for sharing and reuse. A skill is just a folder with a `SKILL.md` file (plus supporting text files). You can browse skills in the web app or use the CLI to search, install, update, and publish skills.Site: [clawhub.ai](https://clawhub.ai/)

## [​](https://docs.openclaw.ai/tools/clawhub\#what-clawhub-is)  What ClawHub is

- A public registry for OpenClaw skills.
- A versioned store of skill bundles and metadata.
- A discovery surface for search, tags, and usage signals.

## [​](https://docs.openclaw.ai/tools/clawhub\#how-it-works)  How it works

1. A user publishes a skill bundle (files + metadata).
2. ClawHub stores the bundle, parses metadata, and assigns a version.
3. The registry indexes the skill for search and discovery.
4. Users browse, download, and install skills in OpenClaw.

## [​](https://docs.openclaw.ai/tools/clawhub\#what-you-can-do)  What you can do

- Publish new skills and new versions of existing skills.
- Discover skills by name, tags, or search.
- Download skill bundles and inspect their files.
- Report skills that are abusive or unsafe.
- If you are a moderator, hide, unhide, delete, or ban.

## [​](https://docs.openclaw.ai/tools/clawhub\#who-this-is-for-beginner-friendly)  Who this is for (beginner-friendly)

If you want to add new capabilities to your OpenClaw agent, ClawHub is the easiest way to find and install skills. You do not need to know how the backend works. You can:

- Search for skills by plain language.
- Install a skill into your workspace.
- Update skills later with one command.
- Back up your own skills by publishing them.

## [​](https://docs.openclaw.ai/tools/clawhub\#quick-start-non-technical)  Quick start (non-technical)

1. Install the CLI (see next section).
2. Search for something you need:
   - `clawhub search "calendar"`
3. Install a skill:
   - `clawhub install <skill-slug>`
4. Start a new OpenClaw session so it picks up the new skill.

## [​](https://docs.openclaw.ai/tools/clawhub\#install-the-cli)  Install the CLI

Pick one:

Copy

```
npm i -g clawhub
```

Copy

```
pnpm add -g clawhub
```

## [​](https://docs.openclaw.ai/tools/clawhub\#how-it-fits-into-openclaw)  How it fits into OpenClaw

By default, the CLI installs skills into `./skills` under your current working directory. If a OpenClaw workspace is configured, `clawhub` falls back to that workspace unless you override `--workdir` (or `CLAWHUB_WORKDIR`). OpenClaw loads workspace skills from `<workspace>/skills` and will pick them up in the **next** session. If you already use `~/.openclaw/skills` or bundled skills, workspace skills take precedence.For more detail on how skills are loaded, shared, and gated, see
[Skills](https://docs.openclaw.ai/tools/skills).

## [​](https://docs.openclaw.ai/tools/clawhub\#skill-system-overview)  Skill system overview

A skill is a versioned bundle of files that teaches OpenClaw how to perform a
specific task. Each publish creates a new version, and the registry keeps a
history of versions so users can audit changes.A typical skill includes:

- A `SKILL.md` file with the primary description and usage.
- Optional configs, scripts, or supporting files used by the skill.
- Metadata such as tags, summary, and install requirements.

ClawHub uses metadata to power discovery and safely expose skill capabilities.
The registry also tracks usage signals (such as stars and downloads) to improve
ranking and visibility.

## [​](https://docs.openclaw.ai/tools/clawhub\#what-the-service-provides-features)  What the service provides (features)

- **Public browsing** of skills and their `SKILL.md` content.
- **Search** powered by embeddings (vector search), not just keywords.
- **Versioning** with semver, changelogs, and tags (including `latest`).
- **Downloads** as a zip per version.
- **Stars and comments** for community feedback.
- **Moderation** hooks for approvals and audits.
- **CLI-friendly API** for automation and scripting.

## [​](https://docs.openclaw.ai/tools/clawhub\#security-and-moderation)  Security and moderation

ClawHub is open by default. Anyone can upload skills, but a GitHub account must
be at least one week old to publish. This helps slow down abuse without blocking
legitimate contributors.Reporting and moderation:

- Any signed in user can report a skill.
- Report reasons are required and recorded.
- Each user can have up to 20 active reports at a time.
- Skills with more than 3 unique reports are auto hidden by default.
- Moderators can view hidden skills, unhide them, delete them, or ban users.
- Abusing the report feature can result in account bans.

Interested in becoming a moderator? Ask in the OpenClaw Discord and contact a
moderator or maintainer.

## [​](https://docs.openclaw.ai/tools/clawhub\#cli-commands-and-parameters)  CLI commands and parameters

Global options (apply to all commands):

- `--workdir <dir>`: Working directory (default: current dir; falls back to OpenClaw workspace).
- `--dir <dir>`: Skills directory, relative to workdir (default: `skills`).
- `--site <url>`: Site base URL (browser login).
- `--registry <url>`: Registry API base URL.
- `--no-input`: Disable prompts (non-interactive).
- `-V, --cli-version`: Print CLI version.

Auth:

- `clawhub login` (browser flow) or `clawhub login --token <token>`
- `clawhub logout`
- `clawhub whoami`

Options:

- `--token <token>`: Paste an API token.
- `--label <label>`: Label stored for browser login tokens (default: `CLI token`).
- `--no-browser`: Do not open a browser (requires `--token`).

Search:

- `clawhub search "query"`
- `--limit <n>`: Max results.

Install:

- `clawhub install <slug>`
- `--version <version>`: Install a specific version.
- `--force`: Overwrite if the folder already exists.

Update:

- `clawhub update <slug>`
- `clawhub update --all`
- `--version <version>`: Update to a specific version (single slug only).
- `--force`: Overwrite when local files do not match any published version.

List:

- `clawhub list` (reads `.clawhub/lock.json`)

Publish:

- `clawhub publish <path>`
- `--slug <slug>`: Skill slug.
- `--name <name>`: Display name.
- `--version <version>`: Semver version.
- `--changelog <text>`: Changelog text (can be empty).
- `--tags <tags>`: Comma-separated tags (default: `latest`).

Delete/undelete (owner/admin only):

- `clawhub delete <slug> --yes`
- `clawhub undelete <slug> --yes`

Sync (scan local skills + publish new/updated):

- `clawhub sync`
- `--root <dir...>`: Extra scan roots.
- `--all`: Upload everything without prompts.
- `--dry-run`: Show what would be uploaded.
- `--bump <type>`: `patch|minor|major` for updates (default: `patch`).
- `--changelog <text>`: Changelog for non-interactive updates.
- `--tags <tags>`: Comma-separated tags (default: `latest`).
- `--concurrency <n>`: Registry checks (default: 4).

## [​](https://docs.openclaw.ai/tools/clawhub\#common-workflows-for-agents)  Common workflows for agents

### [​](https://docs.openclaw.ai/tools/clawhub\#search-for-skills)  Search for skills

Copy

```
clawhub search "postgres backups"
```

### [​](https://docs.openclaw.ai/tools/clawhub\#download-new-skills)  Download new skills

Copy

```
clawhub install my-skill-pack
```

### [​](https://docs.openclaw.ai/tools/clawhub\#update-installed-skills)  Update installed skills

Copy

```
clawhub update --all
```

### [​](https://docs.openclaw.ai/tools/clawhub\#back-up-your-skills-publish-or-sync)  Back up your skills (publish or sync)

For a single skill folder:

Copy

```
clawhub publish ./my-skill --slug my-skill --name "My Skill" --version 1.0.0 --tags latest
```

To scan and back up many skills at once:

Copy

```
clawhub sync --all
```

## [​](https://docs.openclaw.ai/tools/clawhub\#advanced-details-technical)  Advanced details (technical)

### [​](https://docs.openclaw.ai/tools/clawhub\#versioning-and-tags)  Versioning and tags

- Each publish creates a new **semver**`SkillVersion`.
- Tags (like `latest`) point to a version; moving tags lets you roll back.
- Changelogs are attached per version and can be empty when syncing or publishing updates.

### [​](https://docs.openclaw.ai/tools/clawhub\#local-changes-vs-registry-versions)  Local changes vs registry versions

Updates compare the local skill contents to registry versions using a content hash. If local files do not match any published version, the CLI asks before overwriting (or requires `--force` in non-interactive runs).

### [​](https://docs.openclaw.ai/tools/clawhub\#sync-scanning-and-fallback-roots)  Sync scanning and fallback roots

`clawhub sync` scans your current workdir first. If no skills are found, it falls back to known legacy locations (for example `~/openclaw/skills` and `~/.openclaw/skills`). This is designed to find older skill installs without extra flags.

### [​](https://docs.openclaw.ai/tools/clawhub\#storage-and-lockfile)  Storage and lockfile

- Installed skills are recorded in `.clawhub/lock.json` under your workdir.
- Auth tokens are stored in the ClawHub CLI config file (override via `CLAWHUB_CONFIG_PATH`).

### [​](https://docs.openclaw.ai/tools/clawhub\#telemetry-install-counts)  Telemetry (install counts)

When you run `clawhub sync` while logged in, the CLI sends a minimal snapshot to compute install counts. You can disable this entirely:

Copy

```
export CLAWHUB_DISABLE_TELEMETRY=1
```

## [​](https://docs.openclaw.ai/tools/clawhub\#environment-variables)  Environment variables

- `CLAWHUB_SITE`: Override the site URL.
- `CLAWHUB_REGISTRY`: Override the registry API URL.
- `CLAWHUB_CONFIG_PATH`: Override where the CLI stores the token/config.
- `CLAWHUB_WORKDIR`: Override the default workdir.
- `CLAWHUB_DISABLE_TELEMETRY=1`: Disable telemetry on `sync`.

[Skills Config](https://docs.openclaw.ai/tools/skills-config) [Plugins](https://docs.openclaw.ai/tools/plugin)

Ctrl+I

Assistant

Responses are generated using AI and may contain mistakes.