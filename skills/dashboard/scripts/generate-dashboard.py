#!/usr/bin/env python3
"""Generate a self-contained HTML dashboard for a cogni-portfolio project.

Usage: python3 generate-dashboard.py <project-dir> [--theme <path-to-theme.md>]
Output: <project-dir>/output/dashboard.html
Returns JSON: {"status": "ok", "path": "<output-path>", "theme": "<name>"} or {"error": "..."}
"""

import json
import glob
import os
import re
import sys
import subprocess
from datetime import datetime


# ---------------------------------------------------------------------------
# Theme parser — reads a cogni-workspace theme.md and extracts design tokens
# ---------------------------------------------------------------------------

DEFAULT_THEME = {
    "name": "cogni-work",
    "colors": {
        "primary": "#111111",
        "secondary": "#333333",
        "accent": "#C8E62E",
        "accent_muted": "#A8C424",
        "accent_dark": "#8BA31E",
        "background": "#FAFAF8",
        "surface": "#F2F2EE",
        "surface_dark": "#111111",
        "text": "#111111",
        "text_light": "#FFFFFF",
        "text_muted": "#6B7280",
        "border": "#E0E0DC",
    },
    "status": {
        "success": "#2E7D32",
        "warning": "#E5A100",
        "danger": "#D32F2F",
        "info": "#1565C0",
    },
    "fonts": {
        "headers": "'DM Sans', Inter, Calibri, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
        "body": "'DM Sans', Inter, Calibri, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
        "mono": "'JetBrains Mono', 'Fira Code', Consolas, monospace",
    },
}


def parse_theme(theme_path):
    """Parse a cogni-workspace theme.md file into a design tokens dict.

    Theme files use this markdown pattern:
      - **Token Name**: `#HEX` - Description
      - **Headers**: Font Name Bold / fallback: ...
    """
    if not theme_path or not os.path.isfile(theme_path):
        return DEFAULT_THEME.copy()

    with open(theme_path) as f:
        content = f.read()

    theme = {
        "name": "",
        "colors": {},
        "status": {},
        "fonts": {},
    }

    # Extract theme name from first heading
    m = re.search(r'^#\s+(.+)', content, re.MULTILINE)
    if m:
        theme["name"] = m.group(1).strip()

    # Extract color tokens: **Name**: `#HEX` - description
    # Map common token names to our CSS variable names
    color_map = {
        "primary": "primary",
        "secondary": "secondary",
        "accent": "accent",
        "accent muted": "accent_muted",
        "accent dark": "accent_dark",
        "background": "background",
        "surface": "surface",
        "surface dark": "surface_dark",
        "text": "text",
        "text light": "text_light",
        "text muted": "text_muted",
        "border": "border",
    }
    status_map = {
        "success": "success",
        "warning": "warning",
        "danger": "danger",
        "info": "info",
    }

    # Parse all color lines
    for m in re.finditer(r'-\s+\*\*([^*]+)\*\*:\s*`(#[0-9A-Fa-f]{3,8})`', content):
        name = m.group(1).strip().lower()
        hex_val = m.group(2).strip()

        # Check color palette tokens
        for key, var_name in color_map.items():
            if name == key or name.startswith(key + " "):
                # Prefer exact match; for "text" avoid matching "text light"/"text muted"
                if name == key:
                    theme["colors"][var_name] = hex_val
                    break
                # Allow prefix match only for multi-word tokens
                elif " " in key and name.startswith(key):
                    theme["colors"][var_name] = hex_val
                    break
        else:
            # Check status tokens
            for key, var_name in status_map.items():
                if name == key or name.startswith(key):
                    theme["status"][var_name] = hex_val
                    break

    # Re-parse to catch "text light" and "text muted" specifically
    for m in re.finditer(r'-\s+\*\*([^*]+)\*\*:\s*`(#[0-9A-Fa-f]{3,8})`', content):
        name = m.group(1).strip().lower()
        hex_val = m.group(2).strip()
        if name == "text light":
            theme["colors"]["text_light"] = hex_val
        elif name == "text muted":
            theme["colors"]["text_muted"] = hex_val

    # Parse font lines: **Headers**: Font Name / fallback: ...
    font_patterns = {
        "headers": r'-\s+\*\*Headers?\*\*:\s*(.+)',
        "body": r'-\s+\*\*Body\*\*:\s*(.+)',
        "mono": r'-\s+\*\*Mono\*\*:\s*(.+)',
    }
    for key, pattern in font_patterns.items():
        fm = re.search(pattern, content, re.IGNORECASE)
        if fm:
            raw = fm.group(1).strip()
            # Convert "Font Name Bold / fallback: Alt1, Alt2" to CSS font-family
            fonts = re.split(r'\s*/\s*fallback:\s*', raw, maxsplit=1)
            primary_font = fonts[0].strip().rstrip(" Bold").rstrip(" Regular")
            fallbacks = fonts[1].strip() if len(fonts) > 1 else ""
            # Build CSS value
            parts = [f"'{primary_font}'"]
            if fallbacks:
                for fb in fallbacks.split(","):
                    fb = fb.strip().rstrip(" Bold").rstrip(" Regular")
                    if fb:
                        parts.append(f"'{fb}'" if " " in fb else fb)
            if key == "mono":
                parts.append("monospace")
            else:
                parts.extend(["-apple-system", "BlinkMacSystemFont", "'Segoe UI'", "sans-serif"])
            theme["fonts"][key] = ", ".join(parts)

    # Fill missing tokens from defaults
    for section in ["colors", "status", "fonts"]:
        for k, v in DEFAULT_THEME[section].items():
            if k not in theme[section]:
                theme[section] = dict(theme[section])
                theme[section][k] = v

    if not theme["name"]:
        theme["name"] = DEFAULT_THEME["name"]

    return theme


