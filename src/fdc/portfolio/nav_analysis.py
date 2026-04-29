from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from statistics import fmean

from sqlalchemy import select
from sqlalchemy.orm import Session

from fdc.db.models import NavDaily, Portfolio


@dataclass
class PortfolioNavMetrics:
    portfolio_code: str
    obs_count: int
    start_date: str
    end_date: str
    start_nav: Decimal
    end_nav: Decimal
    cumulative_return: Decimal
    average_daily_return: Decimal | None
    min_daily_return: Decimal | None
    max_daily_return: Decimal | None


def analyze_nav(session: Session) -> list[PortfolioNavMetrics]:
    portfolios = session.execute(select(Portfolio.id, Portfolio.portfolio_code).order_by(Portfolio.portfolio_code)).all()
    output: list[PortfolioNavMetrics] = []

    for portfolio_id, portfolio_code in portfolios:
        rows = session.execute(
            select(NavDaily.nav_date, NavDaily.nav, NavDaily.daily_return)
            .where(NavDaily.portfolio_id == portfolio_id)
            .order_by(NavDaily.nav_date)
        ).all()
        if not rows:
            continue

        daily_returns = [float(r.daily_return) for r in rows if r.daily_return is not None]
        cumulative_return = (rows[-1].nav / rows[0].nav) - Decimal("1")

        output.append(
            PortfolioNavMetrics(
                portfolio_code=portfolio_code,
                obs_count=len(rows),
                start_date=rows[0].nav_date.isoformat(),
                end_date=rows[-1].nav_date.isoformat(),
                start_nav=rows[0].nav,
                end_nav=rows[-1].nav,
                cumulative_return=cumulative_return,
                average_daily_return=Decimal(str(fmean(daily_returns))) if daily_returns else None,
                min_daily_return=Decimal(str(min(daily_returns))) if daily_returns else None,
                max_daily_return=Decimal(str(max(daily_returns))) if daily_returns else None,
            )
        )

    return output


def build_nav_analysis_report(metrics: list[PortfolioNavMetrics]) -> str:
    lines = [
        "# Sample NAV Analysis Report",
        "",
        "## Scope",
        "- Dataset: `nav_daily` (sample) already imported in SQLite.",
        "- Purpose: portfolio-level NAV analysis MVP report only.",
        "- Persistence: analysis results are **not** written to `portfolio_metric_daily`.",
        "",
        "## Portfolio Metrics",
    ]

    if not metrics:
        lines.append("- No NAV data found.")
        return "\n".join(lines) + "\n"

    for item in metrics:
        lines.extend(
            [
                f"### {item.portfolio_code}",
                f"- Observations: `{item.obs_count}`",
                f"- Date range: `{item.start_date}` to `{item.end_date}`",
                f"- Start NAV: `{item.start_nav}`",
                f"- End NAV: `{item.end_nav}`",
                f"- Cumulative return: `{item.cumulative_return:.8f}`",
                f"- Average daily return: `{_fmt(item.average_daily_return)}`",
                f"- Min daily return: `{_fmt(item.min_daily_return)}`",
                f"- Max daily return: `{_fmt(item.max_daily_return)}`",
                "",
            ]
        )

    return "\n".join(lines)


def _fmt(v: Decimal | None) -> str:
    if v is None:
        return "n/a"
    return f"{v:.8f}"
