from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from fdc.db.session import get_session_local, resolve_database_url
from fdc.portfolio.import_nav import import_nav_csv, seed_portfolios


def build_report(markdown_path: Path, result) -> None:
    issue_lines = "\n".join([f"- `{k}`: {v}" for k, v in sorted(result.issue_counts.items())]) or "- (none)"
    markdown = f"""# Sample NAV Import Report

- Batch ID: `{result.batch_id}`
- Batch Key: `{result.batch_key}`
- Source file: `{result.source_file}`
- Staged artifact: `{result.staged_file}`
- Batch status: `{result.status}`
- Total rows: `{result.total_rows}`
- Accepted rows: `{result.accepted_rows}`
- Rejected rows: `{result.rejected_rows}`
- Date range: `{result.date_min}` to `{result.date_max}`

## Issue Summary
{issue_lines}
"""
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.write_text(markdown, encoding="utf-8")


if __name__ == "__main__":
    db_url = resolve_database_url()
    session_local = get_session_local(db_url)

    portfolio_csv = ROOT / "data" / "sample" / "portfolio_sample.csv"
    nav_csv = ROOT / "data" / "sample" / "nav_daily_sample.csv"
    report_file = ROOT / "data" / "artifacts" / "reports" / "sample_nav_import_report.md"

    with session_local() as session:
        seeded = seed_portfolios(session, portfolio_csv)
        result = import_nav_csv(session, nav_csv)

    build_report(report_file, result)
    print(f"Seeded portfolios: {seeded}")
    print(f"Imported NAV batch_id={result.batch_id} status={result.status}")
    print(f"Report generated: {report_file}")
