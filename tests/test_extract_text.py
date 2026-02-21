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