def derive_surface2(surface_hex):
    """Derive a slightly darker surface variant from the surface color."""
    try:
        r, g, b = int(surface_hex[1:3], 16), int(surface_hex[3:5], 16), int(surface_hex[5:7], 16)
        # Darken by ~4%
        factor = 0.96
        r2, g2, b2 = int(r * factor), int(g * factor), int(b * factor)
        return f"#{r2:02x}{g2:02x}{b2:02x}"
    except Exception:
        return "#E8E8E4"


def google_fonts_url(theme):
    """Build a Google Fonts import URL from theme font names."""
    font_names = set()
    for key in ["headers", "body"]:
        val = theme["fonts"].get(key, "")
        m = re.match(r"'([^']+)'", val)
        if m:
            font_names.add(m.group(1))
    mono_val = theme["fonts"].get("mono", "")
    m = re.match(r"'([^']+)'", mono_val)
    if m:
        font_names.add(m.group(1))

    if not font_names:
        return ""

    families = []
    for name in sorted(font_names):
        encoded = name.replace(" ", "+")
        if "mono" in name.lower() or "code" in name.lower():
            families.append(f"family={encoded}:wght@400;500")
        else:
            families.append(f"family={encoded}:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,700")

    return f"https://fonts.googleapis.com/css2?{'&'.join(families)}&display=swap"


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_json(path):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return None


def load_all_entities(project_dir):
    data = {
        "portfolio": load_json(os.path.join(project_dir, "portfolio.json")) or {},
        "products": {},
        "features": {},
        "markets": {},
        "propositions": {},
        "solutions": {},
        "competitors": {},
        "customers": {},
        "claims": None,
    }
    for entity_type in ["products", "features", "markets", "propositions", "solutions", "competitors", "customers"]:
        entity_dir = os.path.join(project_dir, entity_type)
        if os.path.isdir(entity_dir):
            for fp in sorted(glob.glob(os.path.join(entity_dir, "*.json"))):
                slug = os.path.basename(fp).replace(".json", "")
                obj = load_json(fp)
                if obj:
                    data[entity_type][slug] = obj
    claims_path = os.path.join(project_dir, "cogni-claims", "claims.json")
    if os.path.isfile(claims_path):
        data["claims"] = load_json(claims_path)
    return data


def get_status(project_dir):
    plugin_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    script = os.path.join(plugin_root, "scripts", "project-status.sh")
    try:
        result = subprocess.run(["bash", script, project_dir], capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            return json.loads(result.stdout)
    except Exception:
        pass
    return None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def escape_html(text):
    if not isinstance(text, str):
        text = str(text) if text is not None else ""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def escape_js_string(text):
    if not isinstance(text, str):
        text = str(text) if text is not None else ""
    return text.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n").replace("\r", "")


def format_currency(value, currency="EUR"):
    if value is None:
        return "N/A"
    if value >= 1_000_000_000:
        return f"{currency} {value / 1_000_000_000:.1f}B"
    if value >= 1_000_000:
        return f"{currency} {value / 1_000_000:.1f}M"
    if value >= 1_000:
        return f"{currency} {value / 1_000:.0f}K"
    return f"{currency} {value:,.0f}"


# ---------------------------------------------------------------------------
# HTML generation
# ---------------------------------------------------------------------------

def generate_html(data, status, project_dir, theme):
    """Generate the full HTML dashboard string."""
    portfolio = data["portfolio"]
    company = portfolio.get("company", {})
    company_name = escape_html(company.get("name", "Unknown Company"))
    company_desc = escape_html(company.get("description", ""))
    company_industry = escape_html(company.get("industry", ""))
    project_slug = escape_html(portfolio.get("slug", ""))

    counts = status.get("counts", {}) if status else {}
    completion = status.get("completion", {}) if status else {}
    phase = status.get("phase", "unknown") if status else "unknown"
    next_actions = status.get("next_actions", []) if status else []
    claims_status = status.get("claims", {}) if status else {}

    phases = ["products", "features", "markets", "propositions", "enrichment", "verification", "synthesis", "export", "complete"]
    phase_idx = phases.index(phase) if phase in phases else 0
    phase_pct = int((phase_idx / (len(phases) - 1)) * 100) if len(phases) > 1 else 0

    market_slugs = sorted(data["markets"].keys())
    feature_slugs = sorted(data["features"].keys())

    entities_json = json.dumps({
        "products": data["products"],
        "features": data["features"],
        "markets": data["markets"],
        "propositions": data["propositions"],
        "solutions": data["solutions"],
        "competitors": data["competitors"],
        "customers": data["customers"],
    }, default=str)

    # Theme CSS variables
    c = theme["colors"]
    s = theme["status"]
    fonts = theme["fonts"]
    surface2 = derive_surface2(c["surface"])
    fonts_url = google_fonts_url(theme)
    fonts_import = f"@import url('{fonts_url}');" if fonts_url else ""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{company_name} — Portfolio Dashboard</title>
<style>
{fonts_import}
:root {{
  --bg: {c['background']};
  --surface: {c['surface']};
  --surface2: {surface2};
  --surface-dark: {c['surface_dark']};
  --border: {c['border']};
  --text: {c['text']};
  --text2: {c['text_muted']};
  --text-light: {c['text_light']};
  --accent: {c['accent']};
  --accent-muted: {c['accent_muted']};
  --accent-dark: {c['accent_dark']};
  --green: {s['success']};
  --yellow: {s['warning']};
  --red: {s['danger']};
  --blue: {s['info']};
  --font-body: {fonts['body']};
  --font-headers: {fonts['headers']};
  --font-mono: {fonts['mono']};
  --radius: 10px;
}}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ background: var(--bg); color: var(--text); font-family: var(--font-body); line-height: 1.6; }}
h1, h2, h3, h4, h5 {{ font-family: var(--font-headers); }}
code, .mono {{ font-family: var(--font-mono); }}
.container {{ max-width: 1400px; margin: 0 auto; padding: 24px; }}

