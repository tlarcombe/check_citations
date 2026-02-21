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
