from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from fdc.db.models import DataBatch, DataIssueLog, NavDaily, Portfolio
from fdc.portfolio.nav_analysis import analyze_nav


@dataclass(frozen=True)
class PortfolioListItem:
    portfolio_code: str
    portfolio_name: str
    base_ccy: str
    inception_date: date | None
    is_active: bool


@dataclass(frozen=True)
class PortfolioSummary:
    portfolio_code: str
    portfolio_name: str
    base_ccy: str
    inception_date: date | None
    is_active: bool
    nav_obs_count: int
    first_nav_date: date | None
    latest_nav_date: date | None
    latest_nav: Decimal | None
    latest_nav_accum: Decimal | None


@dataclass(frozen=True)
class NavSeriesItem:
    nav_date: date
    nav: Decimal
    nav_accum: Decimal | None
    daily_return: Decimal | None


@dataclass(frozen=True)
class NavAnalysisSummary:
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


@dataclass(frozen=True)
class BatchIssueBreakdown:
    issue_type_counts: list[tuple[str, int]]
    severity_counts: list[tuple[str, int]]


@dataclass(frozen=True)
class BatchSummary:
    batch_id: int
    batch_key: str
    source_name: str
    dataset_name: str
    status: str
    row_count: int
    window_start: date | None
    window_end: date | None
    created_at: datetime
    completed_at: datetime | None
    linked_issue_count: int
    issue_breakdown: BatchIssueBreakdown


def list_portfolios(session: Session) -> list[PortfolioListItem]:
    rows = session.execute(select(Portfolio).order_by(Portfolio.portfolio_code)).scalars().all()
    return [
        PortfolioListItem(
            portfolio_code=row.portfolio_code,
            portfolio_name=row.portfolio_name,
            base_ccy=row.base_ccy,
            inception_date=row.inception_date,
            is_active=row.is_active,
        )
        for row in rows
    ]


def get_portfolio_summary(session: Session, portfolio_code: str) -> PortfolioSummary | None:
    portfolio = session.execute(
        select(Portfolio).where(Portfolio.portfolio_code == portfolio_code)
    ).scalars().first()
    if portfolio is None:
        return None

    nav_rows = session.execute(
        select(NavDaily.nav_date, NavDaily.nav, NavDaily.nav_accum)
        .where(NavDaily.portfolio_id == portfolio.id)
        .order_by(NavDaily.nav_date)
    ).all()

    if not nav_rows:
        return PortfolioSummary(
            portfolio_code=portfolio.portfolio_code,
            portfolio_name=portfolio.portfolio_name,
            base_ccy=portfolio.base_ccy,
            inception_date=portfolio.inception_date,
            is_active=portfolio.is_active,
            nav_obs_count=0,
            first_nav_date=None,
            latest_nav_date=None,
            latest_nav=None,
            latest_nav_accum=None,
        )

    first = nav_rows[0]
    latest = nav_rows[-1]
    return PortfolioSummary(
        portfolio_code=portfolio.portfolio_code,
        portfolio_name=portfolio.portfolio_name,
        base_ccy=portfolio.base_ccy,
        inception_date=portfolio.inception_date,
        is_active=portfolio.is_active,
        nav_obs_count=len(nav_rows),
        first_nav_date=first.nav_date,
        latest_nav_date=latest.nav_date,
        latest_nav=latest.nav,
        latest_nav_accum=latest.nav_accum,
    )


def get_nav_series(session: Session, portfolio_code: str) -> list[NavSeriesItem]:
    portfolio_id = session.scalar(select(Portfolio.id).where(Portfolio.portfolio_code == portfolio_code))
    if portfolio_id is None:
        return []

    rows = session.execute(
        select(NavDaily.nav_date, NavDaily.nav, NavDaily.nav_accum, NavDaily.daily_return)
        .where(NavDaily.portfolio_id == portfolio_id)
        .order_by(NavDaily.nav_date)
    ).all()
    return [NavSeriesItem(r.nav_date, r.nav, r.nav_accum, r.daily_return) for r in rows]


def get_nav_analysis_summary(session: Session, portfolio_code: str) -> NavAnalysisSummary | None:
    for item in analyze_nav(session):
        if item.portfolio_code == portfolio_code:
            return NavAnalysisSummary(
                portfolio_code=item.portfolio_code,
                obs_count=item.obs_count,
                start_date=item.start_date,
                end_date=item.end_date,
                latest_nav=item.latest_nav,
                cumulative_return=item.cumulative_return,
                average_daily_return=item.average_daily_return,
                min_daily_return=item.min_daily_return,
                max_daily_return=item.max_daily_return,
                max_drawdown=item.max_drawdown,
                annualized_volatility=item.annualized_volatility,
                win_rate=item.win_rate,
                monthly_returns=item.monthly_returns,
            )
    return None


def get_latest_batch_summary(session: Session) -> BatchSummary | None:
    latest = session.execute(
        select(DataBatch)
        .order_by(desc(DataBatch.created_at), desc(DataBatch.id))
    ).scalars().first()
    if latest is None:
        return None

    issue_type_counts = session.execute(
        select(DataIssueLog.issue_type, func.count())
        .where(DataIssueLog.batch_id == latest.id)
        .group_by(DataIssueLog.issue_type)
        .order_by(DataIssueLog.issue_type)
    ).all()
    severity_counts = session.execute(
        select(DataIssueLog.severity, func.count())
        .where(DataIssueLog.batch_id == latest.id)
        .group_by(DataIssueLog.severity)
        .order_by(DataIssueLog.severity)
    ).all()
    linked_issue_count = sum(int(v) for _, v in issue_type_counts)

    return BatchSummary(
        batch_id=latest.id,
        batch_key=latest.batch_key,
        source_name=latest.source_name,
        dataset_name=latest.dataset_name,
        status=latest.status,
        row_count=latest.row_count,
        window_start=latest.window_start,
        window_end=latest.window_end,
        created_at=latest.created_at,
        completed_at=latest.completed_at,
        linked_issue_count=linked_issue_count,
        issue_breakdown=BatchIssueBreakdown(
            issue_type_counts=[(k, int(v)) for k, v in issue_type_counts],
            severity_counts=[(k, int(v)) for k, v in severity_counts],
        ),
    )
