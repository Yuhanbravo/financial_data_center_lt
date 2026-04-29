from __future__ import annotations

import csv
import logging
import os
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from fdc.db.models import DataBatch, DataIssueLog, NavDaily, Portfolio, utc_now
from .validation import REQUIRED_NAV_COLUMNS, ValidationIssue, validate_nav_rows


LOGGER = logging.getLogger(__name__)


@dataclass
class ImportResult:
    batch_id: int
    batch_key: str
    source_file: str
    staged_file: str
    status: str
    total_rows: int
    accepted_rows: int
    rejected_rows: int
    issue_counts: dict[str, int]
    date_min: str | None
    date_max: str | None


def seed_portfolios(session: Session, portfolio_csv_path: Path) -> int:
    with portfolio_csv_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    upserted = 0
    for row in rows:
        code = row["portfolio_code"].strip()
        existing = session.scalar(select(Portfolio).where(Portfolio.portfolio_code == code))
        inception = row.get("inception_date") or None
        if existing is None:
            session.add(
                Portfolio(
                    portfolio_code=code,
                    portfolio_name=row["portfolio_name"].strip(),
                    base_ccy=(row.get("base_ccy") or "USD").strip(),
                    inception_date=datetime.fromisoformat(inception).date() if inception else None,
                    is_active=_parse_bool(row.get("is_active"), default=True),
                )
            )
        else:
            existing.portfolio_name = row["portfolio_name"].strip()
            existing.base_ccy = (row.get("base_ccy") or existing.base_ccy).strip()
            existing.inception_date = datetime.fromisoformat(inception).date() if inception else existing.inception_date
            existing.is_active = _parse_bool(row.get("is_active"), default=existing.is_active)
        upserted += 1

    session.commit()
    return upserted


def import_nav_csv(
    session: Session,
    nav_csv_path: Path,
    source_name: str = "sample_csv",
    dataset_name: str = "nav_daily",
    artifacts_dir: Path | None = None,
) -> ImportResult:
    batch_key = f"nav_import_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')}_{uuid4().hex[:8]}"
    batch = DataBatch(
        batch_key=batch_key,
        source_name=source_name,
        dataset_name=dataset_name,
        status="pending",
        row_count=0,
    )
    session.add(batch)
    session.commit()

    try:
        raw_rows, fieldnames = _read_csv(nav_csv_path)
        batch.row_count = len(raw_rows)

        staged_file = _stage_source_artifact(nav_csv_path=nav_csv_path, batch_key=batch_key, artifacts_dir=artifacts_dir)

        missing_columns = sorted(REQUIRED_NAV_COLUMNS.difference(set(fieldnames)))
        if missing_columns:
            _log_issues(
                session,
                batch.id,
                [
                    ValidationIssue(
                        issue_type="missing_required_columns",
                        issue_message=f"Missing required columns: {', '.join(missing_columns)}",
                        record_key=None,
                    )
                ],
                table_name=dataset_name,
            )
            batch.status = "failed"
            batch.completed_at = utc_now()
            session.commit()
            return _build_result(
                batch,
                str(nav_csv_path),
                str(staged_file),
                0,
                len(raw_rows),
                {"missing_required_columns": 1},
                None,
                None,
            )

        code_to_id = {
            portfolio_code: portfolio_id
            for portfolio_code, portfolio_id in session.execute(select(Portfolio.portfolio_code, Portfolio.id)).all()
        }

        validation = validate_nav_rows(rows=raw_rows, known_portfolios=set(code_to_id.keys()))
        _log_issues(session, batch.id, validation.issues, table_name=dataset_name)

        accepted = 0
        nav_dates = []
        for item in validation.valid_rows:
            portfolio_id = code_to_id[item.portfolio_code]
            existing = session.scalar(
                select(NavDaily).where(NavDaily.portfolio_id == portfolio_id, NavDaily.nav_date == item.nav_date)
            )
            if existing is None:
                session.add(
                    NavDaily(
                        portfolio_id=portfolio_id,
                        nav_date=item.nav_date,
                        nav=item.nav,
                        nav_accum=item.nav_accum,
                        daily_return=item.daily_return,
                    )
                )
            else:
                existing.nav = item.nav
                existing.nav_accum = item.nav_accum
                existing.daily_return = item.daily_return
            accepted += 1
            nav_dates.append(item.nav_date)

        rejected = len(raw_rows) - accepted
        if accepted > 0 and rejected == 0:
            status = "success"
        elif accepted > 0:
            status = "partial"
        else:
            status = "failed"

        batch.status = status
        batch.window_start = min(nav_dates) if nav_dates else None
        batch.window_end = max(nav_dates) if nav_dates else None
        batch.completed_at = utc_now()
        session.commit()

        return _build_result(
            batch=batch,
            source_file=str(nav_csv_path),
            staged_file=str(staged_file),
            accepted_rows=accepted,
            rejected_rows=rejected,
            issue_counts=_count_issues(validation.issues),
            date_min=batch.window_start.isoformat() if batch.window_start else None,
            date_max=batch.window_end.isoformat() if batch.window_end else None,
        )
    except Exception:
        LOGGER.exception("NAV import batch %s failed unexpectedly", batch_key)
        try:
            _mark_batch_failed(session=session, batch_id=batch.id)
        except Exception:
            LOGGER.exception("Unable to mark NAV import batch %s failed", batch_key)
        raise


