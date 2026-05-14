from __future__ import annotations

import sys
from pathlib import Path

from sqlalchemy import func, select

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from fdc.db.models import DataBatch, DataIssueLog, NavDaily, Portfolio
from fdc.db.session import get_session_local, resolve_database_url
from fdc.portfolio.nav_analysis import analyze_nav
from fdc.portfolio.report import (
    AnalysisSummary,
    ImportSummary,
    IssueSummary,
    PortfolioReportModel,
    PortfolioSummary,
    render_portfolio_report,
)

RUNTIME_REPORT = ROOT / "data" / "artifacts" / "reports" / "sample_portfolio_report.md"


if __name__ == "__main__":
    db_url = resolve_database_url()
    session_local = get_session_local(db_url)

    with session_local() as session:
        latest_batch = session.execute(select(DataBatch).where(DataBatch.dataset_name == "nav_daily").order_by(DataBatch.id.desc())).scalars().first()
        if latest_batch is None:
            raise RuntimeError("No nav_daily batch found. Run scripts/import_sample_nav.py first.")

        issue_type_counts = session.execute(
            select(DataIssueLog.issue_type, func.count())
            .where(DataIssueLog.batch_id == latest_batch.id)
            .group_by(DataIssueLog.issue_type)
            .order_by(DataIssueLog.issue_type)
        ).all()
        severity_counts = session.execute(
            select(DataIssueLog.severity, func.count())
            .where(DataIssueLog.batch_id == latest_batch.id)
            .group_by(DataIssueLog.severity)
            .order_by(DataIssueLog.severity)
        ).all()
        total_issues = sum(v for _, v in issue_type_counts)
        total_rows = int(latest_batch.row_count)
        # DataBatch stores source row_count, while rejected row totals are derived
        # from batch-linked issue logs in the current schema.
        rejected_rows = int(total_issues)
        accepted_rows = max(0, total_rows - rejected_rows)

        metrics = analyze_nav(session)
        if not metrics:
            raise RuntimeError("No NAV analysis metrics found. Run scripts/analyze_sample_nav.py prerequisites.")
        item = metrics[0]

        portfolio = session.execute(select(Portfolio).where(Portfolio.portfolio_code == item.portfolio_code)).scalars().first()
        if portfolio is None:
            raise RuntimeError("Portfolio not found for analysis output.")

        obs_count = session.scalar(select(func.count()).select_from(NavDaily).where(NavDaily.portfolio_id == portfolio.id)) or 0

    model = PortfolioReportModel(
        import_summary=ImportSummary(
            batch_id=latest_batch.id,
            batch_key=latest_batch.batch_key,
            status=latest_batch.status,
            total_rows=total_rows,
            accepted_rows=accepted_rows,
            rejected_rows=rejected_rows,
            window_start=latest_batch.window_start.isoformat() if latest_batch.window_start else None,
            window_end=latest_batch.window_end.isoformat() if latest_batch.window_end else None,
        ),
        issue_summary=IssueSummary(
            total_issues=total_issues,
            issue_type_counts=[(k, int(v)) for k, v in issue_type_counts],
            severity_counts=[(k, int(v)) for k, v in severity_counts],
        ),
        portfolio_summary=PortfolioSummary(
            portfolio_code=portfolio.portfolio_code,
            portfolio_name=portfolio.portfolio_name,
            obs_count=obs_count,
            latest_nav=item.latest_nav,
            start_date=item.start_date,
            end_date=item.end_date,
        ),
        analysis_summary=AnalysisSummary(
            cumulative_return=item.cumulative_return,
            max_drawdown=item.max_drawdown,
            annualized_volatility=item.annualized_volatility,
            win_rate=item.win_rate,
            monthly_returns=item.monthly_returns,
        ),
    )

    report = render_portfolio_report(model)
    RUNTIME_REPORT.parent.mkdir(parents=True, exist_ok=True)
    RUNTIME_REPORT.write_text(report, encoding="utf-8")
    print(f"Runtime report generated: {RUNTIME_REPORT}")
