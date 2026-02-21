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
