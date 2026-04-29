from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from math import sqrt

from sqlalchemy import select
from sqlalchemy.orm import Session

from fdc.db.models import DataBatch, DataIssueLog, NavDaily, PortfolioMetricDaily, utc_now


@dataclass
class NavAnalysisResult:
    batch_id: int
    batch_key: str
    status: str
    row_count: int
    inserted_metrics: int
    issue_count: int


def analyze_nav_metrics(
    session: Session,
    source_name: str = "nav_analysis",
    dataset_name: str = "portfolio_metric_daily",
) -> NavAnalysisResult:
    batch_key = f"nav_analysis_{utc_now().strftime('%Y%m%dT%H%M%S')}"
    batch = DataBatch(
        batch_key=batch_key,
        source_name=source_name,
        dataset_name=dataset_name,
        status="pending",
        row_count=0,
    )
    session.add(batch)
    session.commit()

    nav_rows = session.execute(
        select(NavDaily.portfolio_id, NavDaily.nav_date, NavDaily.nav, NavDaily.daily_return)
        .order_by(NavDaily.portfolio_id, NavDaily.nav_date)
    ).all()

    if not nav_rows:
        _log_issue(session, batch.id, "no_nav_data", "No NAV rows available for analysis")
        batch.status = "failed"
        batch.completed_at = utc_now()
        session.commit()
        return NavAnalysisResult(batch.id, batch.batch_key, batch.status, 0, 0, 1)

    by_portfolio: dict[int, list[tuple[date, Decimal, Decimal | None]]] = {}
    for portfolio_id, nav_date, nav, daily_return in nav_rows:
        by_portfolio.setdefault(portfolio_id, []).append((nav_date, nav, daily_return))

    inserted = 0
    for portfolio_id, rows in by_portfolio.items():
        peak = rows[0][1]
        returns: list[Decimal] = []
        for nav_date, nav, daily_return in rows:
            if peak < nav:
                peak = nav
            drawdown = Decimal("0") if peak == 0 else (nav / peak) - Decimal("1")
            inserted += _upsert_metric(session, portfolio_id, nav_date, "drawdown", drawdown, "pct")

            if daily_return is not None:
                returns.append(daily_return)
            if len(returns) >= 20:
                window = returns[-20:]
                vol = _stdev(window) * Decimal(str(sqrt(252)))
                inserted += _upsert_metric(session, portfolio_id, nav_date, "vol_20d", vol, "pct")

            cum_return = (nav / rows[0][1]) - Decimal("1")
            inserted += _upsert_metric(session, portfolio_id, nav_date, "cum_return", cum_return, "pct")

    batch.row_count = len(nav_rows)
    batch.status = "success"
    batch.completed_at = utc_now()
    session.commit()

    return NavAnalysisResult(batch.id, batch.batch_key, batch.status, len(nav_rows), inserted, 0)


def _upsert_metric(session: Session, portfolio_id: int, metric_date: date, metric_name: str, metric_value: Decimal, metric_unit: str) -> int:
    existing = session.scalar(
        select(PortfolioMetricDaily).where(
            PortfolioMetricDaily.portfolio_id == portfolio_id,
            PortfolioMetricDaily.metric_date == metric_date,
            PortfolioMetricDaily.metric_name == metric_name,
        )
    )
    if existing is None:
        session.add(
            PortfolioMetricDaily(
                portfolio_id=portfolio_id,
                metric_date=metric_date,
                metric_name=metric_name,
                metric_value=metric_value,
                metric_unit=metric_unit,
            )
        )
    else:
        existing.metric_value = metric_value
        existing.metric_unit = metric_unit
    return 1


def _log_issue(session: Session, batch_id: int, issue_type: str, msg: str) -> None:
    session.add(
        DataIssueLog(
            batch_id=batch_id,
            table_name="portfolio_metric_daily",
            record_key=None,
            issue_type=issue_type,
            severity="error",
            issue_message=msg,
        )
    )


def _stdev(values: list[Decimal]) -> Decimal:
    if len(values) <= 1:
        return Decimal("0")
    mean = sum(values) / Decimal(len(values))
    var = sum((x - mean) * (x - mean) for x in values) / Decimal(len(values) - 1)
    return Decimal(str(sqrt(float(var))))