/* Header — dark structural anchor */
.header {{ background: var(--surface-dark); color: var(--text-light); padding: 32px 32px 24px; border-radius: var(--radius); margin-bottom: 32px; }}
.header h1 {{ font-size: 28px; font-weight: 700; margin-bottom: 4px; color: var(--text-light); }}
.header .meta {{ color: rgba(255,255,255,0.6); font-size: 14px; display: flex; gap: 20px; flex-wrap: wrap; }}
.header .meta span {{ display: flex; align-items: center; gap: 6px; }}
.header .desc {{ color: rgba(255,255,255,0.5); font-size: 14px; margin-top: 8px; }}

/* Phase progress */
.phase-bar {{ background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 20px 24px; margin-bottom: 24px; }}
.phase-bar h3 {{ font-size: 14px; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text2); margin-bottom: 12px; }}
.phase-steps {{ display: flex; gap: 4px; margin-bottom: 8px; }}
.phase-step {{ flex: 1; height: 6px; border-radius: 3px; background: var(--surface2); transition: background 0.3s; }}
.phase-step.done {{ background: var(--accent-dark); }}
.phase-step.current {{ background: var(--accent); }}
.phase-label {{ font-size: 15px; font-weight: 600; }}
.phase-label .tag {{ display: inline-block; background: var(--surface-dark); color: var(--accent); font-size: 11px; padding: 2px 8px; border-radius: 4px; margin-left: 8px; text-transform: uppercase; letter-spacing: 0.04em; font-family: var(--font-mono); }}

/* Cards grid */
.cards {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 12px; margin-bottom: 32px; }}
.card {{ background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 16px; cursor: default; transition: border-color 0.2s, box-shadow 0.2s; }}
.card:hover {{ border-color: var(--accent-muted); box-shadow: 0 2px 12px rgba(0,0,0,0.06); }}
.card .label {{ font-size: 11px; color: var(--text2); text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 4px; font-weight: 500; }}
.card .value {{ font-size: 28px; font-weight: 700; font-family: var(--font-mono); }}
.card .sub {{ font-size: 12px; color: var(--text2); margin-top: 2px; }}
.card .bar {{ height: 4px; background: var(--surface2); border-radius: 2px; margin-top: 8px; overflow: hidden; }}
.card .bar .fill {{ height: 100%; border-radius: 2px; transition: width 0.5s; }}

/* Section */
.section {{ margin-bottom: 36px; }}
.section-title {{ font-size: 18px; font-weight: 700; margin-bottom: 16px; padding-bottom: 8px; border-bottom: 1px solid var(--border); }}

