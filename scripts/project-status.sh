#!/bin/bash
# Show cogni-portfolio project status with entity counts and gap analysis.
# Usage: project-status.sh <project-dir>
# Outputs JSON with counts, feature/market slugs, missing solutions, and completion ratios.
# Exit codes: 0 = success, 1 = error
set -euo pipefail

PROJECT_DIR="${1:-}"

if [ -z "$PROJECT_DIR" ] || [ ! -d "$PROJECT_DIR" ]; then
  echo '{"error": "Valid project directory required. Usage: project-status.sh <project-dir>"}' >&2
  exit 1
fi

if [ ! -f "$PROJECT_DIR/portfolio.json" ]; then
  echo '{"error": "Not a cogni-portfolio project (missing portfolio.json)"}' >&2
  exit 1
fi

# Count JSON files in a subdirectory
count_json() {
  local dir="$PROJECT_DIR/$1"
  if [ -d "$dir" ]; then
    local n
    n=$(find "$dir" -maxdepth 1 -name '*.json' 2>/dev/null | wc -l)
    echo "$n" | tr -d ' '
  else
    echo "0"
  fi
}

PRODUCTS=$(count_json "products")
FEATURES=$(count_json "features")
MARKETS=$(count_json "markets")
SOLUTIONS=$(count_json "solutions")
COMPETITORS=$(count_json "competitors")
CUSTOMERS=$(count_json "customers")
EXPECTED=$((FEATURES * MARKETS))