def _build_result(
    batch: DataBatch,
    source_file: str,
    staged_file: str,
    accepted_rows: int,
    rejected_rows: int,
    issue_counts: dict[str, int],
    date_min: str | None,
    date_max: str | None,
) -> ImportResult:
    return ImportResult(
        batch_id=batch.id,
        batch_key=batch.batch_key,
        source_file=source_file,
        staged_file=staged_file,
        status=batch.status,
        total_rows=batch.row_count,
        accepted_rows=accepted_rows,
        rejected_rows=rejected_rows,
        issue_counts=issue_counts,
        date_min=date_min,
        date_max=date_max,
    )


def _read_csv(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = reader.fieldnames or []
    return rows, fieldnames


def _stage_source_artifact(nav_csv_path: Path, batch_key: str, artifacts_dir: Path | None = None) -> Path:
    base_artifacts = artifacts_dir or _repo_root() / "data" / "artifacts"
    base_artifacts.mkdir(parents=True, exist_ok=True)

    raw_copy = base_artifacts / f"{batch_key}_{nav_csv_path.name}"
    shutil.copy2(nav_csv_path, raw_copy)

    if not _parquet_staging_enabled():
        return raw_copy

    parquet_path = raw_copy.with_suffix(".parquet")
    try:
        import pandas as pd

        frame = pd.read_csv(nav_csv_path)
        frame.to_parquet(parquet_path, index=False)
        return parquet_path
    except Exception as exc:
        LOGGER.warning("Parquet staging skipped for %s: %s", nav_csv_path, exc)
        return raw_copy


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _count_issues(issues: Iterable[ValidationIssue]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for issue in issues:
        counts[issue.issue_type] = counts.get(issue.issue_type, 0) + 1
    return counts


def _log_issues(session: Session, batch_id: int, issues: list[ValidationIssue], table_name: str = "nav_daily") -> None:
    if not issues:
        return

    session.add_all(
        [
            DataIssueLog(
                batch_id=batch_id,
                table_name=table_name,
                record_key=issue.record_key,
                issue_type=issue.issue_type,
                severity=issue.severity,
                issue_message=issue.issue_message,
            )
            for issue in issues
        ]
    )


def _parse_bool(raw: str | None, default: bool) -> bool:
    if raw is None:
        return default
    value = raw.strip().lower()
    if value in {"1", "true", "yes", "y"}:
        return True
    if value in {"0", "false", "no", "n"}:
        return False
    return default


def _parquet_staging_enabled() -> bool:
    raw = os.getenv("FDC_ENABLE_PARQUET_STAGING", "")
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _mark_batch_failed(session: Session, batch_id: int) -> None:
    session.rollback()
    failed_batch = session.get(DataBatch, batch_id)
    if failed_batch is None:
        LOGGER.warning("Unable to mark NAV import batch %s failed because it no longer exists", batch_id)
        return

    failed_batch.status = "failed"
    failed_batch.completed_at = utc_now()
    session.commit()
