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

cat << EOF
{
  "counts": {
    "products": $PRODUCTS,
    "features": $FEATURES,
    "markets": $MARKETS,
    "solutions": $SOLUTIONS,
    "expected_solutions": $EXPECTED,
    "competitors": $COMPETITORS,
    "customers": $CUSTOMERS
  },
  "products": $product_arr,
  "features": $feature_arr,
  "markets": $market_arr,
  "missing_solutions": $missing_arr,
  "completion": {
    "solutions_pct": $(( EXPECTED > 0 ? (SOLUTIONS * 100 / EXPECTED) : 0 )),
    "competitors_pct": $(( SOLUTIONS > 0 ? (COMPETITORS * 100 / SOLUTIONS) : 0 )),
    "customers_pct": $(( MARKETS > 0 ? (CUSTOMERS * 100 / MARKETS) : 0 ))
  }
}
EOF
