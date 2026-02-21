---
name: check-citations
description: "Extracts citations from a document (markdown, PDF, DOCX), verifies their existence and content match, recommends alternatives for broken sources, and outputs JSON + markdown reports. Call with a document path and optional depth (existence|content). Returns paths to both report files."
---

# check-citations

Verify all citations and references in a document. Produce a structured JSON report and a human-readable markdown summary.

## Invocation

```
/check-citations <document_path> [depth=existence|content] [outdir=./]
```

- `document_path`: absolute or relative path to the document
- `depth`: `existence` (URL alive?) or `content` (URL alive + claim supported?) — default: `content`
- `outdir`: where to write the two report files — default: same directory as document

## Workflow

### Step 1 — Extract text

Run the text extractor:

```bash
python /home/tlarcombe/projects/check_citations/scripts/extract_text.py "<document_path>"
```

If the file is markdown or plain text, you may read it directly instead.

### Step 2 — Identify citations

Carefully read the extracted text. Find ALL citations and references:

- Inline hyperlinks: `[text](url)` or bare URLs
- Footnote markers: `[1]`, `[^1]`, `*` etc.
- Author-year inline: `(Smith, 2023)` or `[Smith 2023]`
- DOI references: `doi:10.XXXX/...`
- Bibliography / References section entries (APA, MLA, Chicago)

Build a preliminary list. Each entry: id, raw_text, type, claimed_in (the sentence containing the citation).

For bare references like `[1]`, find the matching entry in the bibliography.

### Step 3 — Resolve to URLs

For each citation:
- `url` type → use as-is
- `doi` type → `https://doi.org/<id>`
- Academic entries (apa/mla/chicago) → note as `unverifiable` unless a URL is embedded
- Unresolvable bare refs with no matching bibliography → note as `unverifiable`

### Step 4 — Check existence (all citations with a URL)

For each URL, run:

```bash
python /home/tlarcombe/projects/check_citations/scripts/check_url.py "<url>"
```

Record: accessible, status_code, final_url, error.

**Dispatch in parallel using the dispatching-parallel-agents pattern when there are 5+ citations.**

Set status:
- accessible=true, status_code<400 → `verified` (provisional) or `redirected` (if final_url differs from original)
- accessible=false → `failed`

### Step 5 — Check content match (if depth=content)

For each citation with status=`verified` or `redirected`:

1. Use WebFetch to retrieve the page at `final_url`
2. Identify the specific claim in `claimed_in`
3. Search the fetched content for evidence supporting (or contradicting) that claim
4. Set `content_match: true|false` and `confidence: 0.0-1.0`
5. List any `discrepancies`
6. If content contradicts the claim, draft a `body_text_adjustment`

If WebFetch fails (paywall, JS-only): set status=`unverifiable`, content_match=null.

### Step 6 — Find alternatives (for failed citations)

For each citation with status=`failed`:

Use WebSearch with query: key entities from `claimed_in` + the topic of the original source.

Prefer: Wikipedia, gov sites, established publications, academic sources.

Record the best match as `alternative: {url, title, confidence}`.

### Step 7 — Build report and write files

Construct the report dict:

```json
{
  "document": "<document_path>",
  "generated_at": "<ISO8601 timestamp>",
  "summary": {
    "total": 0,
    "verified": 0,
    "failed": 0,
    "unverifiable": 0
  },
  "citations": []
}
```

Write to a temp JSON file, then run:

```bash
python /home/tlarcombe/projects/check_citations/scripts/write_report.py /tmp/check_citations_report.json "<outdir>"
```

### Step 8 — Return to caller

Output:
1. The paths to both report files (JSON and markdown)
2. A brief summary: N citations found, N verified, N failed, N unverifiable
3. Any critical issues (claims that are factually contradicted by their own sources)

## Schema reference

See `/home/tlarcombe/projects/check_citations/skill/references/citation_schema.md`

## Notes for callers

- The JSON report is machine-readable and safe to parse programmatically
- Confidence scores are LLM estimates — treat <0.7 as uncertain
- `unverifiable` does not mean wrong — it means the source cannot be fetched, not that the claim is false
- For paywalled academic papers: flag as unverifiable, suggest open-access alternative if possible (arXiv, PubMed, OpenAlex)
