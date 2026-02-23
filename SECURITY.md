# Security

Threat model, sensitive data handling rules, and known risks for this workspace.

---

## Sensitive Data

### What's Sensitive Here
| Data | Sensitivity | Location |
|---|---|---|
| `ANTHROPIC_API_KEY` | High — billed per token | `.env` (never committed) |
| GitHub PAT | High — repo write access | Used temporarily in git remote URL |
| Uploaded bid documents | Medium — client/project IP | `uploads/` (local only, gitignored) |
| Saved sessions | Medium — project details | `sessions/` (local only, gitignored) |
| Generated Excel BOMs | Medium — estimating IP | `output/` (local only, gitignored) |
| Stock screener output | Low — based on public data | `output/` |

### Rules
1. **Never commit `.env`.** It is in `.gitignore`. Verify before every push: `git status` should not show `.env`.
2. **Never put API keys in source code.** All secrets come from environment variables via `python-dotenv`.
3. **Never embed a GitHub PAT in a committed file.** If you need to update the remote URL with a token, do it temporarily in the terminal and never stage that change.
4. **Client documents stay local.** The `uploads/`, `output/`, and `sessions/` directories are gitignored. Do not push client bid packages to GitHub.

---

## API Key Management

### Anthropic API Key
- Stored in: `electrical-estimator/.env` → `ANTHROPIC_API_KEY`
- Loaded by: `python-dotenv` in `config/settings.py`
- Rotation: Rotate immediately if accidentally exposed. Revoke at [console.anthropic.com](https://console.anthropic.com).
- Scope: This key has billing implications. A single large extraction run can cost $1–5 depending on document size.

### GitHub Personal Access Token (PAT)
- Used for: `git push` to `https://github.com/Hfrad23/electrical-estimator`
- Current status: Expired as of 2026-02-22. Needs renewal.
- Rotation: Generate at [github.com/settings/tokens](https://github.com/settings/tokens). Classic token, `repo` + `workflow` scopes.
- Do NOT store in any file. Use it inline in the remote URL temporarily, then remove.

---

## Input Handling

### Uploaded Files (electrical-estimator)
- Files are read locally and passed to the Anthropic API as text/base64.
- No file content is stored beyond the local `uploads/` directory and the `.cache/` hash.
- **Risk:** Maliciously crafted PDFs could exploit PyMuPDF vulnerabilities. Acceptable risk for a single-user local tool.
- **Mitigation if sharing:** Add file extension allowlist validation (already enforced by the UI file picker).

### AI Responses
- All AI responses are parsed and validated through Pydantic models before use.
- The system prompt instructs the model to return only JSON. Responses that fail Pydantic validation are logged and discarded.
- **Risk:** Prompt injection via document content. A malicious document could contain instructions that alter AI behavior.
- **Mitigation:** The base system prompt establishes a strong extraction-only persona. Review unexpected AI outputs.

---

## Code Execution

Neither project executes user-provided code or shell commands. There is no `eval()`, `exec()`, or `subprocess` call driven by user input.

The DXF parser uses `ezdxf` to parse files. DXF parsing is local and does not execute embedded scripts.

---

## Data at Rest

| Directory | Gitignored | Encrypted | Notes |
|---|---|---|---|
| `.cache/` | Yes | No | AI response cache — contains extracted project data |
| `uploads/` | Yes | No | Original client documents |
| `output/` | Yes | No | Generated BOM Excel files |
| `sessions/` | Yes | No | JSON session snapshots |
| `data/` (stock screener) | Partially | No | `raw_data.pkl` is gitignored |

**Recommendation:** If this tool handles sensitive client data, consider encrypting the `uploads/` and `sessions/` directories at the OS level (FileVault is enabled on macOS by default — verify it's on).

---

## Known Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| API key exposed in git commit | Low | High | `.gitignore` covers `.env`; review before push |
| Client documents accidentally committed | Low | High | All data dirs gitignored; double-check `git status` |
| AI extraction cost overrun | Medium | Medium | Token budgets set per call in `settings.py` |
| yfinance data breach | Very Low | Low | Public data only; no credentials involved |
| Stale cache returning wrong data after prompt change | Medium | Low | Clear `.cache/` after prompt updates |
