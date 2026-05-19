from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from fdc.api.dependencies import get_db
from fdc.api.schemas import (
    BatchIssueBreakdownResponse,
    BatchSummaryResponse,
    ErrorResponse,
    HealthResponse,
    NavAnalysisResponse,
    NavObservationResponse,
    PortfolioListItem,
    PortfolioSummaryResponse,
)
from fdc.portfolio import query

router = APIRouter()


def _require_portfolio(session: Session, portfolio_code: str):
    summary = query.get_portfolio_summary(session, portfolio_code)
    if summary is None:
        raise HTTPException(status_code=404, detail=f"Portfolio not found: {portfolio_code}")
    return summary


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@router.get("/portfolios", response_model=list[PortfolioListItem])
def list_portfolios(session: Session = Depends(get_db)) -> list[PortfolioListItem]:
    items = query.list_portfolios(session)
    return [PortfolioListItem(**item.__dict__) for item in items]


@router.get("/portfolios/{portfolio_code}", response_model=PortfolioSummaryResponse, responses={404: {"model": ErrorResponse}})
def get_portfolio(portfolio_code: str, session: Session = Depends(get_db)) -> PortfolioSummaryResponse:
    summary = _require_portfolio(session, portfolio_code)
    return PortfolioSummaryResponse(**summary.__dict__)


@router.get("/portfolios/{portfolio_code}/nav", response_model=list[NavObservationResponse], responses={404: {"model": ErrorResponse}})
def get_portfolio_nav(portfolio_code: str, session: Session = Depends(get_db)) -> list[NavObservationResponse]:
    _require_portfolio(session, portfolio_code)
    series = query.get_nav_series(session, portfolio_code)
    return [NavObservationResponse(**row.__dict__) for row in series]


@router.get("/portfolios/{portfolio_code}/analysis", response_model=NavAnalysisResponse | None, responses={404: {"model": ErrorResponse}})
def get_portfolio_analysis(portfolio_code: str, session: Session = Depends(get_db)) -> NavAnalysisResponse | None:
    _require_portfolio(session, portfolio_code)
    summary = query.get_nav_analysis_summary(session, portfolio_code)
    if summary is None:
        return None
    return NavAnalysisResponse(**summary.__dict__)


@router.get("/batches/latest", response_model=BatchSummaryResponse | None)
def get_latest_batch(session: Session = Depends(get_db)) -> BatchSummaryResponse | None:
    latest = query.get_latest_batch_summary(session)
    if latest is None:
        return None
    payload = latest.__dict__.copy()
    payload["issue_breakdown"] = BatchIssueBreakdownResponse(**latest.issue_breakdown.__dict__)
    return BatchSummaryResponse(**payload)
