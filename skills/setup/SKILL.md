---
name: setup
description: |
  This skill should be used when the user asks to "create a portfolio",
  "new portfolio project", "set up portfolio", "initialize portfolio",
  or "start portfolio planning". If a project already exists, redirect
  to the resume-portfolio skill instead. Initializes a cogni-portfolio project.
---

# Portfolio Project Setup

Initialize a cogni-portfolio project by capturing company context and creating the project directory structure.

## Workflow

### 1. Gather Company Context

Ask the user for four required fields:

- **Company name**: Legal or trading name
- **Description**: One-sentence summary of what the company does
- **Industry**: Primary industry sector (e.g., "Cloud Infrastructure", "B2B SaaS")
- **Products**: List of main products or services offered

If the user has provided some context already, extract what is available and ask only for missing fields.

### 2. Determine Project Slug

Derive a project slug from the company name:
- Convert to kebab-case
- Keep it short and recognizable (e.g., "Acme Cloud Services" -> `acme-cloud`)
- Confirm the slug with the user

### 3. Create Project Structure

Run the init script to create the directory structure:

```bash
bash $CLAUDE_PLUGIN_ROOT/scripts/project-init.sh "<workspace-dir>" "<project-slug>"
```

The workspace directory is the user's current working directory. The script creates:

```
cogni-portfolio/<project-slug>/
  products/
  features/
  markets/
  propositions/
  competitors/
  customers/
  uploads/
  output/
```

### 4. Write portfolio.json

After the script creates directories, write `portfolio.json` in the project root with the company context gathered in step 1. Follow the schema in `$CLAUDE_PLUGIN_ROOT/skills/setup/references/data-model.md`.

### 5. Confirm and Guide Next Steps

Present the created project structure and suggest the full workflow. If the user has existing documents (product specs, market research, pitch decks, etc.), mention they can drop files into the `uploads/` folder and run the `ingest` skill to import data automatically.

1. (Optional) Drop existing documents into `uploads/` and run the `ingest` skill
2. Define products with the `products` skill
3. Add features to each product with the `features` skill
4. Discover target markets with the `markets` skill
5. Generate proposition messaging with the `propositions` skill
6. Enrich with `compete` (competitor analysis) and `customers` (buyer profiles)
7. Verify web-sourced claims with the `verify` skill
8. Aggregate into messaging repository with the `synthesize` skill
9. Generate deliverables with the `export` skill

## Data Model Overview

The portfolio data model has six entity types:

| Entity | Storage | Key Concept |
|---|---|---|
| Product | `products/{slug}.json` | Named offering that bundles features |
| Feature (IS) | `features/{slug}.json` | Market-independent capability (belongs to a product) |
| Market | `markets/{slug}.json` | Target segment with TAM/SAM/SOM |
| Proposition | `propositions/{feat}--{mkt}.json` | Feature x Market = DOES + MEANS |
| Competitor | `competitors/{feat}--{mkt}.json` | Per-proposition competitive landscape |
| Customer | `customers/{mkt}.json` | Per-market ideal buyer profile |
| Claims | `.claims/claims.json` | Web-sourced claim verification registry |

For complete entity schemas and naming conventions, consult `$CLAUDE_PLUGIN_ROOT/skills/setup/references/data-model.md`.

## Important Notes

- Each project lives under `cogni-portfolio/<slug>/` in the workspace
- Multiple projects are supported (one per company or product line)
- If a project already exists, the init script returns `"status": "exists"` without overwriting
- The `updated` field in portfolio.json should be refreshed whenever entities change
