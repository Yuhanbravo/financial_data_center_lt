# HANDOFF（SSOT）

## 1. 当前阶段
- 阶段：Phase 1A-4（Portfolio NAV Report / Display MVP）
- 日期：2026-05-13
- 状态：当前完成 / 待合并

## 2. 本阶段交付（Phase 1A-4）
- 新增 `src/fdc/portfolio/report.py`：
  - 组合层报告模型与 Markdown 渲染器（deterministic）。
  - 报告结构固定为：Overview / Import / Issue / Portfolio / NAV Analysis / Monthly Return / Method / Limitations。
- 新增 `scripts/generate_sample_portfolio_report.py`：
  - 从 SQLite 样例工作流结果组装输入（`data_batch`、`data_issue_log`、`portfolio`、`nav_daily`、Phase 1A-3 分析结果）。
  - 输出运行期报告到 `data/artifacts/reports/sample_portfolio_report.md`。
- 新增 `docs/reports/sample_portfolio_report.example.md`：稳定示例报告（不含时间戳/绝对路径/随机噪声）。
- 新增 `tests/test_portfolio_report_smoke.py`：
  - 校验运行期报告生成。
  - 校验稳定示例存在且正常脚本运行不覆盖。
  - 校验报告必需章节。
  - 校验不写 `portfolio_metric_daily`。
  - 校验未引入 pandas/numpy 作为核心依赖。

## 3. 校验命令与结果（本次实际执行）
Cloud validation（实际执行）：
- `python scripts/init_sqlite.py`：通过
- `python scripts/import_sample_nav.py`：通过
- `python scripts/analyze_sample_nav.py`：通过
- `python scripts/generate_sample_portfolio_report.py`：通过
- `python -m pytest -q`：通过

Local Windows Gate（`D:\miniforge3\envs\data-center-py312\python.exe`）：未验证（当前环境非 Windows）。

## 4. 关键边界确认
- 未新增 API/FastAPI/frontend/UI。
- 未引入 holdings/positions/trades/instruments。
- 未接入 benchmark/market data。
- 未引入 PostgreSQL/Alembic。
- 未接入真实数据。
- 未写入/持久化 `portfolio_metric_daily`。
- 未新增 pandas/numpy 核心依赖。

## 5. 下一步建议（不把 1A-4 作为下一步）
1. Phase 1A-5：在保持 SQLite 样例边界下补充报告一致性回归（多组合排序、异常批次显示策略、跨月样例覆盖）。
2. Phase 1B 规划：在独立任务包中定义 holdings/trades/instruments 分层与口径（仍与当前 1A 边界解耦）。
