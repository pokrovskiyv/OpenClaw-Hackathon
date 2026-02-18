<!-- CUSTOM:START -->

## 1. Timeouts

- **ALWAYS** specify `timeout` for `execute_command` (e.g., 30000ms)
- Set timeouts for HTTP requests (e.g., `httpx.AsyncClient(timeout=10.0)`)
- Max single wait: 5 minutes; may extend by another 5 min if still running
- Max total duration: 30 minutes

## 2. Git Safety

**FORBIDDEN** (modifies repo/history):

- `git commit`, `push`, `reset`, `rebase`, `merge`, `cherry-pick`, `revert`, `checkout`, `switch`, `pull`, `fetch --prune`, `clean`

**ALLOWED** (read-only):

- `git status`, `diff`, `log`, `show`, `blame`, `grep`

**File deletion**: use `trash` instead of `rm -rf`

## 3. Code Quality

**PROHIBITED**:

- Silent fallbacks (`or "default"`, `get() or fallback`)
- Mock/stub implementations
- Hardcoded credentials or API keys
- Generic error messages
- Bare `except:` clauses

**REQUIRED**:

- Explicit error handling (fail fast)
- Real implementations only
- `TODO`/`FIXME` comments for unimplemented features
- ENV variables for configuration
<!-- CUSTOM:END -->
