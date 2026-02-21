# check_citations Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a shared Claude Code skill that extracts citations from documents, verifies their existence and content match, finds alternatives for broken sources, and outputs both JSON and markdown reports.

**Architecture:** A Claude Code skill (`~/.claude/skills/check-citations/SKILL.md`) that orchestrates Python helper scripts (document parsing, URL checking, report writing) and Claude's built-in tools (WebFetch, WebSearch) for citation verification. Python handles I/O and HTTP; Claude handles LLM reasoning. Parallel subagents verify citations concurrently.

**Tech Stack:** Python 3.14, requests 2.32, python-docx 1.2 (installed), pdfplumber (to install), pytest, Claude Code skill system.

---

## Key facts before starting

- Python 3.14.2 at `python3`
- `python-docx` and `requests` already installed; `pdfplumber` needs installing
- Skill file lives at `~/.claude/skills/check-citations/SKILL.md` (symlink or copy from repo)
- Plan output always into `docs/plans/YYYY-MM-DD-*.md`
- Run all tests from project root: `pytest tests/ -v`
- The skill is a **markdown prompt** — not a Python daemon. It tells Claude *how* to orchestrate the process.

---

## Task 1: Scaffold project structure

**Files:**
- Create: `src/__init__.py`
- Create: `src/scripts/__init__.py`
- Create: `scripts/extract_text.py` (stub)
- Create: `scripts/check_url.py` (stub)
- Create: `scripts/write_report.py` (stub)
- Create: `tests/__init__.py`
- Create: `tests/fixtures/sample_markdown.md`
- Create: `tests/fixtures/sample.docx` (generated in test setup)
- Create: `requirements.txt`
- Create: `pyproject.toml`

**Step 1: Create directory structure**

```bash
mkdir -p scripts tests/fixtures src
touch scripts/__init__.py tests/__init__.py src/__init__.py
```

Expected: no output, no errors.

**Step 2: Create requirements.txt**

```
pdfplumber>=0.11
requests>=2.32
python-docx>=1.2
pytest>=8.0
pytest-mock>=3.14
```

**Step 3: Install pdfplumber**

```bash
pip install pdfplumber --quiet
```

Expected: `Successfully installed pdfplumber-...`

**Step 4: Create pyproject.toml**

```toml
[project]
name = "check-citations"
version = "0.1.0"
description = "Citation verification utility for Claude Code skills ecosystem"
requires-python = ">=3.11"
dependencies = [
    "pdfplumber>=0.11",
    "requests>=2.32",
    "python-docx>=1.2",
]

[project.scripts]
extract-text = "scripts.extract_text:main"
check-url = "scripts.check_url:main"
write-report = "scripts.write_report:main"

[tool.pytest.ini_options]
testpaths = ["tests"]
```

**Step 5: Create stub scripts (just `pass` bodies — real code comes in later tasks)**

`scripts/extract_text.py`:
```python
#!/usr/bin/env python3
"""Extract plain text from a document file. Usage: python scripts/extract_text.py <path>"""
import sys

def extract(path: str) -> str:
    raise NotImplementedError

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: extract_text.py <path>", file=sys.stderr)
        sys.exit(1)
    print(extract(sys.argv[1]))
```

`scripts/check_url.py`:
```python
#!/usr/bin/env python3
"""Check if a URL is accessible. Usage: python scripts/check_url.py <url>"""
import sys, json

def check(url: str) -> dict:
    raise NotImplementedError

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: check_url.py <url>", file=sys.stderr)
        sys.exit(1)
    print(json.dumps(check(sys.argv[1])))
```

`scripts/write_report.py`:
```python
#!/usr/bin/env python3
"""Write JSON + markdown report. Usage: python scripts/write_report.py <report.json> <outdir>"""
import sys, json, pathlib

def write(report: dict, outdir: str) -> tuple[str, str]:
    raise NotImplementedError

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: write_report.py <report.json> <outdir>", file=sys.stderr)
        sys.exit(1)
    data = json.loads(pathlib.Path(sys.argv[1]).read_text())
    json_path, md_path = write(data, sys.argv[2])
    print(f"JSON: {json_path}\nMarkdown: {md_path}")
```

**Step 6: Create markdown test fixture**

