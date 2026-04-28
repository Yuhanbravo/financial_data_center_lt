from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .session import Base


def utc_now() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


class Portfolio(Base):
    __tablename__ = "portfolio"
    __table_args__ = (UniqueConstraint("portfolio_code", name="uq_portfolio_code"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    portfolio_code: Mapped[str] = mapped_column(String(64), nullable=False)
    portfolio_name: Mapped[str] = mapped_column(String(255), nullable=False)
    base_ccy: Mapped[str] = mapped_column(String(16), nullable=False, default="CNY")
    inception_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utc_now, onupdate=utc_now)


class DataBatch(Base):
    __tablename__ = "data_batch"
    __table_args__ = (UniqueConstraint("batch_key", name="uq_data_batch_batch_key"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    batch_key: Mapped[str] = mapped_column(String(128), nullable=False)
    source_name: Mapped[str] = mapped_column(String(128), nullable=False)
    dataset_name: Mapped[str] = mapped_column(String(128), nullable=False)
    window_start: Mapped[date | None] = mapped_column(Date, nullable=True)
    window_end: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    row_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utc_now)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class DataIssueLog(Base):
    __tablename__ = "data_issue_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    batch_id: Mapped[int | None] = mapped_column(ForeignKey("data_batch.id"), nullable=True, index=True)
    table_name: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    record_key: Mapped[str | None] = mapped_column(String(255), nullable=True)
    issue_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    severity: Mapped[str] = mapped_column(String(16), nullable=False)
    issue_message: Mapped[str] = mapped_column(String(1000), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utc_now)


class NavDaily(Base):
    __tablename__ = "nav_daily"
    __table_args__ = (UniqueConstraint("portfolio_id", "nav_date", name="uq_nav_daily_portfolio_date"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    portfolio_id: Mapped[int] = mapped_column(ForeignKey("portfolio.id"), nullable=False)
    nav_date: Mapped[date] = mapped_column(Date, nullable=False)
    nav: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False)
    nav_accum: Mapped[Decimal | None] = mapped_column(Numeric(20, 8), nullable=True)
    daily_return: Mapped[Decimal | None] = mapped_column(Numeric(12, 8), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utc_now, onupdate=utc_now)


class PortfolioMetricDaily(Base):
    __tablename__ = "portfolio_metric_daily"
    __table_args__ = (
        UniqueConstraint(
            "portfolio_id",
            "metric_date",
            "metric_name",
            name="uq_metric_daily_portfolio_date_name",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    portfolio_id: Mapped[int] = mapped_column(ForeignKey("portfolio.id"), nullable=False)
    metric_date: Mapped[date] = mapped_column(Date, nullable=False)
    metric_name: Mapped[str] = mapped_column(String(64), nullable=False)
    metric_value: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False)
    metric_unit: Mapped[str | None] = mapped_column(String(32), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utc_now)
