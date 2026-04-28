# Sample NAV Import Report (Example)

- Batch ID: `<batch_id>`
- Batch Key: `<batch_key>`
- Source file: `data/sample/nav_daily_sample.csv`
- Staged artifact: `data/artifacts/<batch_key>_nav_daily_sample.parquet`
- Batch status: `success|partial|failed`
- Total rows: `<total_rows>`
- Accepted rows: `<accepted_rows>`
- Rejected rows: `<rejected_rows>`
- Date range: `<date_min>` to `<date_max>`

## Issue Summary
- `missing_required_columns`: `<count>`
- `unknown_portfolio_code`: `<count>`
- `invalid_trade_date`: `<count>`
- `non_positive_nav`: `<count>`
- `duplicate_source_key`: `<count>`
