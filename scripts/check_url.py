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
