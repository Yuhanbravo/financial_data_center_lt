from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, field_serializer


class DecimalStringModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    @field_serializer("*", when_used="json")
    def serialize_decimal(self, value):
        if isinstance(value, Decimal):
            return str(value)
        return value


class HealthResponse(DecimalStringModel):
    status: str


class PortfolioListItem(DecimalStringModel):
    portfolio_code: str
    portfolio_name: str
    base_ccy: str
    inception_date: date | None
    is_active: bool


class PortfolioSummaryResponse(PortfolioListItem):
    nav_obs_count: int
    first_nav_date: date | None
    latest_nav_date: date | None
    latest_nav: Decimal | None
    latest_nav_accum: Decimal | None


class NavObservationResponse(DecimalStringModel):
    nav_date: date
    nav: Decimal
    nav_accum: Decimal | None
    daily_return: Decimal | None


class NavAnalysisResponse(DecimalStringModel):
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


class BatchIssueBreakdownResponse(DecimalStringModel):
    issue_type_counts: list[tuple[str, int]]
    severity_counts: list[tuple[str, int]]


class BatchSummaryResponse(DecimalStringModel):
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
    issue_breakdown: BatchIssueBreakdownResponse


class ErrorResponse(DecimalStringModel):
    detail: str
