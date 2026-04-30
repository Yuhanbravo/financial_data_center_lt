from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from math import sqrt

from sqlalchemy import select
from sqlalchemy.orm import Session

from fdc.db.models import NavDaily, Portfolio

TRADING_DAYS_PER_YEAR = Decimal("252")


@dataclass
class PortfolioNavMetrics:
    portfolio_code: str
    obs_count: int
    start_date: str
    end_date: str
    latest_nav: Decimal
    cumulative_return: Decimal
    average_daily_return: Decimal | None
    min_daily_return: Decimal | None
    max_daily_return: Decimal | None
    max_drawdown: Decimal
    annualized_volatility: Decimal | None
    win_rate: Decimal | None
    monthly_returns: list[tuple[str, Decimal | None]]


def analyze_nav(session: Session) -> list[PortfolioNavMetrics]:
    portfolios = session.execute(select(Portfolio.id, Portfolio.portfolio_code).order_by(Portfolio.portfolio_code)).all()
    output: list[PortfolioNavMetrics] = []

    for portfolio_id, portfolio_code in portfolios:
        rows = session.execute(
            select(NavDaily.nav_date, NavDaily.nav)
            .where(NavDaily.portfolio_id == portfolio_id)
            .order_by(NavDaily.nav_date)
        ).all()
        if not rows:
            continue

        dated_navs = [(r.nav_date, r.nav) for r in rows]
        _validate_nav_series(portfolio_code, dated_navs)

        nav_series = [nav for _, nav in dated_navs]
        daily_returns = _compute_daily_returns(dated_navs)
        cumulative_return = (nav_series[-1] / nav_series[0]) - Decimal("1")
        max_drawdown = _compute_max_drawdown(nav_series)
        annualized_volatility = _compute_annualized_volatility(daily_returns)
        win_rate = _compute_win_rate(daily_returns)
        monthly_returns = _compute_monthly_returns(dated_navs)

        output.append(
            PortfolioNavMetrics(
                portfolio_code=portfolio_code,
                obs_count=len(rows),
                start_date=rows[0].nav_date.isoformat(),
                end_date=rows[-1].nav_date.isoformat(),
                latest_nav=rows[-1].nav,
                cumulative_return=cumulative_return,
                average_daily_return=_compute_average_daily_return(daily_returns),
                min_daily_return=min(daily_returns) if daily_returns else None,
                max_daily_return=max(daily_returns) if daily_returns else None,
                max_drawdown=max_drawdown,
                annualized_volatility=annualized_volatility,
                win_rate=win_rate,
                monthly_returns=monthly_returns,
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
                f"- Observation count: `{item.obs_count}`",
                f"- Date range: `{item.start_date}` to `{item.end_date}`",
                f"- Latest NAV: `{item.latest_nav:.8f}`",
                f"- Cumulative return: `{_fmt_pct(item.cumulative_return)}`",
                f"- Daily return summary (avg/min/max): `{_fmt_pct(item.average_daily_return)}` / `{_fmt_pct(item.min_daily_return)}` / `{_fmt_pct(item.max_daily_return)}`",
                f"- Max drawdown: `{_fmt_pct(item.max_drawdown)}`",
                f"- Annualized volatility (ddof=1): `{_fmt_pct(item.annualized_volatility)}`",
                f"- Win rate: `{_fmt_pct(item.win_rate)}`",
                "- Monthly return table:",
                "",
                "| Month | Return |",
                "|---|---:|",
            ]
        )
        for month, value in item.monthly_returns:
            lines.append(f"| {month} | {_fmt_pct(value)} |")
        lines.append("")

    return "\n".join(lines)


def _validate_nav_series(portfolio_code: str, rows: list[tuple[date, Decimal]]) -> None:
    for idx, (nav_date, nav) in enumerate(rows):
        if not nav.is_finite() or nav <= 0:
            raise ValueError(f"Invalid NAV for portfolio {portfolio_code} on {nav_date.isoformat()} at index {idx}: {nav}")


def _compute_daily_returns(rows: list[tuple[date, Decimal]]) -> list[Decimal]:
    output: list[Decimal] = []
    previous_nav: Decimal | None = None
    for _, nav in rows:
        if previous_nav is not None:
            output.append((nav / previous_nav) - Decimal("1"))
        previous_nav = nav
    return output


def _compute_average_daily_return(daily_returns: list[Decimal]) -> Decimal | None:
    if not daily_returns:
        return None
    return sum(daily_returns, start=Decimal("0")) / Decimal(len(daily_returns))


def _compute_max_drawdown(nav_series: list[Decimal]) -> Decimal:
    peak = nav_series[0]
    max_drawdown = Decimal("0")
    for nav in nav_series:
        if nav > peak:
            peak = nav
        drawdown = (nav / peak) - Decimal("1")
        if drawdown < max_drawdown:
            max_drawdown = drawdown
    return max_drawdown


def _compute_annualized_volatility(daily_returns: list[Decimal]) -> Decimal | None:
    if len(daily_returns) < 2:
        return None
    return_values = [float(value) for value in daily_returns]
    mean = sum(return_values) / len(return_values)
    sample_var = sum((x - mean) ** 2 for x in return_values) / (len(return_values) - 1)
    return Decimal(str(sqrt(sample_var))) * TRADING_DAYS_PER_YEAR.sqrt()


def _compute_win_rate(daily_returns: list[Decimal]) -> Decimal | None:
    if not daily_returns:
        return None
    wins = sum(1 for r in daily_returns if r > 0)
    return Decimal(wins) / Decimal(len(daily_returns))


def _compute_monthly_returns(rows: list[tuple[date, Decimal]]) -> list[tuple[str, Decimal | None]]:
    month_end_nav: dict[str, Decimal] = {}
    for nav_date, nav in rows:
        month_end_nav[f"{nav_date.year:04d}-{nav_date.month:02d}"] = nav

    months = sorted(month_end_nav.keys())
    output: list[tuple[str, Decimal | None]] = []
    prev_nav: Decimal | None = None
    for month in months:
        current = month_end_nav[month]
        if prev_nav is None:
            output.append((month, None))
        else:
            output.append((month, (current / prev_nav) - Decimal("1")))
        prev_nav = current
    return output


def _fmt_pct(v: Decimal | None) -> str:
    if v is None:
        return "n/a"
    return f"{(v * Decimal('100')):.4f}%"
