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
warnings="["
first_warning=true

add_error() {
  if $first; then first=false; else errors="$errors, "; fi
  errors="$errors{\"entity\": \"$1\", \"file\": \"$2\", \"message\": \"$3\"}"
}

add_warning() {
  if $first_warning; then first_warning=false; else warnings="$warnings, "; fi
  warnings="$warnings{\"entity\": \"$1\", \"file\": \"$2\", \"message\": \"$3\"}"
}

# Check portfolio.json exists and has required fields
if [ ! -f "$PROJECT_DIR/portfolio.json" ]; then
  add_error "portfolio" "portfolio.json" "Missing portfolio.json"
fi

# Check portfolio.json company.products matches actual products/ directory
if [ -f "$PROJECT_DIR/portfolio.json" ] && [ -d "$PROJECT_DIR/products" ]; then
  python3 -c "
import json, os, sys
pf = json.load(open('$PROJECT_DIR/portfolio.json'))
company = pf.get('company', pf)
listed = sorted(company.get('products', [])) if isinstance(company, dict) else []
actual = sorted(f[:-5] for f in os.listdir('$PROJECT_DIR/products') if f.endswith('.json'))
if listed != actual:
    missing_in_pf = [s for s in actual if s not in listed]
    extra_in_pf = [s for s in listed if s not in actual]
    msgs = []
    if missing_in_pf: msgs.append('products/ has ' + ', '.join(missing_in_pf) + ' not listed in portfolio.json')
    if extra_in_pf: msgs.append('portfolio.json lists ' + ', '.join(extra_in_pf) + ' not found in products/')
    print('; '.join(msgs))
    sys.exit(1)
" 2>/dev/null || {
    sync_msg=$(python3 -c "
import json, os
pf = json.load(open('$PROJECT_DIR/portfolio.json'))
company = pf.get('company', pf)
listed = sorted(company.get('products', [])) if isinstance(company, dict) else []
actual = sorted(f[:-5] for f in os.listdir('$PROJECT_DIR/products') if f.endswith('.json'))
missing = [s for s in actual if s not in listed]
extra = [s for s in listed if s not in actual]
msgs = []
if missing: msgs.append('products/ has ' + ', '.join(missing) + ' not in portfolio.json')
if extra: msgs.append('portfolio.json lists ' + ', '.join(extra) + ' not in products/')
print('; '.join(msgs))
" 2>/dev/null)
    add_error "portfolio" "portfolio.json" "Product list out of sync: $sync_msg. Run sync-portfolio.sh to fix."
  }
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
    exit_code=0
    python3 -c "
import json, sys
with open('$f') as fh:
    d = json.load(fh)
    if 'name' not in d: sys.exit(1)
    if 'description' not in d: sys.exit(1)
    if 'slug' in d and d['slug'] != '$slug': sys.exit(2)
    if 'product_slug' not in d: sys.exit(3)
    if 'readiness' in d and d['readiness'] not in ['ga', 'beta', 'planned']: sys.exit(4)
" 2>/dev/null || exit_code=$?
    if [ "$exit_code" -eq 4 ]; then
      add_error "feature" "$slug" "Invalid readiness value -- must be one of: ga, beta, planned"
    elif [ "$exit_code" -ne 0 ]; then
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

# Warn on singleton categories (possible typos)
if [ -d "$PROJECT_DIR/features" ]; then
  while IFS='|' read -r slug msg; do
    add_warning "feature" "$slug" "$msg"
  done < <(python3 -c "
import json, os, glob
cats = {}
for f in glob.glob('$PROJECT_DIR/features/*.json'):
    try:
        d = json.load(open(f))
        c = d.get('category')
        if c:
            cats.setdefault(c, []).append(os.path.basename(f)[:-5])
    except Exception:
        pass
for cat, slugs in cats.items():
    if len(slugs) == 1:
        print(f'{slugs[0]}|Category {cat} is used by only one feature -- possible typo')
" 2>/dev/null)
fi

# Valid region codes from the taxonomy
VALID_REGIONS="de dach eu uk nordics us na cn apac jp latam mea global"

# Validate markets have required fields (slug, name, region, description)
if [ -d "$PROJECT_DIR/markets" ]; then
  for m in "$PROJECT_DIR/markets"/*.json; do
    [ -f "$m" ] || continue
    slug=$(basename "$m" .json)
    exit_code=0
    python3 -c "
import json, sys
with open('$m') as fh:
    d = json.load(fh)
    if 'name' not in d: sys.exit(1)
    if 'description' not in d: sys.exit(1)
    if 'slug' in d and d['slug'] != '$slug': sys.exit(2)
    if 'region' not in d: sys.exit(3)
    if 'priority' in d and d['priority'] not in ['beachhead', 'expansion', 'aspirational']: sys.exit(4)
" 2>/dev/null || exit_code=$?
    if [ "$exit_code" -eq 4 ]; then
      add_error "market" "$slug" "Invalid priority value -- must be one of: beachhead, expansion, aspirational"
    elif [ "$exit_code" -ne 0 ]; then
      add_error "market" "$slug" "Invalid JSON or missing required field (name, description, region)"
    else
      # Validate region code against taxonomy
      region=$(python3 -c "import json; print(json.load(open('$m')).get('region',''))" 2>/dev/null)
      region_valid=false
      for r in $VALID_REGIONS; do
        if [ "$region" = "$r" ]; then region_valid=true; break; fi
      done
      if [ "$region_valid" = "false" ]; then
        add_error "market" "$slug" "Invalid region '$region' -- must be one of: $VALID_REGIONS"
      fi
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

# Validate solutions reference valid propositions and have required structure
if [ -d "$PROJECT_DIR/solutions" ]; then
  for s in "$PROJECT_DIR/solutions"/*.json; do
    [ -f "$s" ] || continue
    slug=$(basename "$s" .json)
    if [ ! -f "$PROJECT_DIR/propositions/${slug}.json" ]; then
      add_error "solution" "$slug" "References missing proposition: $slug"
    fi
    exit_code=0
    python3 -c "
import json, sys
with open('$s') as fh:
    d = json.load(fh)
    if 'proposition_slug' not in d: sys.exit(1)
    impl = d.get('implementation')
    if not isinstance(impl, list) or len(impl) == 0: sys.exit(2)
    for phase in impl:
        if 'phase' not in phase or 'duration_weeks' not in phase: sys.exit(3)
        dw = phase.get('duration_weeks')
        if not isinstance(dw, (int, float)) and not (isinstance(dw, str) and dw.isdigit()):
            sys.exit(6)
    pricing = d.get('pricing')
    if not isinstance(pricing, dict): sys.exit(4)
    for tier in ['proof_of_value', 'small', 'medium', 'large']:
        t = pricing.get(tier)
        if not isinstance(t, dict) or 'price' not in t or 'currency' not in t: sys.exit(5)
" 2>/dev/null || exit_code=$?
    if [ "$exit_code" -eq 6 ]; then
      add_warning "solution" "$slug" "Non-numeric duration_weeks value (e.g. 'ongoing') — accepted but may affect duration totals"
    elif [ "$exit_code" -ne 0 ]; then
      add_error "solution" "$slug" "Missing required fields or invalid structure (needs proposition_slug, implementation phases, pricing tiers)"
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
warnings="$warnings]"

if $first; then
  echo "{\"valid\": true, \"errors\": [], \"warnings\": $warnings}"
  exit 0
else
  echo "{\"valid\": false, \"errors\": $errors, \"warnings\": $warnings}"
  exit 1
fi