/* Matrix */
.matrix-wrap {{ overflow-x: auto; margin-bottom: 32px; }}
.matrix {{ border-collapse: separate; border-spacing: 2px; width: 100%; }}
.matrix th {{ background: var(--surface2); color: var(--text2); font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em; padding: 8px 10px; text-align: left; white-space: nowrap; position: sticky; top: 0; }}
.matrix th.corner {{ background: transparent; }}
.matrix td {{ padding: 0; }}
.matrix .cell {{ width: 100%; height: 48px; border: none; border-radius: 6px; cursor: pointer; font-size: 18px; display: flex; align-items: center; justify-content: center; transition: transform 0.15s, box-shadow 0.15s; }}
.matrix .cell:hover {{ transform: scale(1.08); box-shadow: 0 4px 16px rgba(0,0,0,0.15); z-index: 2; position: relative; }}
.cell.full {{ background: var(--green); color: #fff; }}
.cell.partial {{ background: var(--yellow); color: #fff; }}
.cell.missing {{ background: var(--red); color: #fff; opacity: 0.4; }}
.matrix .feature-label {{ font-size: 13px; color: var(--text); padding: 8px 10px; white-space: nowrap; background: var(--surface); border-radius: 6px; }}

/* Market cards */
.market-cards {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 16px; }}
.market-card {{ background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 20px; cursor: pointer; transition: border-color 0.2s, box-shadow 0.2s; }}
.market-card:hover {{ border-color: var(--accent-muted); box-shadow: 0 4px 20px rgba(0,0,0,0.06); }}
.market-card h4 {{ font-size: 15px; font-weight: 600; margin-bottom: 4px; }}
.market-card .region-badge {{ display: inline-block; background: var(--surface-dark); color: var(--accent); font-size: 10px; padding: 2px 8px; border-radius: 3px; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 8px; font-family: var(--font-mono); font-weight: 500; }}
.market-card .desc {{ font-size: 13px; color: var(--text2); margin-bottom: 12px; }}
.sizing-bars {{ display: flex; flex-direction: column; gap: 6px; }}
.sizing-row {{ display: flex; align-items: center; gap: 8px; font-size: 12px; }}
.sizing-row .sizing-label {{ width: 36px; color: var(--text2); text-transform: uppercase; font-weight: 600; font-family: var(--font-mono); }}
.sizing-row .sizing-bar {{ flex: 1; height: 8px; background: var(--surface2); border-radius: 4px; overflow: hidden; }}
.sizing-row .sizing-bar .fill {{ height: 100%; border-radius: 4px; }}
.sizing-row .sizing-val {{ width: 80px; text-align: right; color: var(--text); font-weight: 500; font-family: var(--font-mono); font-size: 11px; }}

/* Product list */
.product-group {{ background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); margin-bottom: 12px; overflow: hidden; }}
.product-header {{ padding: 16px 20px; cursor: pointer; display: flex; justify-content: space-between; align-items: center; }}
.product-header:hover {{ background: var(--surface2); }}
.product-header h4 {{ font-size: 15px; font-weight: 600; }}
.product-header .badge {{ font-size: 12px; color: var(--text2); }}
.product-features {{ padding: 0 20px 16px; }}
.feature-item {{ padding: 8px 0; border-top: 1px solid var(--border); font-size: 13px; }}
.feature-item .fname {{ font-weight: 600; }}
.feature-item .fdesc {{ color: var(--text2); }}

/* Solutions table */
.solutions-table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
.solutions-table th {{ text-align: left; padding: 10px 12px; background: var(--surface2); color: var(--text2); font-size: 11px; text-transform: uppercase; letter-spacing: 0.04em; font-weight: 600; }}
.solutions-table td {{ padding: 10px 12px; border-bottom: 1px solid var(--border); }}
.solutions-table tr:hover td {{ background: var(--surface); }}
.price {{ font-weight: 600; font-family: var(--font-mono); }}

/* Claims */
.claims-summary {{ display: flex; gap: 12px; flex-wrap: wrap; align-items: center; }}
.claims-chip {{ padding: 6px 14px; border-radius: 20px; font-size: 13px; font-weight: 500; }}

/* Next actions */
.action-item {{ background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 14px 20px; margin-bottom: 8px; display: flex; gap: 12px; align-items: center; }}
.action-skill {{ background: var(--surface-dark); color: var(--accent); padding: 3px 12px; border-radius: 4px; font-size: 12px; font-weight: 600; white-space: nowrap; font-family: var(--font-mono); }}
.action-reason {{ font-size: 14px; color: var(--text2); }}

/* Modal / Detail panel */
.overlay {{ display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.4); z-index: 100; justify-content: center; align-items: flex-start; padding: 60px 24px; overflow-y: auto; }}
.overlay.open {{ display: flex; }}
.panel {{ background: var(--bg); border: 1px solid var(--border); border-radius: 14px; max-width: 720px; width: 100%; padding: 28px 32px; position: relative; box-shadow: 0 24px 64px rgba(0,0,0,0.2); }}
.panel-close {{ position: absolute; top: 14px; right: 18px; background: none; border: none; color: var(--text2); font-size: 22px; cursor: pointer; }}
.panel-close:hover {{ color: var(--text); }}
.panel h3 {{ font-size: 18px; margin-bottom: 4px; }}
.panel .panel-sub {{ color: var(--text2); font-size: 13px; margin-bottom: 16px; font-family: var(--font-mono); }}
.panel .section-label {{ font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em; color: var(--accent-dark); font-weight: 700; margin-top: 16px; margin-bottom: 6px; }}
.panel .stmt {{ font-size: 14px; margin-bottom: 10px; line-height: 1.5; }}
.panel table {{ width: 100%; font-size: 13px; border-collapse: collapse; margin-top: 8px; }}
.panel table th {{ text-align: left; padding: 6px 10px; color: var(--text2); font-size: 11px; text-transform: uppercase; border-bottom: 1px solid var(--border); }}
.panel table td {{ padding: 6px 10px; border-bottom: 1px solid var(--border); }}
.competitor-card {{ background: var(--surface); border-radius: 8px; padding: 12px 16px; margin-bottom: 8px; }}
.competitor-card h5 {{ font-size: 14px; margin-bottom: 4px; }}
.competitor-card .comp-detail {{ font-size: 12px; color: var(--text2); margin-bottom: 2px; }}
.comp-pills {{ display: flex; flex-wrap: wrap; gap: 4px; margin-top: 4px; }}
.comp-pill {{ font-size: 11px; padding: 2px 8px; border-radius: 3px; }}
.comp-pill.strength {{ background: rgba(46,125,50,0.1); color: var(--green); }}
.comp-pill.weakness {{ background: rgba(211,47,47,0.1); color: var(--red); }}

/* Customer profile */
.profile-card {{ background: var(--surface); border-radius: 8px; padding: 14px 18px; margin-bottom: 10px; }}
.profile-card h5 {{ font-size: 14px; margin-bottom: 2px; }}
.profile-card .profile-meta {{ font-size: 12px; color: var(--text2); margin-bottom: 8px; }}
.profile-list {{ list-style: none; padding: 0; }}
.profile-list li {{ font-size: 12px; color: var(--text2); padding: 2px 0; padding-left: 14px; position: relative; }}
.profile-list li::before {{ content: ""; position: absolute; left: 0; top: 9px; width: 6px; height: 6px; border-radius: 50%; background: var(--accent-dark); }}

/* Theme badge */
.theme-badge {{ display: inline-block; font-size: 10px; color: rgba(255,255,255,0.4); font-family: var(--font-mono); margin-top: 8px; }}
.theme-badge .swatch {{ display: inline-block; width: 8px; height: 8px; border-radius: 2px; margin-right: 4px; vertical-align: middle; }}

/* Responsive */
@media (max-width: 768px) {{
  .cards {{ grid-template-columns: repeat(2, 1fr); }}
  .market-cards {{ grid-template-columns: 1fr; }}
  .panel {{ padding: 20px; }}
}}
</style>
</head>
<body>
<div class="container">

<!-- Header -->
<div class="header">
  <h1>{company_name}</h1>
  <div class="meta">
    <span>{company_industry}</span>
    <span>Project: {project_slug}</span>
    <span>Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}</span>
  </div>
  {f'<div class="desc">{escape_html(company_desc)}</div>' if company_desc else ''}
  <div class="theme-badge"><span class="swatch" style="background:var(--accent)"></span>Theme: {escape_html(theme["name"])}</div>
</div>

<!-- Phase Progress -->
<div class="phase-bar">
  <h3>Workflow Progress</h3>
  <div class="phase-steps">
"""
    for i, p in enumerate(phases):
        cls = "done" if i < phase_idx else ("current" if i == phase_idx else "")
        html += f'    <div class="phase-step {cls}" title="{p}"></div>\n'

    html += f"""  </div>
  <div class="phase-label">
    Phase: {phase.title()} <span class="tag">{phase_pct}%</span>
  </div>
</div>

<!-- Entity Counts -->
<div class="section">
  <div class="section-title">Entity Overview</div>
  <div class="cards">
"""

    entity_cards = [
        ("Products", counts.get("products", 0), None, None),
        ("Features", counts.get("features", 0), None, None),
        ("Markets", counts.get("markets", 0), None, None),
        ("Propositions", counts.get("propositions", 0), counts.get("expected_propositions", 0), completion.get("propositions_pct", 0)),
        ("Solutions", counts.get("solutions", 0), counts.get("propositions", 0), completion.get("solutions_pct", 0)),
        ("Competitors", counts.get("competitors", 0), counts.get("propositions", 0), completion.get("competitors_pct", 0)),
        ("Customers", counts.get("customers", 0), counts.get("markets", 0), completion.get("customers_pct", 0)),
    ]

    for label, val, expected, pct in entity_cards:
        sub = f"of {expected}" if expected is not None else ""
        bar_html = ""
        if pct is not None:
            color = "var(--green)" if pct >= 100 else ("var(--yellow)" if pct >= 50 else "var(--red)")
            bar_html = f'<div class="bar"><div class="fill" style="width:{min(pct,100)}%;background:{color}"></div></div>'
        html += f"""    <div class="card">
      <div class="label">{label}</div>
      <div class="value">{val}</div>
      {f'<div class="sub">{sub} ({pct}%)</div>' if pct is not None else ''}
      {bar_html}
    </div>
"""

    html += """  </div>
</div>
"""

    # --- Feature x Market Matrix ---
    if feature_slugs and market_slugs:
        html += """
<!-- Feature x Market Matrix -->
<div class="section">
  <div class="section-title">Feature x Market Matrix</div>
  <div class="matrix-wrap">
    <table class="matrix">
      <thead><tr><th class="corner"></th>
"""
        for ms in market_slugs:
            m = data["markets"][ms]
            html += f'        <th title="{escape_html(m.get("name", ms))}">{escape_html(ms)}</th>\n'
        html += "      </tr></thead>\n      <tbody>\n"

        for fs in feature_slugs:
            f = data["features"][fs]
            html += f'      <tr><td class="feature-label" title="{escape_html(f.get("description", ""))}">{escape_html(f.get("name", fs))}</td>\n'
            for ms in market_slugs:
                pair = f"{fs}--{ms}"
                has_prop = pair in data["propositions"]
                has_sol = pair in data["solutions"]
                if has_prop and has_sol:
                    cls = "full"
                    icon = "&#10003;"
                elif has_prop:
                    cls = "partial"
                    icon = "&#9679;"
                else:
                    cls = "missing"
                    icon = "&#10005;"
                html += f'        <td><button class="cell {cls}" onclick="openProposition(\'{escape_js_string(pair)}\')" title="{escape_html(pair)}">{icon}</button></td>\n'
            html += "      </tr>\n"
        html += "      </tbody>\n    </table>\n  </div>\n"
        html += '  <div style="font-size:12px;color:var(--text2);display:flex;gap:16px;margin-top:4px">'
        html += '<span><span style="color:var(--green)">&#9632;</span> Proposition + Solution</span>'
        html += '<span><span style="color:var(--yellow)">&#9632;</span> Proposition only</span>'
        html += '<span><span style="color:var(--red)">&#9632;</span> Missing</span>'
        html += '</div>\n</div>\n'

    # --- Markets Overview ---
    if data["markets"]:
        html += """
<!-- Markets Overview -->
<div class="section">
  <div class="section-title">Markets</div>
  <div class="market-cards">
"""
        max_tam = max(
            (m.get("tam", {}).get("value", 0) or 0 for m in data["markets"].values()),
            default=1
        ) or 1

        for ms, m in sorted(data["markets"].items()):
            region = escape_html(m.get("region", "?"))
            name = escape_html(m.get("name", ms))
            desc = escape_html(m.get("description", ""))
            tam = m.get("tam", {})
            sam = m.get("sam", {})
            som = m.get("som", {})
            tam_val = tam.get("value") or 0
            sam_val = sam.get("value") or 0
            som_val = som.get("value") or 0
            currency = tam.get("currency") or sam.get("currency") or som.get("currency") or "EUR"
            tam_pct = (tam_val / max_tam * 100) if max_tam else 0
            sam_pct = (sam_val / max_tam * 100) if max_tam else 0
            som_pct = (som_val / max_tam * 100) if max_tam else 0

            html += f"""    <div class="market-card" onclick="openMarket('{escape_js_string(ms)}')">
      <div class="region-badge">{region}</div>
      <h4>{name}</h4>
      <div class="desc">{desc}</div>
      <div class="sizing-bars">
        <div class="sizing-row"><span class="sizing-label">TAM</span><div class="sizing-bar"><div class="fill" style="width:{tam_pct:.0f}%;background:var(--blue)"></div></div><span class="sizing-val">{format_currency(tam_val, currency)}</span></div>
        <div class="sizing-row"><span class="sizing-label">SAM</span><div class="sizing-bar"><div class="fill" style="width:{sam_pct:.0f}%;background:var(--accent-dark)"></div></div><span class="sizing-val">{format_currency(sam_val, currency)}</span></div>
        <div class="sizing-row"><span class="sizing-label">SOM</span><div class="sizing-bar"><div class="fill" style="width:{som_pct:.0f}%;background:var(--green)"></div></div><span class="sizing-val">{format_currency(som_val, currency)}</span></div>
      </div>
    </div>
"""
        html += "  </div>\n</div>\n"

    # --- Products & Features ---
    if data["products"]:
        html += """
<!-- Products & Features -->
<div class="section">
  <div class="section-title">Products & Features</div>
"""
        for ps, p in sorted(data["products"].items()):
            pname = escape_html(p.get("name", ps))
            maturity = escape_html(p.get("maturity", ""))
            positioning = escape_html(p.get("positioning", ""))
            product_features = {fs: f for fs, f in data["features"].items() if f.get("product_slug") == ps}
            fcount = len(product_features)

            html += f"""  <div class="product-group">
    <div class="product-header" onclick="this.nextElementSibling.style.display=this.nextElementSibling.style.display==='none'?'block':'none'">
      <h4>{pname} {f'<span style="font-size:12px;color:var(--text2);font-weight:400;margin-left:8px">{maturity}</span>' if maturity else ''}</h4>
      <span class="badge">{fcount} feature{"s" if fcount != 1 else ""}</span>
    </div>
    <div class="product-features">
      {f'<div style="font-size:13px;color:var(--text2);margin-bottom:8px">{positioning}</div>' if positioning else ''}
"""
            for fs, f in sorted(product_features.items()):
                fname = escape_html(f.get("name", fs))
                fdesc = escape_html(f.get("description", ""))
                html += f'      <div class="feature-item"><span class="fname">{fname}</span><br><span class="fdesc">{fdesc}</span></div>\n'
            html += "    </div>\n  </div>\n"
        html += "</div>\n"

    # --- Solutions & Pricing ---
    if data["solutions"]:
        html += """
<!-- Solutions & Pricing -->
<div class="section">
  <div class="section-title">Solutions & Pricing</div>
  <div style="overflow-x:auto">
    <table class="solutions-table">
      <thead><tr><th>Proposition</th><th>Phases</th><th>Duration</th><th>PoV</th><th>Small</th><th>Medium</th><th>Large</th></tr></thead>
      <tbody>
"""
        for ss, s_ent in sorted(data["solutions"].items()):
            impl = s_ent.get("implementation", [])
            pricing = s_ent.get("pricing", {})
            total_weeks = sum(ph.get("duration_weeks", 0) for ph in impl)
            phase_names = " → ".join(ph.get("phase", "?") for ph in impl)

            def tier_str(tier_key, pr=pricing):
                t = pr.get(tier_key, {})
                if not t:
                    return "—"
                return format_currency(t.get("price"), t.get("currency", "EUR"))

            html += f"""        <tr style="cursor:pointer" onclick="openProposition('{escape_js_string(ss)}')">
          <td style="font-weight:500">{escape_html(ss)}</td>
          <td style="font-size:12px;color:var(--text2)">{escape_html(phase_names)}</td>
          <td class="mono">{total_weeks}w</td>
          <td class="price">{tier_str("proof_of_value")}</td>
          <td class="price">{tier_str("small")}</td>
          <td class="price">{tier_str("medium")}</td>
          <td class="price">{tier_str("large")}</td>
        </tr>
"""
        html += "      </tbody>\n    </table>\n  </div>\n</div>\n"

    # --- Claims Status ---
    claims_total = claims_status.get("total", 0)
    if claims_total > 0:
        verified = claims_status.get("verified", 0)
        resolved = claims_status.get("resolved", 0)
        unverified = claims_status.get("unverified", 0)
        deviated = claims_status.get("deviated", 0)
        unavailable = claims_status.get("source_unavailable", 0)
        clean = verified + resolved
        clean_pct = int(clean / claims_total * 100) if claims_total else 0

        html += f"""
<!-- Claims Status -->
<div class="section">
  <div class="section-title">Claims Verification</div>
  <div style="margin-bottom:12px">
    <div class="bar" style="height:8px;width:100%;max-width:500px">
      <div class="fill" style="width:{clean_pct}%;background:var(--green)"></div>
    </div>
    <div style="font-size:13px;color:var(--text2);margin-top:4px">{clean} of {claims_total} claims verified ({clean_pct}%)</div>
  </div>
  <div class="claims-summary">
    <span class="claims-chip" style="background:rgba(46,125,50,0.1);color:var(--green)">Verified: {verified}</span>
    <span class="claims-chip" style="background:rgba(46,125,50,0.06);color:var(--green)">Resolved: {resolved}</span>
    <span class="claims-chip" style="background:rgba(229,161,0,0.1);color:var(--yellow)">Unverified: {unverified}</span>
    <span class="claims-chip" style="background:rgba(211,47,47,0.1);color:var(--red)">Deviated: {deviated}</span>
    <span class="claims-chip" style="background:rgba(107,114,128,0.1);color:var(--text2)">Unavailable: {unavailable}</span>
  </div>
</div>
"""

    # --- Next Actions ---
    if next_actions:
        html += """
<!-- Next Actions -->
<div class="section">
  <div class="section-title">Recommended Next Actions</div>
"""
        for action in next_actions:
            skill = escape_html(action.get("skill", ""))
            reason = escape_html(action.get("reason", ""))
            html += f"""  <div class="action-item">
    <span class="action-skill">{skill}</span>
    <span class="action-reason">{reason}</span>
  </div>
"""
        html += "</div>\n"

    # --- Detail Panel (Modal) + JS ---
    html += f"""
<!-- Detail Panel -->
<div class="overlay" id="overlay" onclick="if(event.target===this)closePanel()">
  <div class="panel" id="panel"></div>
</div>

<script>
const E = {entities_json};

function closePanel() {{
  document.getElementById('overlay').classList.remove('open');
}}

document.addEventListener('keydown', e => {{ if(e.key==='Escape') closePanel(); }});

function openProposition(slug) {{
  const p = E.propositions[slug];
  const s = E.solutions[slug];
  const c = E.competitors[slug];
  const parts = slug.split('--');
  const fSlug = parts[0];
  const mSlug = parts.slice(1).join('--');
  const f = E.features[fSlug] || {{}};
  const m = E.markets[mSlug] || {{}};

  let html = '<button class="panel-close" onclick="closePanel()">&times;</button>';
  html += '<h3>' + esc(f.name || fSlug) + ' &rarr; ' + esc(m.name || mSlug) + '</h3>';
  html += '<div class="panel-sub">' + esc(slug) + '</div>';

  if (p) {{
    html += '<div class="section-label">IS (What it is)</div><div class="stmt">' + esc(p.is_statement || '') + '</div>';
    html += '<div class="section-label">DOES (What it does)</div><div class="stmt">' + esc(p.does_statement || '') + '</div>';
    html += '<div class="section-label">MEANS (What it means)</div><div class="stmt">' + esc(p.means_statement || '') + '</div>';

    if (p.evidence && p.evidence.length) {{
      html += '<div class="section-label">Evidence</div>';
      p.evidence.forEach(e => {{
        html += '<div style="font-size:13px;color:var(--text2);margin-bottom:4px">&bull; ' + esc(e.statement || '');
        if (e.source_url) html += ' <a href="' + esc(e.source_url) + '" target="_blank" style="color:var(--accent-dark)">[source]</a>';
        html += '</div>';
      }});
    }}
  }} else {{
    html += '<div style="color:var(--red);margin:16px 0">No proposition created yet for this Feature x Market pair.</div>';
  }}

  if (s) {{
    html += '<div class="section-label">Implementation</div>';
    html += '<table><thead><tr><th>Phase</th><th>Duration</th><th>Description</th></tr></thead><tbody>';
    (s.implementation || []).forEach(ph => {{
      html += '<tr><td style="font-weight:500">' + esc(ph.phase) + '</td><td class="mono">' + ph.duration_weeks + 'w</td><td style="color:var(--text2)">' + esc(ph.description) + '</td></tr>';
    }});
    html += '</tbody></table>';

    html += '<div class="section-label">Pricing</div>';
    html += '<table><thead><tr><th>Tier</th><th>Price</th><th>Scope</th></tr></thead><tbody>';
    ['proof_of_value','small','medium','large'].forEach(tier => {{
      const t = (s.pricing || {{}})[tier];
      if (t) {{
        const label = tier === 'proof_of_value' ? 'Proof of Value' : tier.charAt(0).toUpperCase() + tier.slice(1);
        html += '<tr><td style="font-weight:500">' + label + '</td><td class="price">' + fmtCurrency(t.price, t.currency) + '</td><td style="color:var(--text2)">' + esc(t.scope) + '</td></tr>';
      }}
    }});
    html += '</tbody></table>';
  }}

  if (c && c.competitors && c.competitors.length) {{
    html += '<div class="section-label">Competitors</div>';
    c.competitors.forEach(comp => {{
      html += '<div class="competitor-card">';
      html += '<h5>' + esc(comp.name) + '</h5>';
      if (comp.positioning) html += '<div class="comp-detail">' + esc(comp.positioning) + '</div>';
      if (comp.differentiation) html += '<div class="comp-detail" style="color:var(--accent-dark);margin-top:4px">' + esc(comp.differentiation) + '</div>';
      html += '<div class="comp-pills">';
      (comp.strengths || []).forEach(s => {{ html += '<span class="comp-pill strength">' + esc(s) + '</span>'; }});
      (comp.weaknesses || []).forEach(w => {{ html += '<span class="comp-pill weakness">' + esc(w) + '</span>'; }});
      html += '</div></div>';
    }});
  }}

  document.getElementById('panel').innerHTML = html;
  document.getElementById('overlay').classList.add('open');
}}

function openMarket(slug) {{
  const m = E.markets[slug];
  if (!m) return;
  const cust = E.customers[slug];

  let html = '<button class="panel-close" onclick="closePanel()">&times;</button>';
  html += '<h3>' + esc(m.name || slug) + '</h3>';
  html += '<div class="panel-sub">' + esc(m.region || '') + ' &bull; ' + esc(slug) + '</div>';
  html += '<div class="stmt">' + esc(m.description || '') + '</div>';

  if (m.segmentation) {{
    html += '<div class="section-label">Segmentation</div>';
    html += '<table><tbody>';
    Object.entries(m.segmentation).forEach(([k,v]) => {{
      html += '<tr><td style="color:var(--text2)">' + esc(k) + '</td><td>' + esc(v) + '</td></tr>';
    }});
    html += '</tbody></table>';
  }}

  html += '<div class="section-label">Market Sizing</div>';
  html += '<table><thead><tr><th>Metric</th><th>Value</th><th>Source</th></tr></thead><tbody>';
  ['tam','sam','som'].forEach(key => {{
    const d = m[key];
    if (d) {{
      html += '<tr><td style="font-weight:500">' + key.toUpperCase() + '</td><td class="price">' + fmtCurrency(d.value, d.currency) + '</td><td style="color:var(--text2);font-size:12px">' + esc(d.source || d.description || '') + '</td></tr>';
    }}
  }});
  html += '</tbody></table>';

  if (cust && cust.profiles && cust.profiles.length) {{
    html += '<div class="section-label">Customer Profiles</div>';
    cust.profiles.forEach(prof => {{
      html += '<div class="profile-card">';
      html += '<h5>' + esc(prof.role || '') + '</h5>';
      html += '<div class="profile-meta">' + esc(prof.seniority || '') + (prof.decision_role ? ' &bull; ' + esc(prof.decision_role) : '') + '</div>';
      if (prof.pain_points && prof.pain_points.length) {{
        html += '<div style="font-size:12px;color:var(--text2);margin-bottom:2px">Pain Points</div><ul class="profile-list">';
        prof.pain_points.forEach(pp => {{ html += '<li>' + esc(pp) + '</li>'; }});
        html += '</ul>';
      }}
      if (prof.buying_criteria && prof.buying_criteria.length) {{
        html += '<div style="font-size:12px;color:var(--text2);margin-top:6px;margin-bottom:2px">Buying Criteria</div><ul class="profile-list">';
        prof.buying_criteria.forEach(bc => {{ html += '<li>' + esc(bc) + '</li>'; }});
        html += '</ul>';
      }}
      html += '</div>';
    }});
  }}

  const props = Object.entries(E.propositions).filter(([k,v]) => v.market_slug === slug);
  if (props.length) {{
    html += '<div class="section-label">Propositions (' + props.length + ')</div>';
    props.forEach(([k,v]) => {{
      const feat = E.features[v.feature_slug] || {{}};
      html += '<div style="background:var(--surface);border-radius:8px;padding:12px 16px;margin-bottom:8px;cursor:pointer" onclick="openProposition(\\''+k+'\\')"><h5>' + esc(feat.name || v.feature_slug) + '</h5>';
      html += '<div style="font-size:12px;color:var(--text2)">' + esc(v.does_statement || '').substring(0,120) + '...</div></div>';
    }});
  }}

  document.getElementById('panel').innerHTML = html;
  document.getElementById('overlay').classList.add('open');
}}

function esc(s) {{
  if (s == null) return '';
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}}

function fmtCurrency(val, cur) {{
  cur = cur || 'EUR';
  if (val == null) return 'N/A';
  if (val >= 1e9) return cur + ' ' + (val/1e9).toFixed(1) + 'B';
  if (val >= 1e6) return cur + ' ' + (val/1e6).toFixed(1) + 'M';
  if (val >= 1e3) return cur + ' ' + (val/1e3).toFixed(0) + 'K';
  return cur + ' ' + val.toLocaleString();
}}
</script>

</div>
</body>
</html>"""
    return html


def find_default_theme():
    """Look for cogni-work theme in standard cogni-workspace locations."""
    candidates = [
        os.path.expanduser("~/.claude/plugins/marketplaces/cogni-works/cogni-workspace/themes/cogni-work/theme.md"),
        os.path.expanduser("~/.claude/plugins/cache/cogni-works/cogni-workspace/*/themes/cogni-work/theme.md"),
    ]
    for pattern in candidates:
        matches = glob.glob(pattern)
        if matches:
            return matches[0]
    return None


def main():
    # Parse args
    args = sys.argv[1:]
    project_dir = None
    theme_path = None

    i = 0
    while i < len(args):
        if args[i] == "--theme" and i + 1 < len(args):
            theme_path = args[i + 1]
            i += 2
        elif not project_dir:
            project_dir = args[i]
            i += 1
        else:
            i += 1

    if not project_dir:
        print(json.dumps({"error": "Usage: generate-dashboard.py <project-dir> [--theme <theme.md>]"}))
        sys.exit(1)

    project_dir = os.path.abspath(project_dir)
    if not os.path.isfile(os.path.join(project_dir, "portfolio.json")):
        print(json.dumps({"error": f"Not a cogni-portfolio project (missing portfolio.json): {project_dir}"}))
        sys.exit(1)

    # Load theme
    if not theme_path:
        theme_path = find_default_theme()
    theme = parse_theme(theme_path)

    data = load_all_entities(project_dir)
    status = get_status(project_dir)
    html = generate_html(data, status, project_dir, theme)

    output_dir = os.path.join(project_dir, "output")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "dashboard.html")

    with open(output_path, "w") as f:
        f.write(html)

    print(json.dumps({"status": "ok", "path": output_path, "theme": theme["name"]}))


if __name__ == "__main__":
    main()
