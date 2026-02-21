# check_citations

## Project Purpose

A shared citation-checking utility, callable from other projects and skills. Identifies citations and references in a document, verifies their existence and content, flags unverifiable sources, recommends alternatives, and highlights body text that may need adjusting.

## Architecture Decision

**Form**: Claude Code skill (`~/.claude/skills/check-citations`) backed by code in this repo.

**Invocation pattern**: Other projects call this via the `Skill` tool or reference it in their prompts. Stable input/output API so any project in the ecosystem can use it without modification.

**Parallelisation**: The skill orchestrates subagents — one per citation (or batched) — for concurrent web fetching and content matching. Uses `dispatching-parallel-agents` pattern.

## Core Capabilities

1. **Citation extraction** — LLM-based parsing of documents to identify all references (inline URLs, footnotes, APA/MLA/Chicago bibliographies, DOIs, bare hyperlinks)
2. **Existence check** — HTTP fetch / Playwright to verify source resolves and is accessible
3. **Content match** — Fetch source content, use LLM to verify the cited claim is actually supported
4. **Unverifiable flagging** — Mark paywalled, dead, or ambiguous sources with reason codes
5. **Alternative sourcing** — Web search fallback to find live replacement sources
6. **Fact adjustment recommendations** — Flag body text that conflicts with or is not supported by the verified source

## Input

- Document content (string) or file path
- Document type hint: `markdown` | `pdf` | `docx` | `text` (auto-detected if not provided)
- Verification depth: `existence` | `content` | `full` (default: `content`)
- Optional: specific citation range, skip list

## Output

Dual output — always produced together:

1. **`citations_report.json`** — machine-readable, structured:
   ```json
   {
     "summary": { "total": 12, "verified": 8, "failed": 2, "unverifiable": 2 },
     "citations": [
       {
         "id": 1,
         "raw_text": "...",
         "type": "url|doi|apa|mla|bare_link",
         "resolved_url": "...",
         "status": "verified|failed|unverifiable|redirected",
         "content_match": true|false|null,
         "confidence": 0.85,
         "discrepancies": ["..."],
         "alternative": { "url": "...", "title": "...", "confidence": 0.9 },
         "body_text_adjustment": "..."
       }
     ]
   }
   ```

2. **`citations_report.md`** — human-readable summary with sections: Verified, Failed, Unverifiable, Recommendations

## Verification Strategy

- **Primary**: Direct web fetch (HTTP or Playwright for JS-heavy pages)
- **Fallback**: Web search to find alternative sources when primary fails
- **Academic**: DOI resolution via standard HTTP redirect (no API key required)
- **Not in scope (v1)**: Crossref, Semantic Scholar, OpenAlex APIs

## Document Types Supported

- Markdown / plain text (v1)
- PDF (v1, via text extraction)
- DOCX / Word (v1, via python-docx)

## Citation Styles Supported

All of the below — extraction is LLM-based so style-agnostic:
- Inline URLs / hyperlinks
- APA / MLA / Chicago bibliography entries
- DOI references
- Numbered footnotes / endnotes
- Author-year inline citations matched to bibliography

## Project Location

`/home/tlarcombe/projects/check_citations/`

Skill deployed to: `~/.claude/skills/check-citations`

## Implementation Status (v1 complete)

- [x] Architecture decision: Claude Code skill + Python helpers
- [x] `scripts/extract_text.py` — markdown, txt, DOCX, PDF
- [x] `scripts/check_url.py` — HTTP existence check, redirect following, timeout handling
- [x] `scripts/write_report.py` — JSON + markdown dual output
- [x] `skill/SKILL.md` — 8-phase workflow prompt deployed to `~/.claude/skills/check-citations/`
- [x] `Makefile` — `make deploy` / `make undeploy` / `make test`
- [x] 18 tests passing

## Running

```bash
# Run tests
make test          # or: .venv/bin/pytest tests/ -v

# Deploy skill after changes
make deploy

# Use from another Claude Code session
/check-citations path/to/document.md depth=content outdir=/tmp/
```

## Known Limitations (v1)

- Python packages in `.venv/` — use `.venv/bin/python`, not system `python3`
- PDF extraction via pdfplumber — text only, no OCR for scanned PDFs
- Academic refs (APA/MLA) without embedded URLs marked `unverifiable`
- Script paths in SKILL.md are hardcoded to `/home/tlarcombe/projects/check_citations/`

## Related Projects

- `fact-or-fiction` — empty directory, nothing to reuse
- `report_generator` — likely primary consumer of this utility
- `website_orchestrator` — potential consumer

## Development Notes

- Use `writing-plans` before touching code
- Use `dispatching-parallel-agents` pattern for concurrent citation verification
- Use `brainstorming` before designing any new feature
- Test with a real document containing known-broken and known-good citations
