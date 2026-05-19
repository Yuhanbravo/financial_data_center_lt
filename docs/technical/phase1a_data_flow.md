# Phase 1A 数据流（Data Flow）

## 概览（Overview）

Phase 1A 使用仓库内置 sample CSV 在本地演示组合层数据流。流程从 sample data 开始，写入 SQLite 规范化表，生成 runtime reports，并提供 read-only structured queries。

```text
data/sample/*.csv
  -> scripts/import_sample_nav.py
  -> portfolio, data_batch, data_issue_log, nav_daily
  -> scripts/analyze_sample_nav.py
  -> runtime NAV analysis report
  -> scripts/generate_sample_portfolio_report.py
  -> runtime portfolio report
  -> scripts/query_sample_portfolio.py
  -> read-only structured query output
```

## Sample CSV 到 SQLite 的导入路径

导入入口是 `scripts/import_sample_nav.py`，它复用 `src/fdc/portfolio/` 下的 import 与 validation 模块。

输入文件：
- `data/sample/portfolio_sample.csv`
- `data/sample/nav_daily_sample.csv`
- `data/sample/nav_daily_sample_with_issues.csv`

运行期输出和 staged artifacts 写入 `data/artifacts/`。该目录由 Git ignore，不作为版本化交付物。

## 关键表（Key Tables）

### `portfolio`

组合主数据表。用于定义 portfolio identity，例如 portfolio code、name、base currency、inception date 和 active status。

### `data_batch`

批次元数据表。记录 import / processing run 的 source name、dataset name、status、row count、time window 和 lifecycle timestamps。

### `data_issue_log`

数据质量与校验问题表。用于记录 issue type、severity、message、record key，并在可能时关联到 batch。

### `nav_daily`

组合日频 NAV 事实表。它是 Phase 1A NAV analysis 和 query behavior 的主要事实来源。

### `portfolio_metric_daily`

预留的组合指标表。Phase 1A-3、1A-4 和 1A-5A 不向该表写入 analysis outputs；当前它也不是生成指标的事实源。

## Phase 关系（Phase Relationships）

- Phase 1A-2：将 sample portfolio 与 NAV 数据导入 SQLite，并记录 batch 和 issue。
- Phase 1A-3：读取 `nav_daily`，计算组合层 NAV analysis，不持久化 metrics。
- Phase 1A-4：组合 import 与 analysis 输出，生成确定性的 sample portfolio Markdown report。
- Phase 1A-5A：基于当前 SQLite sample workflow 暴露 read-only structured query functions。

## 报告边界（Report Boundaries）

稳定示例报告位于 `docs/reports/`，作为 versioned review baseline。

运行期报告位于 `data/artifacts/reports/`，不提交到 Git：
- `data/artifacts/reports/sample_nav_import_report.md`
- `data/artifacts/reports/sample_nav_analysis_report.md`
- `data/artifacts/reports/sample_portfolio_report.md`

不要把 runtime reports 复制到 `docs/reports/`。如果 stable example report 需要更新，应通过 reviewed task package 修改对应 `.example.md` 文件。
