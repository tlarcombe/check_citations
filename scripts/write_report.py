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
        "# Citation Check Report",
        "",
        f"**Document:** `{report.get('document', 'unknown')}`  ",
        f"**Generated:** {report.get('generated_at', 'unknown')}",
        "",
        "## Summary",
        "",
        "| Status | Count |",
        "|--------|-------|",
        f"| Total | {s['total']} |",
        f"| Verified | {s['verified']} |",
        f"| Failed | {s['failed']} |",
        f"| Unverifiable | {s['unverifiable']} |",
        "",
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
                lines.append("- **Discrepancies:**")
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
