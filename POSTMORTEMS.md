# Postmortems

What broke, root cause, fix, and what changed to prevent recurrence.

---

## Postmortem Template

```
## [Date] — [Project] — [Short title]

**Severity:** Low / Medium / High
**Detected:** How was the failure found?
**Duration:** How long was it broken?

### What Happened
[Describe the failure from the user's perspective]

### Root Cause
[The actual technical reason]

### Fix
[What was done to resolve it]

### Prevention
[What changed to prevent this from happening again]
```

---

## [2026-02-22] — electrical-estimator — Pydantic v2 validation failures across all BOM tabs

**Severity:** High
**Detected:** During initial end-to-end testing of the MVP
**Duration:** Initial session

### What Happened
All 10 BOM tabs failed to populate. Pydantic validation errors were raised for nearly every extracted field. The Excel output was empty or incomplete.

### Root Cause
The codebase was initially written with Pydantic v1 patterns (`@validator`, `pre=True`) but `pydantic>=2.0` was installed. Pydantic v2 broke backward compatibility:
- `@validator` was removed in favor of `@field_validator`
- The `mode="before"` syntax changed
- Optional fields with `None` defaults behaved differently
- Enum field coercion no longer happened automatically

Additionally, the AI was returning field values in formats not anticipated by the validators:
- Confidence as lowercase `"confirmed"` when the enum expected `"Confirmed"`
- AWG as an integer (`12`) when the model expected a string (`"12"`)
- Optional float fields returning `"N/A"` strings instead of `None`

### Fix
Rewrote all validators across 15 Pydantic models in `config/bom_schema.py`:
- Migrated from `@validator` to `@field_validator` with `@classmethod`
- Added normalization in each validator: lowercase/capitalize for enums, cast int→str for AWG, return `None` for non-numeric optional floats
- Added `mode="before"` to all pre-validators
- Fixed `Optional[float]` fields to handle string inputs gracefully

### Prevention
- Added this postmortem as a reference for future Pydantic upgrades
- Established the pattern: all field validators must handle both the expected format AND the AI's common variant formats
- `PATTERNS.md` now documents the standard validator pattern
- `TESTING.md` lists Pydantic model tests as Tier 1 priority — these should be the first tests written

---

## [2026-02-22] — electrical-estimator — GitHub push failed (expired PAT)

**Severity:** Low (local work unaffected)
**Detected:** At end of session when attempting to push commit 8291727
**Duration:** Ongoing — not yet resolved

### What Happened
`git push origin main` failed with a 401 authentication error. The personal access token stored in the remote URL had expired.

### Root Cause
GitHub PATs have expiration dates. The token used for remote authentication had expired.

### Fix (Pending)
1. Generate a new PAT at [github.com/settings/tokens](https://github.com/settings/tokens)
2. Set new remote URL: `git remote set-url origin https://NEW-TOKEN@github.com/Hfrad23/electrical-estimator.git`
3. Push: `git push origin main`

### Prevention
- `RUNBOOK.md` now documents the exact commands for renewing a PAT and updating the remote URL
- Consider using GitHub CLI (`gh auth login`) instead of token-in-URL for more durable authentication
- `SECURITY.md` documents that PATs must never be committed to files

---

## [Future entries go here]

Add a new postmortem whenever:
- A bug caused incorrect BOM output
- An AI prompt change broke extraction
- A dependency upgrade caused failures
- Data was lost or corrupted
- A deployment/push failed in a non-obvious way