`tests/fixtures/sample_markdown.md`:
```markdown
# Test Document for Citation Checking

The Eiffel Tower is 330 metres tall [1].

Python was created in 1991 by Guido van Rossum. See [the official docs](https://docs.python.org/3/).

A broken link example: [this source](https://this-url-definitely-does-not-exist-abcxyz123.com/paper).

A DOI example: The paper argues for better testing practices (doi:10.1000/xyz123).

## References

[1] https://en.wikipedia.org/wiki/Eiffel_Tower
```

**Step 7: Commit**

```bash
git add .
git commit -m "chore: scaffold project structure with stub scripts and test fixtures"
```

---

## Task 2: Text extractor — markdown and plain text

**Files:**
- Modify: `scripts/extract_text.py`
- Create: `tests/test_extract_text.py`

**Step 1: Write failing tests**

`tests/test_extract_text.py`:
```python
import pytest
from pathlib import Path

FIXTURE_DIR = Path(__file__).parent / "fixtures"

def test_extract_markdown_returns_string():
    from scripts.extract_text import extract
    result = extract(str(FIXTURE_DIR / "sample_markdown.md"))
    assert isinstance(result, str)
    assert len(result) > 0

def test_extract_markdown_preserves_content():
    from scripts.extract_text import extract
    result = extract(str(FIXTURE_DIR / "sample_markdown.md"))
    assert "Eiffel Tower" in result
    assert "docs.python.org" in result

def test_extract_txt_file(tmp_path):
    from scripts.extract_text import extract
    f = tmp_path / "test.txt"
    f.write_text("Hello citation world")
    result = extract(str(f))
    assert result == "Hello citation world"

def test_extract_unknown_extension_raises(tmp_path):
    from scripts.extract_text import extract
    f = tmp_path / "test.xyz"
    f.write_text("content")
    with pytest.raises(ValueError, match="Unsupported"):
        extract(str(f))

def test_extract_missing_file_raises():
    from scripts.extract_text import extract
    with pytest.raises(FileNotFoundError):
        extract("/nonexistent/path/file.md")
```

**Step 2: Run tests — verify they fail**

```bash
pytest tests/test_extract_text.py -v
```

Expected: FAILED — `NotImplementedError` from stub.

**Step 3: Implement extract_text.py**

```python
#!/usr/bin/env python3
"""Extract plain text from a document file. Usage: python scripts/extract_text.py <path>"""
import sys
from pathlib import Path


def extract(path: str) -> str:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"File not found: {path}")
    suffix = p.suffix.lower()
    if suffix in (".md", ".txt", ".rst", ""):
        return p.read_text(encoding="utf-8")
    elif suffix == ".docx":
        return _extract_docx(p)
    elif suffix == ".pdf":
        return _extract_pdf(p)
    else:
        raise ValueError(f"Unsupported file type: {suffix}")


def _extract_docx(p: Path) -> str:
    from docx import Document
    doc = Document(str(p))
    return "\n".join(para.text for para in doc.paragraphs)


def _extract_pdf(p: Path) -> str:
    import pdfplumber
    pages = []
    with pdfplumber.open(str(p)) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                pages.append(text)
    return "\n".join(pages)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: extract_text.py <path>", file=sys.stderr)
        sys.exit(1)
    print(extract(sys.argv[1]))
```

**Step 4: Run tests — verify they pass**

```bash
pytest tests/test_extract_text.py -v
```

Expected: 5 PASSED.

**Step 5: Commit**

```bash
git add scripts/extract_text.py tests/test_extract_text.py
git commit -m "feat: extract_text helper for markdown, txt, docx, pdf"
```

---

## Task 3: Text extractor — DOCX

**Files:**
- Modify: `tests/test_extract_text.py`
- Create: `tests/fixtures/create_fixtures.py` (test helper)

**Step 1: Write DOCX fixture generator**

`tests/fixtures/create_fixtures.py`:
```python
"""Run once to generate binary test fixtures."""
from pathlib import Path
from docx import Document

def create_sample_docx():
    doc = Document()
    doc.add_heading("Test Document", 0)
    doc.add_paragraph("This is a claim about climate change [Smith 2023].")
    doc.add_paragraph("See also https://en.wikipedia.org/wiki/Climate_change")
    out = Path(__file__).parent / "sample.docx"
    doc.save(str(out))
    print(f"Created {out}")

if __name__ == "__main__":
    create_sample_docx()
```

