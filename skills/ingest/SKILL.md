---
name: ingest
description: |
  This skill should be used when the user asks to "ingest uploads",
  "process uploads", "import uploaded files", "import documents",
  "ingest files", "process uploaded documents", or "import existing data".
  Extracts portfolio entities from documents in the uploads folder.
---

# Upload Ingestion

Extract portfolio entities from user-provided documents in the project's `uploads/` folder. Supported file types: `.md`, `.docx`, `.pptx`, `.xlsx`, `.pdf`.

## Prerequisites

- An active cogni-portfolio project (portfolio.json must exist)
- One or more supported files in the project's `uploads/` directory
- The `document-skills` plugin for non-markdown file extraction (docx, pptx, xlsx, pdf)

## Workflow

### 1. Locate Project and Scan Uploads

Find the active portfolio project using the same approach as the `resume-portfolio` skill:

```bash
find . -maxdepth 3 -name "portfolio.json" -path "*/cogni-portfolio/*"
```

If multiple projects exist, ask which one to use. Then scan the `uploads/` directory for supported files (exclude the `processed/` subdirectory):

```bash
find <project-dir>/uploads -maxdepth 1 -type f \( -name '*.md' -o -name '*.docx' -o -name '*.pptx' -o -name '*.xlsx' -o -name '*.pdf' \)
```

If no files are found, inform the user the uploads folder is empty and list the supported file types.

### 2. Check File Type Requirements

After scanning uploads, check file types. If non-markdown files are present (.docx, .pptx, .xlsx, .pdf), verify document-skills availability. If unavailable, inform the user which files cannot be processed, process only the .md files, and leave the binary files in uploads/ for later.

### 3. Extract Text Content

Process each file based on its type:

- **Markdown (.md)**: Read directly with the Read tool
- **Word (.docx)**: Use the `document-skills:docx` skill to extract text
- **PowerPoint (.pptx)**: Use the `document-skills:pptx` skill to extract slide content
- **Excel (.xlsx)**: Use the `document-skills:xlsx` skill to extract sheet data
- **PDF (.pdf)**: Use the `document-skills:pdf` skill to extract text

For each file, note the filename and extracted content for analysis.

For large documents (PDFs over 20 pages, Excel workbooks with many sheets), process in focused segments. For PDFs, use the `pages` parameter to read 10-20 pages at a time. For Excel, process one sheet at a time. Present extracted entities per segment so the user can confirm incrementally rather than reviewing dozens of entities at once.

### 4. Analyze and Classify Content

Read the existing `portfolio.json` to understand the company context. Then analyze extracted content against the portfolio data model to identify potential entities:

| Entity Type | What to Look For |
|---|---|
| Products | Named offerings, product lines, service packages |
| Features | Capabilities, specifications, functions, technical components |
| Markets | Target segments, customer groups, geographic regions, verticals |

Note any competitive intelligence or buyer persona data found in documents, but do not create competitor or customer entities during ingestion. These entity types require propositions or markets as parents and are handled by the `compete` and `customers` skills after the prerequisite entities exist.

Cross-reference with existing entities in the project to avoid duplicates. Read existing JSON files from `products/`, `features/`, and `markets/` directories to know what already exists.

### 5. Present Extracted Entities for Confirmation

Group extracted entities by type and present them in tables:

**From: `product-overview.pdf`**

| Type | Slug | Name | Key Fields |
|---|---|---|---|
| Product | cloud-platform | Cloud Platform | description, positioning |
| Feature | auto-scaling | Auto-Scaling | product: cloud-platform, category: infrastructure |
| Feature | monitoring | Real-Time Monitoring | product: cloud-platform, category: observability |

**From: `market-analysis.xlsx`**

| Type | Slug | Name | Key Fields |
|---|---|---|---|
| Market | mid-market-saas | Mid-Market SaaS | geography: DACH, TAM: 5B EUR |

For each entity, show enough detail for the user to judge accuracy. Mark entities that may overlap with existing ones.

Allow the user to:
- **Approve all** -- create all proposed entities
- **Select individually** -- approve, edit, or skip each entity
- **Edit before creating** -- modify fields before writing JSON

### 6. Write Entity JSON Files

For each confirmed entity, write a JSON file following the schemas in `$CLAUDE_PLUGIN_ROOT/skills/setup/references/data-model.md`:

- Products to `products/{slug}.json`
- Features to `features/{slug}.json`
- Markets to `markets/{slug}.json`

Set `created` to today's date. Include `"source_file": "<filename>"` in each entity JSON, where `<filename>` is the name of the source file in uploads/ (e.g., `"product-overview.md"`). This enables tracing entity origins.

For features, ensure `product_slug` references a valid product. If a referenced product does not exist, propose creating it first or ask the user to assign a different product.

### 7. Move Processed Files

After all confirmed entities are written, move processed files to `uploads/processed/`:

```bash
mkdir -p <project-dir>/uploads/processed
mv <project-dir>/uploads/<filename> <project-dir>/uploads/processed/
```

Only move files that were successfully processed. If a file yielded no usable entities (user skipped everything from it), still move it to avoid re-processing.

### 8. Present Summary and Next Steps

Show a summary of what was created:

| Type | Created | Skipped |
|---|---|---|
| Products | 2 | 0 |
| Features | 5 | 1 |
| Markets | 3 | 0 |

Suggest the logical next step based on what was ingested:
- If products and features were created, suggest the `markets` skill
- If markets were created, suggest the `propositions` skill
- If only partial data was ingested, suggest completing the entity type manually
- If competitive or buyer persona data was observed in documents, mention it and suggest running `compete` or `customers` after the prerequisite entities (propositions/markets) are in place

If any markets were created without TAM/SAM/SOM data, list them explicitly: "N market(s) created without sizing data: [slugs]. Run the `markets` skill to add TAM/SAM/SOM estimates."

## Important Notes

- Always confirm entities with the user before writing -- never auto-create
- Respect existing entities; do not overwrite files that already exist unless the user explicitly requests it
- One document may contain data for multiple entity types
- If a document is ambiguous, ask the user which entity types to extract
- Feature extraction should produce market-independent statements (IS layer only)
- Market data from documents may lack TAM/SAM/SOM; create the market entity with available fields and note that sizing can be added later via the `markets` skill
- The `uploads/processed/` subdirectory is not scanned by project-status.sh
