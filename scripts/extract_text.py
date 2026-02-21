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
