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
    assert "1" in content


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
