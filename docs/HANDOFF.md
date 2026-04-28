# HANDOFF（SSOT）

## 1. 当前阶段
- 阶段：Phase 1A-2（样例 NAV 导入流水线）
- 日期：2026-04-28
- 状态：已完成（代码与验证已收敛）

## 2. 已完成内容
- 新增样例数据：
  - `data/sample/portfolio_sample.csv`
  - `data/sample/nav_daily_sample.csv`
  - `data/sample/nav_daily_sample_with_issues.csv`
- 实现可复用 NAV 导入能力：
  - `seed_portfolios`：portfolio 主数据 seed/upsert
  - `import_nav_csv`：批次创建、校验、写入、issue log、状态落盘
- 完成校验规则：
  - 必需列检查（缺列直接 failed + `missing_required_columns` issue）
  - unknown portfolio_code / invalid trade_date / nav<=0 / duplicate_source_key
- 脚本 `scripts/import_sample_nav.py`：
  - 先 seed portfolio，再导入样例 NAV
  - 运行期报告输出到 `data/artifacts/reports/sample_nav_import_report.md`（不入库）
- smoke tests 覆盖：
  - 成功导入
  - 带问题数据的 partial 导入 + issue logging
  - 缺失必需列失败路径
  - FK-safe 行为（unknown portfolio 不写入 nav_daily）
  - 重复执行导入（无 unique constraint 失败）

## 3. 校验命令与结果（本次实际执行）
- `python scripts/init_sqlite.py`：通过
- `python scripts/import_sample_nav.py`：通过（生成 batch + 运行期报告）
- `pytest`：通过（全部通过）

## 4. 未完成内容（按阶段边界刻意留空）
- 持仓层（positions）
- 交易层（trades）
- 行情接入（Wind/第三方 API）
- FastAPI 服务层
- 前端查询
- PostgreSQL 迁移脚本与部署流水线
- 复杂指标计算/回测口径

## 5. 明确边界（本阶段不做）
- 不接真实生产数据，不进行外部系统联调。
- 不接 Wind / Oracle / PostgreSQL。
- 不实现 API、前端。
- 不扩展到组合穿透分析、风控引擎、多资产估值。

## 6. 下一步推荐任务（优先级）
1. **Phase 1A-3：组合 NAV 分析能力**
   - 在现有 `nav_daily` 基础上实现组合级 NAV 分析与验证闭环
   - `portfolio_metric_daily` ingestion 作为后续可选增强（非本阶段必做）
2. **Phase 1B：持仓/交易/标的层扩展**
   - holdings / positions / trades / instruments 分层建模

## 7. 接手提示
- 先阅读：
  1) `docs/blueprint/IMPLEMENTATION_BLUEPRINT.md`
  2) `docs/blueprint/PHASE1A_PLAN.md`
  3) `docs/schema/phase1a_schema.md`
- 变更模型字段时，同步更新 schema 文档与测试断言，保持“文档与实现一致”。