**Step 2: Generate the fixture**

```bash
python tests/fixtures/create_fixtures.py
```

Expected: `Created .../tests/fixtures/sample.docx`

**Step 3: Write failing DOCX tests**

Add to `tests/test_extract_text.py`:
```python
def test_extract_docx_returns_string():
    from scripts.extract_text import extract
    result = extract(str(FIXTURE_DIR / "sample.docx"))
    assert isinstance(result, str)
    assert len(result) > 0

def test_extract_docx_preserves_content():
    from scripts.extract_text import extract
    result = extract(str(FIXTURE_DIR / "sample.docx"))
    assert "climate change" in result.lower()
    assert "wikipedia.org" in result
```

**Step 4: Run tests**

```bash
pytest tests/test_extract_text.py -v
```

Expected: 7 PASSED (the existing 5 + 2 new DOCX tests).

**Step 5: Commit**

```bash
git add tests/test_extract_text.py tests/fixtures/
git commit -m "test: add DOCX fixture and extraction tests"
```

---

## Task 4: URL checker

**Files:**
- Modify: `scripts/check_url.py`
- Create: `tests/test_check_url.py`

**Step 1: Write failing tests**

`tests/test_check_url.py`:
```python
import pytest
from unittest.mock import patch, MagicMock

def test_live_url_returns_accessible():
    from scripts.check_url import check
    # Uses a URL that is reliably up
    result = check("https://docs.python.org/3/")
    assert result["accessible"] is True
    assert result["status_code"] == 200
    assert "final_url" in result

def test_dead_url_returns_inaccessible():
    from scripts.check_url import check
    result = check("https://this-url-definitely-does-not-exist-abcxyz123.com/")
    assert result["accessible"] is False
    assert result["error"] is not None

def test_doi_url_follows_redirect():
    from scripts.check_url import check
    # doi.org redirects to publisher — we just need it to resolve
    result = check("https://doi.org/10.1038/nature12373")
    # May be accessible or paywalled but should not hard-error
    assert "accessible" in result
    assert "final_url" in result

def test_result_schema():
    from scripts.check_url import check
    with patch("scripts.check_url.requests") as mock_req:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.url = "https://example.com"
        mock_req.get.return_value = mock_resp
        result = check("https://example.com")
    assert set(result.keys()) >= {"accessible", "status_code", "final_url", "error"}

def test_timeout_returns_inaccessible():
    from scripts.check_url import check
    import requests as req_lib
    with patch("scripts.check_url.requests.get", side_effect=req_lib.Timeout):
        result = check("https://example.com")
    assert result["accessible"] is False
    assert "timeout" in result["error"].lower()
```

**Step 2: Run tests — verify they fail**

```bash
pytest tests/test_check_url.py -v
```

Expected: FAILED — `NotImplementedError`.

**Step 3: Implement check_url.py**

```python
#!/usr/bin/env python3
"""Check if a URL is accessible. Outputs JSON. Usage: python scripts/check_url.py <url>"""
import sys
import json
import requests
from requests.exceptions import Timeout, ConnectionError, TooManyRedirects


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; check-citations/1.0; "
        "+https://github.com/tlarcombe/check_citations)"
    )
}
TIMEOUT = 10  # seconds


def check(url: str) -> dict:
    try:
        resp = requests.get(
            url,
            headers=HEADERS,
            timeout=TIMEOUT,
            allow_redirects=True,
        )
        return {
            "accessible": resp.status_code < 400,
            "status_code": resp.status_code,
            "final_url": resp.url,
            "error": None,
        }
    except Timeout:
        return _error(url, "Timeout after 10s")
    except ConnectionError as e:
        return _error(url, f"Connection error: {e}")
    except TooManyRedirects:
        return _error(url, "Too many redirects")
    except Exception as e:
        return _error(url, str(e))


def _error(url: str, msg: str) -> dict:
    return {
        "accessible": False,
        "status_code": None,
        "final_url": url,
        "error": msg,
    }


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: check_url.py <url>", file=sys.stderr)
        sys.exit(1)
    print(json.dumps(check(sys.argv[1])))
```

**Step 4: Run tests**

