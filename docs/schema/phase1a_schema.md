# Phase 1A Schema（组合层）

> 说明：以下为 Phase 1A 最小 schema，面向 SQLite 实现并保持 PostgreSQL 可迁移性。

## 1) portfolio

### 定位
组合主数据维表。

### 字段
- `id`：INTEGER，主键
- `portfolio_code`：STRING(64)，组合代码，非空，唯一
- `portfolio_name`：STRING(255)，组合名称，非空
- `base_ccy`：STRING(16)，基准币种，非空，默认 `CNY`
- `inception_date`：DATE，可空
- `is_active`：BOOLEAN，非空，默认 `true`
- `created_at`：DATETIME，非空
- `updated_at`：DATETIME，非空

### 约束
- 唯一约束：`uq_portfolio_code(portfolio_code)`

### 阶段边界
不包含策略参数、账户体系映射、组织权限信息。

---

## 2) data_batch

### 定位
记录每次数据处理批次元信息，用于追踪与审计。

### 字段
- `id`：INTEGER，主键
- `batch_key`：STRING(128)，批次标识，非空，唯一
- `source_name`：STRING(128)，数据来源名，非空
- `dataset_name`：STRING(128)，数据集名，非空
- `window_start`：DATE，可空
- `window_end`：DATE，可空
- `status`：STRING(32)，非空（如 `pending/success/failed`）
- `row_count`：INTEGER，非空，默认 0
- `created_at`：DATETIME，非空
- `completed_at`：DATETIME，可空

### 约束
- 唯一约束：`uq_data_batch_batch_key(batch_key)`

### 阶段边界
不包含任务调度 DAG、重试拓扑、分布式执行元数据。

---

## 3) data_issue_log

### 定位
记录数据质量问题与校验告警。

### 字段
- `id`：INTEGER，主键
- `batch_id`：INTEGER，外键 -> `data_batch.id`，可空
- `table_name`：STRING(128)，非空
- `record_key`：STRING(255)，可空
- `issue_type`：STRING(64)，非空（如 `missing_field`）
- `severity`：STRING(16)，非空（如 `info/warn/error`）
- `issue_message`：STRING(1000)，非空
- `created_at`：DATETIME，非空

### 约束
- 索引建议：`batch_id`, `table_name`, `issue_type`

### 阶段边界
仅记录日志，不实现自动修复闭环。

---

## 4) nav_daily

### 定位
组合日频净值事实表。

### 字段
- `id`：INTEGER，主键
- `portfolio_id`：INTEGER，外键 -> `portfolio.id`，非空
- `nav_date`：DATE，非空
- `nav`：NUMERIC(20,8)，非空
- `nav_accum`：NUMERIC(20,8)，可空
- `daily_return`：NUMERIC(12,8)，可空
- `created_at`：DATETIME，非空
- `updated_at`：DATETIME，非空

### 约束
- 唯一约束：`uq_nav_daily_portfolio_date(portfolio_id, nav_date)`

### 阶段边界
不包含复权链路与份额变动拆解。

---

## 5) portfolio_metric_daily

### 定位
组合日频指标表（key-value 结构，便于增量扩展）。

### 字段
- `id`：INTEGER，主键
- `portfolio_id`：INTEGER，外键 -> `portfolio.id`，非空
- `metric_date`：DATE，非空
- `metric_name`：STRING(64)，非空（如 `vol_20d`）
- `metric_value`：NUMERIC(20,8)，非空
- `metric_unit`：STRING(32)，可空
- `created_at`：DATETIME，非空

### 约束
- 唯一约束：`uq_metric_daily_portfolio_date_name(portfolio_id, metric_date, metric_name)`

### 阶段边界
不包含复杂衍生指标计算流程，仅承接结果落库。
