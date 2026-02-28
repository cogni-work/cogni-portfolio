#!/bin/bash
# Validate cogni-portfolio project data model integrity.
# Usage: validate-entities.sh <project-dir>
# Checks: required fields, referential integrity, naming conventions.
# Outputs JSON with errors array and valid boolean.
# Exit codes: 0 = valid, 1 = errors found, 2 = usage error
set -euo pipefail

PROJECT_DIR="${1:-}"

if [ -z "$PROJECT_DIR" ] || [ ! -d "$PROJECT_DIR" ]; then
  echo '{"error": "Usage: validate-entities.sh <project-dir>"}' >&2
  exit 2
fi

errors="["
first=true

add_error() {
  if $first; then first=false; else errors="$errors, "; fi
  errors="$errors{\"entity\": \"$1\", \"file\": \"$2\", \"message\": \"$3\"}"
}

# Check portfolio.json exists and has required fields
if [ ! -f "$PROJECT_DIR/portfolio.json" ]; then
  add_error "portfolio" "portfolio.json" "Missing portfolio.json"
fi

# Validate products have required fields (slug, name, description)
if [ -d "$PROJECT_DIR/products" ]; then
  for p in "$PROJECT_DIR/products"/*.json; do
    [ -f "$p" ] || continue
    slug=$(basename "$p" .json)
    if ! python3 -c "
import json, sys
with open('$p') as fh:
    d = json.load(fh)
    if 'name' not in d: sys.exit(1)
    if 'description' not in d: sys.exit(1)
    if 'slug' in d and d['slug'] != '$slug': sys.exit(2)
    if 'maturity' in d and d['maturity'] not in ['concept','development','launch','growth','mature','decline']: sys.exit(3)
" 2>/dev/null; then
      add_error "product" "$slug" "Invalid JSON, missing required field (name, description), or invalid maturity value"
    fi
  done
fi

# Validate features have required fields (slug, name, description, product_slug)
if [ -d "$PROJECT_DIR/features" ]; then
  for f in "$PROJECT_DIR/features"/*.json; do
    [ -f "$f" ] || continue
    slug=$(basename "$f" .json)
    # Check file is valid JSON and has required fields
    if ! python3 -c "
import json, sys
with open('$f') as fh:
    d = json.load(fh)
    if 'name' not in d: sys.exit(1)
    if 'description' not in d: sys.exit(1)
    if 'slug' in d and d['slug'] != '$slug': sys.exit(2)
    if 'product_slug' not in d: sys.exit(3)
" 2>/dev/null; then
      add_error "feature" "$slug" "Invalid JSON, missing required field (name, description), or missing product_slug"
    else
      # Check referenced product exists
      p_slug=$(python3 -c "import json; print(json.load(open('$f')).get('product_slug',''))" 2>/dev/null)
      if [ -n "$p_slug" ] && [ ! -f "$PROJECT_DIR/products/${p_slug}.json" ]; then
        add_error "feature" "$slug" "References missing product: $p_slug"
      fi
    fi
  done
fi

# Validate markets have required fields (slug, name, description)
if [ -d "$PROJECT_DIR/markets" ]; then
  for m in "$PROJECT_DIR/markets"/*.json; do
    [ -f "$m" ] || continue
    slug=$(basename "$m" .json)
    if ! python3 -c "
import json, sys
with open('$m') as fh:
    d = json.load(fh)
    if 'name' not in d: sys.exit(1)
    if 'description' not in d: sys.exit(1)
    if 'slug' in d and d['slug'] != '$slug': sys.exit(2)
" 2>/dev/null; then
      add_error "market" "$slug" "Invalid JSON or missing required field (name, description)"
    fi
  done
fi

# Validate propositions reference valid features and markets
if [ -d "$PROJECT_DIR/propositions" ]; then
  for s in "$PROJECT_DIR/propositions"/*.json; do
    [ -f "$s" ] || continue
    slug=$(basename "$s" .json)
    # Check naming convention: feature-slug--market-slug
    if [[ "$slug" != *"--"* ]]; then
      add_error "proposition" "$slug" "Invalid naming: expected feature-slug--market-slug"
      continue
    fi
    f_slug="${slug%%--*}"
    m_slug="${slug#*--}"
    # Check referenced feature exists
    if [ ! -f "$PROJECT_DIR/features/${f_slug}.json" ]; then
      add_error "proposition" "$slug" "References missing feature: $f_slug"
    fi
    # Check referenced market exists
    if [ ! -f "$PROJECT_DIR/markets/${m_slug}.json" ]; then
      add_error "proposition" "$slug" "References missing market: $m_slug"
    fi
    # Check required fields including foreign keys
    if ! python3 -c "
import json, sys
with open('$s') as fh:
    d = json.load(fh)
    for field in ['feature_slug', 'market_slug', 'is_statement', 'does_statement', 'means_statement']:
        if field not in d: sys.exit(1)
" 2>/dev/null; then
      add_error "proposition" "$slug" "Missing required fields (feature_slug, market_slug, is_statement, does_statement, means_statement)"
    fi
  done
fi

# Validate competitors reference valid propositions
if [ -d "$PROJECT_DIR/competitors" ]; then
  for c in "$PROJECT_DIR/competitors"/*.json; do
    [ -f "$c" ] || continue
    slug=$(basename "$c" .json)
    if [ ! -f "$PROJECT_DIR/propositions/${slug}.json" ]; then
      add_error "competitor" "$slug" "References missing proposition: $slug"
    fi
  done
fi

# Validate customers reference valid markets
if [ -d "$PROJECT_DIR/customers" ]; then
  for c in "$PROJECT_DIR/customers"/*.json; do
    [ -f "$c" ] || continue
    slug=$(basename "$c" .json)
    if [ ! -f "$PROJECT_DIR/markets/${slug}.json" ]; then
      add_error "customer" "$slug" "References missing market: $slug"
    fi
  done
fi

errors="$errors]"

if $first; then
  echo '{"valid": true, "errors": []}'
  exit 0
else
  echo "{\"valid\": false, \"errors\": $errors}"
  exit 1
fi
