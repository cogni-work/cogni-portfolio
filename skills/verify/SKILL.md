---
name: verify
description: |
  This skill should be used when the user asks to "verify claims",
  "check portfolio claims", "claim status", "verify portfolio",
  "review claims", or "fact-check". Portfolio workflow phase between
  enrichment and synthesis that verifies web-sourced claims.
---

# Portfolio Claim Verification

Workflow phase that verifies claims submitted by portfolio research agents (market-researcher, competitor-researcher, solution-generator) against their cited web sources. Runs between the enrichment phase and synthesis phase.

## Prerequisites

This skill requires the `cogni-claims` plugin to be installed and active. It provides the verification engine (claim-verifier agent) and claim management UI (dashboard, inspect, resolve). If the `cogni-claims:claims` skill is not available, inform the user that verification requires the cogni-claims plugin and provide installation guidance.

Check that claims exist:

```bash
test -f "<project-dir>/.claims/claims.json" && echo "Claims workspace found" || echo "No claims workspace"
```

If no `.claims/` directory exists, inform the user that no claims have been submitted yet. Research agents submit claims automatically during market research, competitor research, and solution generation (when web search is used). Suggest running those skills with web research enabled first.

## Workflow

### 1. Show Claim Summary

Read `.claims/claims.json` and count claims by status:

```
Claims Summary:
- Unverified: N
- Verified: N
- Deviated: N (X critical, Y high, Z medium, W low)
- Source unavailable: N
- Resolved: N
Total: N claims from K unique sources
```

Also show breakdown by submitter (cogni-portfolio:market-researcher, cogni-portfolio:competitor-researcher, cogni-portfolio:solution-generator).

### 2. Verification

If unverified claims exist, ask the user if they want to run verification. When confirmed, invoke the `cogni-claims:claims` skill with mode `verify`:

```
Use the cogni-claims:claims skill to verify all unverified claims.
Working directory: <project-dir>
```

The claims skill handles grouping by URL, parallel agent dispatch, and result collection.

### 3. Review Results

After verification completes, show the updated summary. If deviations were found:

- List claims with `high` or `critical` severity deviations
- For each, show: claim statement, deviation type, severity
- Suggest using `cogni-claims:claims` skill with mode `inspect` for detailed evidence

### 4. Resolution Guidance

If deviated claims exist, offer resolution options:

1. **Review and resolve individually** -- invoke `cogni-claims:claims` with mode `resolve` for each
2. **Show dashboard** -- invoke `cogni-claims:claims` with mode `dashboard` for full overview
3. **Proceed to synthesis anyway** -- warn that unresolved deviations will be flagged in output

### 5. Synthesis Gate

Before the user proceeds to synthesis, present the verification status as a gate:

```
Verification Gate:
- Verified: N claims (safe to use)
- Resolved: N claims (user-approved corrections)
- Deviated (unresolved): N claims (will be flagged in output)
- Unverified: N claims (will be flagged in output)

Recommendation: [Resolve remaining deviations / Ready for synthesis]
```

If all claims are verified or resolved, confirm the portfolio is ready for synthesis. If deviations remain, the user may still proceed -- the synthesize and export skills will flag unverified content.

## Important Notes

- This skill orchestrates; `cogni-claims:claims` does the actual verification work
- Never auto-resolve deviations -- the user must decide
- Claims without web sources (internal estimates) are not submitted and do not need verification
- Re-running verification on already-verified claims is safe (re-verification)
- The `.claims/` directory is inside the portfolio project directory