```bash
pytest tests/test_check_url.py -v
```

Expected: 5 PASSED. Note: `test_live_url_returns_accessible` and `test_doi_url_follows_redirect` make real HTTP calls — they will be slow but should pass.

**Step 5: Commit**

```bash
git add scripts/check_url.py tests/test_check_url.py
git commit -m "feat: check_url helper with timeout, redirect following, error schema"
```

---

## Task 5: Report writer

**Files:**
- Modify: `scripts/write_report.py`
- Create: `tests/test_write_report.py`

**Step 1: Define the canonical JSON schema**

The report dict structure (used by skill and all helpers):

```python
SAMPLE_REPORT = {
    "document": "path/to/doc.md",
    "generated_at": "2026-02-21T12:00:00Z",
    "summary": {
        "total": 3,
        "verified": 1,
        "failed": 1,
        "unverifiable": 1,
    },
    "citations": [
        {
            "id": 1,
            "raw_text": "https://en.wikipedia.org/wiki/Eiffel_Tower",
            "type": "url",          # url | doi | apa | mla | chicago | bare_ref
            "claimed_in": "The Eiffel Tower is 330 metres tall [1].",
            "resolved_url": "https://en.wikipedia.org/wiki/Eiffel_Tower",
            "status": "verified",   # verified | failed | unverifiable | redirected
            "content_match": True,  # True | False | None (None = not checked)
            "confidence": 0.9,
            "discrepancies": [],
            "alternative": None,
            "body_text_adjustment": None,
        },
        {
            "id": 2,
            "raw_text": "https://this-url-definitely-does-not-exist-abcxyz123.com/paper",
            "type": "url",
            "claimed_in": "A broken link example.",
            "resolved_url": None,
            "status": "failed",
            "content_match": None,
            "confidence": 0.0,
            "discrepancies": [],
            "alternative": {
                "url": "https://example-alternative.com/paper",
                "title": "Alternative Source Title",
                "confidence": 0.75,
            },
            "body_text_adjustment": None,
        },
        {
            "id": 3,
            "raw_text": "doi:10.1000/xyz123",
            "type": "doi",
            "claimed_in": "The paper argues for better testing practices.",
            "resolved_url": "https://doi.org/10.1000/xyz123",
            "status": "unverifiable",
            "content_match": None,
            "confidence": 0.0,
            "discrepancies": [],
            "alternative": None,
            "body_text_adjustment": None,
        },
    ],
}
```

**Step 2: Write failing tests**

`tests/test_write_report.py`:
```python
import json
import pytest
from pathlib import Path

SAMPLE_REPORT = {
    "document": "test.md",
    "generated_at": "2026-02-21T12:00:00Z",
    "summary": {"total": 1, "verified": 1, "failed": 0, "unverifiable": 0},
    "citations": [
        {
            "id": 1,
            "raw_text": "https://example.com",
            "type": "url",
            "claimed_in": "See example [1].",
            "resolved_url": "https://example.com",
            "status": "verified",
            "content_match": True,
            "confidence": 0.9,
            "discrepancies": [],
            "alternative": None,
            "body_text_adjustment": None,
        }
    ],
}


def test_write_creates_json_file(tmp_path):
    from scripts.write_report import write
    json_path, md_path = write(SAMPLE_REPORT, str(tmp_path))
    assert Path(json_path).exists()
    assert json_path.endswith(".json")


def test_write_creates_markdown_file(tmp_path):
    from scripts.write_report import write
    json_path, md_path = write(SAMPLE_REPORT, str(tmp_path))
    assert Path(md_path).exists()
    assert md_path.endswith(".md")


def test_json_output_is_valid(tmp_path):
    from scripts.write_report import write
    json_path, _ = write(SAMPLE_REPORT, str(tmp_path))
    data = json.loads(Path(json_path).read_text())
    assert data["summary"]["total"] == 1
    assert len(data["citations"]) == 1
    assert data["citations"][0]["status"] == "verified"


def test_markdown_contains_summary(tmp_path):
    from scripts.write_report import write
    _, md_path = write(SAMPLE_REPORT, str(tmp_path))
    content = Path(md_path).read_text()
    assert "## Summary" in content
    assert "1" in content  # total count


def test_markdown_has_sections(tmp_path):
    from scripts.write_report import write
    _, md_path = write(SAMPLE_REPORT, str(tmp_path))
    content = Path(md_path).read_text()
    for section in ["Verified", "Failed", "Unverifiable"]:
        assert section in content


def test_failed_citation_in_markdown(tmp_path):
    from scripts.write_report import write
    report = dict(SAMPLE_REPORT)
    report["summary"] = {"total": 1, "verified": 0, "failed": 1, "unverifiable": 0}
    report["citations"] = [{**SAMPLE_REPORT["citations"][0], "status": "failed",
                            "content_match": None, "resolved_url": None}]
    _, md_path = write(report, str(tmp_path))
    content = Path(md_path).read_text()
    assert "https://example.com" in content
```

