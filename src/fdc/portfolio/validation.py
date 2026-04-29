from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation


REQUIRED_NAV_COLUMNS = {"portfolio_code", "trade_date", "nav", "nav_accum", "daily_return"}


@dataclass
class ValidationIssue:
    issue_type: str
    issue_message: str
    record_key: str | None
    severity: str = "error"


@dataclass
class ValidatedNavRow:
    portfolio_code: str
    nav_date: date
    nav: Decimal
    nav_accum: Decimal | None
    daily_return: Decimal | None


@dataclass
class NavValidationResult:
    valid_rows: list[ValidatedNavRow]
    issues: list[ValidationIssue]


def validate_nav_rows(rows: list[dict[str, str]], known_portfolios: set[str]) -> NavValidationResult:
    issues: list[ValidationIssue] = []
    valid_rows: list[ValidatedNavRow] = []
    seen_keys: set[tuple[str, date]] = set()

    for row_index, row in enumerate(rows, start=2):
        portfolio_code = (row.get("portfolio_code") or "").strip()
        trade_date_raw = (row.get("trade_date") or "").strip()
        nav_raw = (row.get("nav") or "").strip()
        nav_accum_raw = (row.get("nav_accum") or "").strip()
        daily_return_raw = (row.get("daily_return") or "").strip()

        record_key = f"{portfolio_code}|{trade_date_raw}" if portfolio_code or trade_date_raw else f"row:{row_index}"

        if portfolio_code not in known_portfolios:
            issues.append(
                ValidationIssue(
                    issue_type="unknown_portfolio_code",
                    issue_message=f"Unknown portfolio_code '{portfolio_code}' at source row {row_index}",
                    record_key=record_key,
                )
            )
            continue

        try:
            nav_date = date.fromisoformat(trade_date_raw)
        except ValueError:
            issues.append(
                ValidationIssue(
                    issue_type="invalid_trade_date",
                    issue_message=f"Invalid trade_date '{trade_date_raw}' at source row {row_index}",
                    record_key=record_key,
                )
            )
            continue

        try:
            nav_value = Decimal(nav_raw)
        except InvalidOperation:
            issues.append(
                ValidationIssue(
                    issue_type="invalid_nav",
                    issue_message=f"Invalid nav '{nav_raw}' at source row {row_index}",
                    record_key=record_key,
                )
            )
            continue

        if not nav_value.is_finite():
            issues.append(
                ValidationIssue(
                    issue_type="invalid_nav",
                    issue_message=f"Invalid nav '{nav_raw}' at source row {row_index}",
                    record_key=record_key,
                )
            )
            continue

        try:
            non_positive_nav = nav_value <= 0
        except InvalidOperation:
            issues.append(
                ValidationIssue(
                    issue_type="invalid_nav",
                    issue_message=f"Invalid nav '{nav_raw}' at source row {row_index}",
                    record_key=record_key,
                )
            )
            continue

        if non_positive_nav:
            issues.append(
                ValidationIssue(
                    issue_type="non_positive_nav",
                    issue_message=f"NAV must be > 0, got '{nav_raw}' at source row {row_index}",
                    record_key=record_key,
                )
            )
            continue

        row_key = (portfolio_code, nav_date)
        if row_key in seen_keys:
            issues.append(
                ValidationIssue(
                    issue_type="duplicate_source_key",
                    issue_message=(
                        "Duplicate (portfolio_code, trade_date) in source file; "
                        f"skipping later occurrence at source row {row_index}"
                    ),
                    record_key=f"{portfolio_code}|{nav_date.isoformat()}",
                )
            )
            continue
        seen_keys.add(row_key)

        try:
            nav_accum = Decimal(nav_accum_raw) if nav_accum_raw else None
            daily_return = Decimal(daily_return_raw) if daily_return_raw else None
        except InvalidOperation:
            issues.append(
                ValidationIssue(
                    issue_type="invalid_optional_numeric",
                    issue_message=(
                        "Invalid nav_accum or daily_return at source row "
                        f"{row_index}: nav_accum='{nav_accum_raw}', daily_return='{daily_return_raw}'"
                    ),
                    record_key=record_key,
                )
            )
            continue

        if (nav_accum is not None and not nav_accum.is_finite()) or (
            daily_return is not None and not daily_return.is_finite()
        ):
            issues.append(
                ValidationIssue(
                    issue_type="invalid_optional_numeric",
                    issue_message=(
                        "Invalid nav_accum or daily_return at source row "
                        f"{row_index}: nav_accum='{nav_accum_raw}', daily_return='{daily_return_raw}'"
                    ),
                    record_key=record_key,
                )
            )
            continue

        valid_rows.append(
            ValidatedNavRow(
                portfolio_code=portfolio_code,
                nav_date=nav_date,
                nav=nav_value,
                nav_accum=nav_accum,
                daily_return=daily_return,
            )
        )

    return NavValidationResult(valid_rows=valid_rows, issues=issues)
