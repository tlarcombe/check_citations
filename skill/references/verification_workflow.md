# Verification Workflow

## Phase 1: Extract Citations

Use LLM reasoning on the document text. Produce a numbered list where each entry has:
- The exact raw text of the citation/reference
- The sentence it appears in (for context)
- Your best guess at the type (url, doi, apa, etc.)

Scan both inline citations and any bibliography/references section at the end.

## Phase 2: Resolve URLs

For each citation:
- **url type**: use the URL directly
- **doi type**: resolve to `https://doi.org/{doi_id}`
- **apa/mla/chicago type**: attempt to construct a search query — e.g. author + title + year
- **bare_ref**: match to bibliography entry at end of document
- **footnote**: match to footnote list

## Phase 3: Check Existence (via Python helper)

Run: `python /home/tlarcombe/projects/check_citations/scripts/check_url.py <url>`

Returns JSON: `{"accessible": true|false, "status_code": 200, "final_url": "...", "error": null}`

## Phase 4: Content Match (depth=content only)

If accessible, use WebFetch to retrieve the page content, then:
1. Identify the specific claim being made in the body text
2. Search the fetched content for supporting evidence
3. Assign content_match: true/false and confidence 0.0-1.0
4. Note any specific factual discrepancies

Signs of content mismatch:
- Claimed statistic differs from source
- Source says the opposite of what is claimed
- Source does not mention the topic at all
- Source is from a different context (e.g., claim is about UK, source is about USA)

## Phase 5: Find Alternatives (for failed citations)

For citations with status=failed, use WebSearch to find a replacement source:
- Search query: the claim text + key entities
- Prefer: authoritative sources (gov, edu, established publications)
- Exclude: the original (broken) domain

## Phase 6: Write Report

Run: `python /home/tlarcombe/projects/check_citations/scripts/write_report.py <report_json_path> <outdir>`

Or construct the JSON in memory and pass to the Python helper.
