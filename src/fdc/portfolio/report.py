from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class ImportSummary:
    batch_id: int
    batch_key: str
    status: str
    total_rows: int
    accepted_rows: int
    rejected_rows: int
    window_start: str | None
    window_end: str | None


@dataclass(frozen=True)
class IssueSummary:
    total_issues: int
    issue_type_counts: list[tuple[str, int]]
    severity_counts: list[tuple[str, int]]


@dataclass(frozen=True)
class PortfolioSummary:
    portfolio_code: str
    portfolio_name: str
    obs_count: int
    latest_nav: Decimal
    start_date: str
    end_date: str


@dataclass(frozen=True)
class AnalysisSummary:
    cumulative_return: Decimal
    max_drawdown: Decimal
    annualized_volatility: Decimal | None
    win_rate: Decimal | None
    monthly_returns: list[tuple[str, Decimal | None]]


@dataclass(frozen=True)
class PortfolioReportModel:
    import_summary: ImportSummary
    issue_summary: IssueSummary
    portfolio_summary: PortfolioSummary
    analysis_summary: AnalysisSummary


def render_portfolio_report(model: PortfolioReportModel) -> str:
    lines = [
        "# Sample Portfolio Report",
        "",
        "## Report Overview",
        "- This report composes Phase 1A-2 SQLite import outputs and Phase 1A-3 NAV analysis outputs.",
        "- Scope: deterministic sample reporting MVP (no API/frontend, no portfolio_metric_daily persistence).",
        "",
        "## Import Summary",
        f"- Batch ID: `{model.import_summary.batch_id}`",
        f"- Batch Key: `{model.import_summary.batch_key}`",
        f"- Status: `{model.import_summary.status}`",
        f"- Rows (total/accepted/rejected): `{model.import_summary.total_rows}` / `{model.import_summary.accepted_rows}` / `{model.import_summary.rejected_rows}`",
        f"- Date window: `{model.import_summary.window_start}` to `{model.import_summary.window_end}`",
        "",
        "## Issue Summary",
        f"- Total issues: `{model.issue_summary.total_issues}`",
        "- Issue type breakdown:",
    ]
    for k, v in model.issue_summary.issue_type_counts:
        lines.append(f"  - `{k}`: {v}")
    if not model.issue_summary.issue_type_counts:
        lines.append("  - (none)")
    lines.append("- Severity breakdown:")
    for k, v in model.issue_summary.severity_counts:
        lines.append(f"  - `{k}`: {v}")
    if not model.issue_summary.severity_counts:
        lines.append("  - (none)")

    lines.extend([
        "",
        "## Portfolio Summary",
        f"- Portfolio: `{model.portfolio_summary.portfolio_code}` ({model.portfolio_summary.portfolio_name})",
        f"- Observation count: `{model.portfolio_summary.obs_count}`",
        f"- Date range: `{model.portfolio_summary.start_date}` to `{model.portfolio_summary.end_date}`",
        f"- Latest NAV: `{model.portfolio_summary.latest_nav:.8f}`",
        "",
        "## NAV Analysis Summary",
        f"- Cumulative return: `{_fmt_pct(model.analysis_summary.cumulative_return)}`",
        f"- Max drawdown: `{_fmt_pct(model.analysis_summary.max_drawdown)}`",
        f"- Annualized volatility (ddof=1): `{_fmt_pct(model.analysis_summary.annualized_volatility)}`",
        f"- Win rate: `{_fmt_pct(model.analysis_summary.win_rate)}`",
        "",
        "## Monthly Return Table",
        "| Month | Return |",
        "|---|---:|",
    ])
    for month, value in model.analysis_summary.monthly_returns:
        lines.append(f"| {month} | {_fmt_pct(value)} |")

    lines.extend([
        "",
        "## Method Notes",
        "- Data lineage: sample SQLite initialization + sample NAV import + Phase 1A-3 NAV analysis reuse.",
        "- Determinism: section order, metric formatting, and table ordering are fixed.",
        "",
        "## Known Limitations and Next Steps",
        "- Synthetic sample data only.",
        "- No benchmark or market data integration.",
        "- No holdings/positions layer.",
        "- No API/frontend delivery in this phase.",
        "- No portfolio_metric_daily persistence.",
        "",
    ])
    return "\n".join(lines)


def _fmt_pct(v: Decimal | None) -> str:
    if v is None:
        return "n/a"
    return f"{(v * Decimal('100')):.4f}%"
