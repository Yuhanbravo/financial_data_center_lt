# Sample Portfolio Report

## Report Overview
- This report composes Phase 1A-2 SQLite import outputs and Phase 1A-3 NAV analysis outputs.
- Scope: deterministic sample reporting MVP (no API/frontend, no portfolio_metric_daily persistence).

## Import Summary
- Batch ID: `1`
- Batch Key: `nav_import_example`
- Status: `success`
- Rows (total/accepted/rejected): `4` / `4` / `0`
- Date window: `2026-01-02` to `2026-01-03`

## Issue Summary
- Total issues: `0`
- Issue type breakdown: none
- Severity breakdown: none

## Portfolio Summary
- Portfolio: `PF_DEMO_A` (Demo Growth Portfolio A)
- Observation count: `2`
- Date range: `2026-01-02` to `2026-01-03`
- Latest NAV: `1.00250000`

## NAV Analysis Summary
- Cumulative return: `0.2500%`
- Max drawdown: `0.0000%`
- Annualized volatility (ddof=1): `n/a`
- Win rate: `100.0000%`

## Monthly Return Table
| Month | Return |
|---|---:|
| 2026-01 | n/a |

## Method Notes
- Data lineage: sample SQLite initialization + sample NAV import + Phase 1A-3 NAV analysis reuse.
- Import Summary row counts use latest batch row_count minus batch-linked issue log count.
- Determinism: section order, metric formatting, and table ordering are fixed.

## Known Limitations and Next Steps
- Synthetic sample data only.
- No benchmark or market data integration.
- No holdings/positions layer.
- No API/frontend delivery in this phase.
- No portfolio_metric_daily persistence.