**Step 3: Run tests — verify they fail**

```bash
pytest tests/test_write_report.py -v
```

Expected: FAILED — `NotImplementedError`.

**Step 4: Implement write_report.py**

```python
#!/usr/bin/env python3
"""Write JSON + markdown citation report. Usage: python scripts/write_report.py <report.json> <outdir>"""
import sys
import json
import pathlib
from datetime import datetime


def write(report: dict, outdir: str) -> tuple[str, str]:
    out = pathlib.Path(outdir)
    out.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = out / f"citations_report_{stamp}.json"
    md_path = out / f"citations_report_{stamp}.md"
    json_path.write_text(json.dumps(report, indent=2))
    md_path.write_text(_to_markdown(report))
    return str(json_path), str(md_path)


def _to_markdown(report: dict) -> str:
    s = report["summary"]
    lines = [
        f"# Citation Check Report",
        f"",
        f"**Document:** `{report.get('document', 'unknown')}`  ",
        f"**Generated:** {report.get('generated_at', 'unknown')}",
        f"",
        f"## Summary",
        f"",
        f"| Status | Count |",
        f"|--------|-------|",
        f"| Total | {s['total']} |",
        f"| Verified | {s['verified']} |",
        f"| Failed | {s['failed']} |",
        f"| Unverifiable | {s['unverifiable']} |",
        f"",
    ]

    for section, statuses in [
        ("Verified", ["verified", "redirected"]),
        ("Failed", ["failed"]),
        ("Unverifiable", ["unverifiable"]),
    ]:
        items = [c for c in report["citations"] if c["status"] in statuses]
        lines.append(f"## {section} ({len(items)})")
        lines.append("")
        if not items:
            lines.append("_None._")
            lines.append("")
            continue
        for c in items:
            lines.append(f"### [{c['id']}] `{c['raw_text']}`")
            lines.append(f"- **Type:** {c['type']}")
            lines.append(f"- **Claimed in:** _{c.get('claimed_in', '—')}_")
            if c.get("resolved_url"):
                lines.append(f"- **Resolved URL:** {c['resolved_url']}")
            if c.get("content_match") is not None:
                match_str = "Yes" if c["content_match"] else "No"
                lines.append(f"- **Content match:** {match_str} (confidence: {c.get('confidence', 0):.0%})")
            if c.get("discrepancies"):
                lines.append(f"- **Discrepancies:**")
                for d in c["discrepancies"]:
                    lines.append(f"  - {d}")
            if c.get("alternative"):
                alt = c["alternative"]
                lines.append(f"- **Suggested alternative:** [{alt.get('title', alt['url'])}]({alt['url']}) (confidence: {alt.get('confidence', 0):.0%})")
            if c.get("body_text_adjustment"):
                lines.append(f"- **Recommended adjustment:** {c['body_text_adjustment']}")
            lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: write_report.py <report.json> <outdir>", file=sys.stderr)
        sys.exit(1)
    data = json.loads(pathlib.Path(sys.argv[1]).read_text())
    json_path, md_path = write(data, sys.argv[2])
    print(f"JSON: {json_path}\nMarkdown: {md_path}")
```

**Step 5: Run tests**

```bash
pytest tests/test_write_report.py -v
```

Expected: 6 PASSED.

**Step 6: Run full test suite**

```bash
pytest tests/ -v
```

Expected: All tests pass.

**Step 7: Commit**

```bash
git add scripts/write_report.py tests/test_write_report.py
git commit -m "feat: write_report helper producing JSON + markdown with status sections"
```

