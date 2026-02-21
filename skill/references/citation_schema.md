# Citation JSON Schema

Each citation in the report follows this exact structure:

```json
{
  "id": 1,
  "raw_text": "the exact text as found in the document",
  "type": "url | doi | apa | mla | chicago | bare_ref | footnote",
  "claimed_in": "the sentence in the body that makes the claim citing this reference",
  "resolved_url": "the final URL (after redirects) or null",
  "status": "verified | failed | unverifiable | redirected",
  "content_match": true,
  "confidence": 0.0,
  "discrepancies": ["list of specific factual mismatches"],
  "alternative": {
    "url": "https://...",
    "title": "Source title",
    "confidence": 0.0
  },
  "body_text_adjustment": "Suggested correction to body text, or null"
}
```

## Status Definitions

- **verified**: URL accessible AND (content matches claim OR depth=existence)
- **failed**: URL not accessible or returns 4xx/5xx
- **unverifiable**: Cannot retrieve content (paywall, login required, PDF download, book ISBN, ambiguous reference)
- **redirected**: URL redirected to a different final URL — flag for human review

## Type Definitions

- **url**: Full `https://` or `http://` URL
- **doi**: `doi:` prefix or `https://doi.org/` URL
- **apa**: Author (Year). Title. Journal. e.g. `Smith, J. (2023). Testing...`
- **mla**: Author. "Title." Publication, Year. e.g. `Smith, John. "Testing..."`
- **chicago**: Footnote or bibliography style
- **bare_ref**: `[1]` or `[Smith 2023]` — inline marker pointing to bibliography
- **footnote**: Numbered footnote reference
