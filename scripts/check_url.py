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