---

## Task 6: Build the SKILL.md

**Files:**
- Create: `skill/SKILL.md` (source of truth in repo)
- Create: `skill/references/citation_schema.md`
- Create: `skill/references/verification_workflow.md`

This is the most important task. The skill file is a detailed prompt that instructs Claude how to execute the citation-checking workflow. It is not Python — it is markdown with YAML frontmatter.

**Step 1: Create skill directory structure**

```bash
mkdir -p skill/references skill/assets
```

**Step 2: Create citation schema reference**

`skill/references/citation_schema.md`:
```markdown
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
  "content_match": true | false | null,
  "confidence": 0.0,
  "discrepancies": ["list of specific factual mismatches"],
  "alternative": {
    "url": "https://...",
    "title": "Source title",
    "confidence": 0.0
  } | null,
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
```

**Step 3: Create verification workflow reference**

`skill/references/verification_workflow.md`:
```markdown
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
- Source doesn't mention the topic at all
- Source is from a different context (e.g., claim is about UK, source is about USA)

## Phase 5: Find Alternatives (for failed citations)

For citations with status=failed, use WebSearch to find a replacement source:
- Search query: the claim text + key entities
- Prefer: authoritative sources (gov, edu, established publications)
- Exclude: the original (broken) domain

## Phase 6: Write Report

Run: `python /home/tlarcombe/projects/check_citations/scripts/write_report.py <report_json_path> <outdir>`

Or construct the JSON in memory and pass to the Python helper.
```

**Step 4: Write the SKILL.md**

`skill/SKILL.md`:
```markdown
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
    "total": N,
    "verified": N,
    "failed": N,
    "unverifiable": N
  },
  "citations": [ ... ]
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
- `unverifiable` ≠ wrong — it means the source cannot be fetched, not that the claim is false
- For paywalled academic papers: flag as unverifiable, suggest open-access alternative if possible (arXiv, PubMed, OpenAlex)
```

**Step 5: Verify skill file has valid frontmatter**

```bash
python3 -c "
import re
text = open('skill/SKILL.md').read()
fm = re.match(r'^---\n(.+?)\n---', text, re.DOTALL)
assert fm, 'No frontmatter found'
assert 'name:' in fm.group(1), 'Missing name:'
assert 'description:' in fm.group(1), 'Missing description:'
print('Frontmatter OK')
name_line = [l for l in fm.group(1).splitlines() if l.startswith('name:')][0]
name = name_line.split(':', 1)[1].strip()
assert re.match(r'^[a-z0-9][a-z0-9-]*[a-z0-9]$', name), f'Invalid name format: {name}'
print(f'Name valid: {name}')
"
```

Expected: `Frontmatter OK` / `Name valid: check-citations`

**Step 6: Commit**

```bash
git add skill/
git commit -m "feat: SKILL.md with full citation extraction and verification workflow"
```

---

## Task 7: Deploy skill

**Files:**
- Create: `Makefile` (with deploy target)

**Step 1: Create Makefile**

```makefile
SKILL_NAME := check-citations
SKILL_DIR := $(HOME)/.claude/skills/$(SKILL_NAME)
SRC_DIR := $(CURDIR)/skill

.PHONY: deploy undeploy test

deploy:
	mkdir -p $(SKILL_DIR)/references $(SKILL_DIR)/assets
	cp $(SRC_DIR)/SKILL.md $(SKILL_DIR)/SKILL.md
	cp $(SRC_DIR)/references/* $(SKILL_DIR)/references/ 2>/dev/null || true
	@echo "Deployed $(SKILL_NAME) to $(SKILL_DIR)"

undeploy:
	rm -rf $(SKILL_DIR)
	@echo "Removed $(SKILL_NAME)"

test:
	pytest tests/ -v
```

**Step 2: Deploy the skill**

```bash
make deploy
```

Expected: `Deployed check-citations to /home/tlarcombe/.claude/skills/check-citations`

**Step 3: Verify it appears in the skills directory**

```bash
ls ~/.claude/skills/check-citations/
```

Expected: `SKILL.md  references/`

**Step 4: Commit**

```bash
git add Makefile
git commit -m "chore: Makefile with deploy/undeploy/test targets"
```

---

## Task 8: Integration test with the sample fixture

