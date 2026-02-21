# check-citations

A shared Claude Code skill that extracts citations and references from documents, verifies their validity, flags unverifiable sources, recommends alternatives, and highlights body text that may need adjusting.

## What it does

Given a document, the skill will:

1. **Extract** all citations — inline URLs, footnotes, DOIs, APA/MLA/Chicago bibliography entries
2. **Verify** each source exists and is accessible via HTTP
3. **Check content match** — fetch the source and confirm it actually supports the claimed fact
4. **Flag unverifiable** sources (paywalled, dead links, ambiguous references) with reason codes
5. **Recommend alternatives** via web search for broken or inaccessible sources
6. **Suggest body text adjustments** where a source contradicts or doesn't support the claim

## Output

Always produces two files:

- **`citations_report.json`** — machine-readable, structured report for programmatic use
- **`citations_report.md`** — human-readable summary with Verified / Failed / Unverifiable sections

## Supported document types

| Format | Support |
|--------|---------|
| Markdown / plain text | ✅ |
| DOCX / Word | ✅ via python-docx |
| PDF | ✅ via pdfplumber (text-only; no OCR) |

## Citation styles

LLM-based extraction handles all styles without configuration:
- Inline hyperlinks and bare URLs
- DOI references (`doi:10.XXXX/...`)
- APA, MLA, Chicago bibliography entries
- Numbered footnotes and endnotes (`[1]`, `[^1]`)
- Author-year inline citations matched to bibliography

## Usage

This is a **Claude Code skill**. Once deployed, invoke it from any Claude Code session:

```
/check-citations path/to/document.md
/check-citations path/to/report.pdf depth=existence
/check-citations path/to/paper.docx depth=content outdir=/tmp/citations/
```

**Parameters:**

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `depth` | `existence` \| `content` | `content` | Existence-only is faster; content checks that the source supports the claim |
| `outdir` | any path | document directory | Where to write the two report files |

### Calling from other projects

The skill is designed as a shared utility. Other Claude Code agents and skills can invoke it via the `Skill` tool:

```python
# In a Claude Code skill or agent prompt:
Use the check-citations skill with args="path/to/document.md depth=content outdir=/tmp/"
```

The JSON output has a stable schema safe to parse programmatically.

## JSON schema

```json
{
  "document": "path/to/doc.md",
  "generated_at": "2026-02-21T12:00:00Z",
  "summary": {
    "total": 12,
    "verified": 8,
    "failed": 2,
    "unverifiable": 2
  },
  "citations": [
    {
      "id": 1,
      "raw_text": "https://example.com/source",
      "type": "url",
      "claimed_in": "The sentence making the claim [1].",
      "resolved_url": "https://example.com/source",
      "status": "verified",
      "content_match": true,
      "confidence": 0.92,
      "discrepancies": [],
      "alternative": null,
      "body_text_adjustment": null
    }
  ]
}
```

**Status values:** `verified` | `failed` | `unverifiable` | `redirected`
**Type values:** `url` | `doi` | `apa` | `mla` | `chicago` | `bare_ref` | `footnote`

## Installation

### Requirements

- Python 3.11+
- Claude Code CLI

```bash
git clone git@github.com:tlarcombe/check_citations.git
cd check_citations
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
make deploy
```

`make deploy` copies the skill files to `~/.claude/skills/check-citations/`, making it available in all Claude Code sessions.

### Other Makefile targets

```bash
make test      # run the test suite
make undeploy  # remove the skill from ~/.claude/skills/
```

## Project structure

```
check_citations/
├── scripts/
│   ├── extract_text.py      # document → plain text (MD, DOCX, PDF)
│   ├── check_url.py         # URL existence checker, returns JSON
│   └── write_report.py      # writes citations_report.{json,md}
├── skill/
│   ├── SKILL.md             # Claude Code skill definition (8-phase workflow)
│   └── references/
│       ├── citation_schema.md
│       └── verification_workflow.md
├── tests/
│   ├── fixtures/
│   │   ├── sample_markdown.md
│   │   ├── sample.docx
│   │   └── create_fixtures.py
│   ├── test_extract_text.py
│   ├── test_check_url.py
│   └── test_write_report.py
├── Makefile
├── requirements.txt
└── pyproject.toml
```

## How it works

The skill is a **Claude Code prompt** (`skill/SKILL.md`) that orchestrates:

- Python helpers for I/O (document parsing, HTTP checking, report writing)
- Claude's built-in `WebFetch` for content matching
- Claude's built-in `WebSearch` for finding alternative sources
- Parallel subagents for concurrent citation verification (5+ citations)

Claude handles all LLM reasoning (citation extraction, claim-vs-source matching, alternative selection). Python handles file I/O and HTTP.

## Limitations (v1)

- PDF extraction is text-only — scanned PDFs require OCR pre-processing
- Academic references without embedded URLs (APA/MLA/Chicago) are marked `unverifiable` — no title-search verification in v1
- Script paths in the skill are hardcoded to the install location — re-run `make deploy` after moving the repo
- Confidence scores are LLM estimates; treat values below 0.7 as uncertain

## Licence

MIT