# Collect product slugs as JSON array
product_arr="["
first=true
if [ -d "$PROJECT_DIR/products" ]; then
  for p in "$PROJECT_DIR/products"/*.json; do
    [ -f "$p" ] || continue
    slug=$(basename "$p" .json)
    if $first; then first=false; else product_arr="$product_arr, "; fi
    product_arr="$product_arr\"$slug\""
  done
fi
product_arr="$product_arr]"

# Collect feature slugs as JSON array
feature_arr="["
first=true
if [ -d "$PROJECT_DIR/features" ]; then
  for f in "$PROJECT_DIR/features"/*.json; do
    [ -f "$f" ] || continue
    slug=$(basename "$f" .json)
    if $first; then first=false; else feature_arr="$feature_arr, "; fi
    feature_arr="$feature_arr\"$slug\""
  done
fi
feature_arr="$feature_arr]"

# Collect market slugs as JSON array
market_arr="["
first=true
if [ -d "$PROJECT_DIR/markets" ]; then
  for m in "$PROJECT_DIR/markets"/*.json; do
    [ -f "$m" ] || continue
    slug=$(basename "$m" .json)
    if $first; then first=false; else market_arr="$market_arr, "; fi
    market_arr="$market_arr\"$slug\""
  done
fi
market_arr="$market_arr]"

# Find missing solutions (Feature x Market pairs without a solution file)
missing_arr="["
first=true
if [ "$FEATURES" -gt 0 ] && [ "$MARKETS" -gt 0 ]; then
  for f in "$PROJECT_DIR/features"/*.json; do
    [ -f "$f" ] || continue
    f_slug=$(basename "$f" .json)
    for m in "$PROJECT_DIR/markets"/*.json; do
      [ -f "$m" ] || continue
      m_slug=$(basename "$m" .json)
      sol="$PROJECT_DIR/solutions/${f_slug}--${m_slug}.json"
      if [ ! -f "$sol" ]; then
        if $first; then first=false; else missing_arr="$missing_arr, "; fi
        missing_arr="$missing_arr\"${f_slug}--${m_slug}\""
      fi
    done
  done
fi
missing_arr="$missing_arr]"

MISSING_COUNT=$((EXPECTED - SOLUTIONS))
if [ "$MISSING_COUNT" -lt 0 ]; then MISSING_COUNT=0; fi

if [ "$EXPECTED" -gt 0 ]; then
  SOLUTIONS_PCT=$(( SOLUTIONS * 100 / EXPECTED ))
else
  SOLUTIONS_PCT=0
fi
if [ "$SOLUTIONS" -gt 0 ]; then
  COMPETITORS_PCT=$(( COMPETITORS * 100 / SOLUTIONS ))
else
  COMPETITORS_PCT=0
fi
if [ "$MARKETS" -gt 0 ]; then
  CUSTOMERS_PCT=$(( CUSTOMERS * 100 / MARKETS ))
else
  CUSTOMERS_PCT=0
fi

HAS_README="false"
if [ -f "$PROJECT_DIR/output/README.md" ]; then HAS_README="true"; fi
HAS_XLSX="false"
if [ -f "$PROJECT_DIR/output/portfolio.xlsx" ]; then HAS_XLSX="true"; fi

# Count unprocessed uploads (exclude processed/ subdirectory)
UPLOADS=0
if [ -d "$PROJECT_DIR/uploads" ]; then
  UPLOADS=$(find "$PROJECT_DIR/uploads" -maxdepth 1 -type f \( -name '*.md' -o -name '*.docx' -o -name '*.pptx' -o -name '*.xlsx' -o -name '*.pdf' \) 2>/dev/null | wc -l)
  UPLOADS=$(echo "$UPLOADS" | tr -d ' ')
fi

# Count claims by status
CLAIMS_TOTAL=0
CLAIMS_UNVERIFIED=0
CLAIMS_VERIFIED=0
CLAIMS_DEVIATED=0
CLAIMS_RESOLVED=0
CLAIMS_UNAVAILABLE=0
HAS_CLAIMS="false"
if [ -f "$PROJECT_DIR/.claims/claims.json" ]; then
  HAS_CLAIMS="true"
  eval "$(python3 -c "
import json, sys
try:
    with open('$PROJECT_DIR/.claims/claims.json') as f:
        data = json.load(f)
    claims = data.get('claims', [])
    counts = {}
    for c in claims:
        s = c.get('status', 'unverified')
        counts[s] = counts.get(s, 0) + 1
    print(f'CLAIMS_TOTAL={len(claims)}')
    print(f'CLAIMS_UNVERIFIED={counts.get(\"unverified\", 0)}')
    print(f'CLAIMS_VERIFIED={counts.get(\"verified\", 0)}')
    print(f'CLAIMS_DEVIATED={counts.get(\"deviated\", 0)}')
    print(f'CLAIMS_RESOLVED={counts.get(\"resolved\", 0)}')
    print(f'CLAIMS_UNAVAILABLE={counts.get(\"source_unavailable\", 0)}')
except Exception:
    print('CLAIMS_TOTAL=0')
" 2>/dev/null)"
fi
CLAIMS_CLEAN=$((CLAIMS_VERIFIED + CLAIMS_RESOLVED))
CLAIMS_PENDING=$((CLAIMS_UNVERIFIED + CLAIMS_DEVIATED))

# Determine workflow phase (evaluated in priority order)
if [ "$PRODUCTS" -eq 0 ]; then
  PHASE="products"
elif [ "$FEATURES" -eq 0 ]; then
  PHASE="features"
elif [ "$MARKETS" -eq 0 ]; then
  PHASE="markets"
elif [ "$MISSING_COUNT" -gt 0 ]; then
  PHASE="solutions"
elif [ "$COMPETITORS_PCT" -lt 100 ] || [ "$CUSTOMERS_PCT" -lt 100 ]; then
  PHASE="enrichment"
elif [ "$HAS_CLAIMS" = "true" ] && [ "$CLAIMS_PENDING" -gt 0 ]; then
  PHASE="verification"
elif [ "$HAS_README" = "false" ]; then
  PHASE="synthesis"
elif [ "$HAS_XLSX" = "false" ]; then
  PHASE="export"
else
  PHASE="complete"
fi

# Build next_actions array
next_actions="["
na_first=true
add_action() {
  if $na_first; then na_first=false; else next_actions="$next_actions, "; fi
  next_actions="$next_actions{\"skill\": \"$1\", \"reason\": \"$2\"}"
}

case "$PHASE" in
  products)
    add_action "products" "No products defined yet"
    ;;
  features)
    add_action "features" "$PRODUCTS product(s) exist but no features defined"
    ;;
  markets)
    add_action "markets" "Features defined but no target markets yet"
    ;;
  solutions)
    add_action "solutions" "$MISSING_COUNT of $EXPECTED Feature x Market pairs pending"
    ;;
  enrichment)
    if [ "$COMPETITORS_PCT" -lt 100 ]; then
      missing_comp=$((SOLUTIONS - COMPETITORS))
      add_action "compete" "$missing_comp solution(s) lack competitor analysis"
    fi
    if [ "$CUSTOMERS_PCT" -lt 100 ]; then
      missing_cust=$((MARKETS - CUSTOMERS))
      add_action "customers" "$missing_cust market(s) lack customer profiles"
    fi
    ;;
  verification)
    add_action "verify" "$CLAIMS_PENDING claim(s) pending verification ($CLAIMS_UNVERIFIED unverified, $CLAIMS_DEVIATED deviated)"
    ;;
  synthesis)
    add_action "synthesize" "All entities complete -- ready to generate portfolio overview"
    ;;
  export)
    add_action "export" "Synthesis done -- ready to generate deliverables"
    ;;
  complete)
    ;;
esac
next_actions="$next_actions]"

cat << EOF
{
  "counts": {
    "products": $PRODUCTS,
    "features": $FEATURES,
    "markets": $MARKETS,
    "solutions": $SOLUTIONS,
    "expected_solutions": $EXPECTED,
    "competitors": $COMPETITORS,
    "customers": $CUSTOMERS,
    "uploads": $UPLOADS
  },
  "claims": {
    "total": $CLAIMS_TOTAL,
    "unverified": $CLAIMS_UNVERIFIED,
    "verified": $CLAIMS_VERIFIED,
    "deviated": $CLAIMS_DEVIATED,
    "resolved": $CLAIMS_RESOLVED,
    "source_unavailable": $CLAIMS_UNAVAILABLE
  },
  "products": $product_arr,
  "features": $feature_arr,
  "markets": $market_arr,
  "missing_solutions": $missing_arr,
  "phase": "$PHASE",
  "next_actions": $next_actions,
  "completion": {
    "solutions_pct": $SOLUTIONS_PCT,
    "competitors_pct": $COMPETITORS_PCT,
    "customers_pct": $CUSTOMERS_PCT
  }
}
EOF