**Goal:** Run the full skill workflow manually against `tests/fixtures/sample_markdown.md` and verify output.

**Step 1: Run extract_text on the fixture**

```bash
python scripts/extract_text.py tests/fixtures/sample_markdown.md
```

Expected: the raw text of the fixture including URLs and references.

**Step 2: Run check_url on the known-live URL**

```bash
python scripts/check_url.py "https://docs.python.org/3/"
```

Expected JSON: `{"accessible": true, "status_code": 200, ...}`

**Step 3: Run check_url on the known-dead URL**

```bash
python scripts/check_url.py "https://this-url-definitely-does-not-exist-abcxyz123.com/paper"
```

Expected JSON: `{"accessible": false, "status_code": null, "error": "Connection error: ..."}`

**Step 4: Assemble a sample report and write it**

```bash
python3 -c "
import json, pathlib, tempfile
from scripts.write_report import write

report = {
    'document': 'tests/fixtures/sample_markdown.md',
    'generated_at': '2026-02-21T12:00:00Z',
    'summary': {'total': 3, 'verified': 1, 'failed': 1, 'unverifiable': 1},
    'citations': [
        {'id': 1, 'raw_text': 'https://docs.python.org/3/', 'type': 'url',
         'claimed_in': 'See the official docs.', 'resolved_url': 'https://docs.python.org/3/',
         'status': 'verified', 'content_match': True, 'confidence': 0.95,
         'discrepancies': [], 'alternative': None, 'body_text_adjustment': None},
        {'id': 2, 'raw_text': 'https://this-url-definitely-does-not-exist-abcxyz123.com/paper',
         'type': 'url', 'claimed_in': 'A broken link example.', 'resolved_url': None,
         'status': 'failed', 'content_match': None, 'confidence': 0.0,
         'discrepancies': [], 'alternative': {'url': 'https://example.com', 'title': 'Example', 'confidence': 0.6},
         'body_text_adjustment': None},
        {'id': 3, 'raw_text': 'doi:10.1000/xyz123', 'type': 'doi',
         'claimed_in': 'The paper argues for better testing practices.',
         'resolved_url': 'https://doi.org/10.1000/xyz123', 'status': 'unverifiable',
         'content_match': None, 'confidence': 0.0, 'discrepancies': [],
         'alternative': None, 'body_text_adjustment': None},
    ]
}

json_p, md_p = write(report, '/tmp/check_citations_test')
print(f'JSON: {json_p}')
print(f'MD:   {md_p}')
print()
print(open(md_p).read())
"
```

Expected: Full markdown report printed with Verified/Failed/Unverifiable sections.

**Step 5: Run full test suite one final time**

```bash
pytest tests/ -v
```

Expected: All tests pass.

**Step 6: Final commit**

```bash
git add .
git commit -m "test: integration smoke test — helpers confirmed working end-to-end"
```

---

## Task 9: Update CLAUDE.md and memory

**Step 1: Update CLAUDE.md status section**

Change the status checkboxes from `[ ]` to `[x]` for completed items.

**Step 2: Update memory file**

Add to `/home/tlarcombe/.claude/projects/-home-tlarcombe-projects-check-citations/memory/MEMORY.md`:

```markdown
## Implementation Status

- Helpers complete: extract_text.py, check_url.py, write_report.py
- Skill deployed to: ~/.claude/skills/check-citations/
- Deploy with: make deploy (from project root)
- Tests: pytest tests/ -v (all should pass)
- Fixtures: tests/fixtures/sample_markdown.md, tests/fixtures/sample.docx

## Known Limitations (v1)

- No Anthropic SDK dependency — skill relies on Claude Code's built-in tools
- PDF extraction via pdfplumber (text-only, no OCR for scanned PDFs)
- Academic references (APA/MLA) without URLs marked unverifiable — no search-to-verify in v1
- check_url.py makes real HTTP requests — use mock in unit tests for reliability
```

**Step 3: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: update CLAUDE.md with implementation status"
```

---

## Done

All Python helpers are tested and working. The skill is deployed. Any project in the ecosystem can now call:

```
Use the check-citations skill with args="path/to/document.pdf"
```

Or directly from a Claude Code session:
```
/check-citations /path/to/report.md depth=content outdir=/tmp/citation_output
```
