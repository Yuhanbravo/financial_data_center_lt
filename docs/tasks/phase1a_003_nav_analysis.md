# Task Package: phase1a_003_nav_analysis

## 1. task_id
- `phase1a_003_nav_analysis`

## 2. title
- Phase 1A-3: Portfolio NAV Analysis MVP

## 3. context
- Phase 1A-0 / Phase 1A-1 已完成项目骨架、SQLAlchemy models、SQLite 初始化能力与 schema 文档。
- Phase 1A-2 已完成 sample NAV import pipeline，当前仓库已经具备：synthetic sample data、portfolio seed、`nav_daily` 导入、`data_batch` 批次跟踪、`data_issue_log` 记录、repeatable import、runtime import report、smoke tests。
- 当前下一步应复用已导入的 `nav_daily` 数据，打通最小分析闭环：SQLite `nav_daily` -> Python NAV analysis -> runtime Markdown report -> stable example report -> smoke tests。
- 本阶段目标是交付“最小、可验证、可展示”的组合 NAV 分析能力，而不是扩展到更复杂的业绩归因、风控或多资产估值体系。

## 4. objective
- 基于 SQLite 中现有的 `nav_daily` 数据，实现组合级 NAV 基础分析能力。
- 输出一份运行期 Markdown 分析报告到 `data/artifacts/reports/`，并同步维护一份稳定示例报告到 `docs/reports/`。
- 提供一个可重复执行的脚本 `scripts/analyze_sample_nav.py`，用于对 sample NAV 数据执行分析并生成报告。
- 增加 smoke tests，验证分析链路可运行、关键指标口径稳定、输出文件符合约束。

## 5. scope
- 新增 `src/fdc/portfolio/nav_analysis.py`，封装从 `nav_daily` 查询、排序、计算、聚合、格式化输出所需的最小分析逻辑。
- 新增 `scripts/analyze_sample_nav.py`，直接使用 `D:\miniforge3\envs\data-center-py312\python.exe` 可运行，读取 SQLite 中已导入的 sample NAV 数据并生成分析报告。
- 新增 `tests/test_nav_analysis_smoke.py`，覆盖最小分析闭环和关键指标断言。
- 新增稳定示例报告 `docs/reports/sample_nav_analysis_report.example.md`。
- 更新 `docs/HANDOFF.md`，将当前阶段推进到 Phase 1A-3 并记录本阶段交付、验证命令与下一步建议。
- 允许在不修改既有 schema 设计意图的前提下，修复实现层发现的明确 bug；若无明确 bug，不修改已有 schema。

## 6. out_of_scope
- 不新增真实生产数据，不接外部系统，不引入 Wind、Oracle、PostgreSQL。
- 不新增 benchmark、market data、holdings、trades、instruments。
- 不实现业绩归因、Brinson、风控指标、因子分析、回测框架。
- 不实现 FastAPI、frontend、任务调度、异步 worker。
- 不引入 pandas、numpy 作为核心依赖。
- 不将本阶段扩展为通用报表平台或多组合批量分析系统。
- 不修改已有 schema，除非定位到影响本阶段交付的明确 bug。
- 不要求在本阶段把分析结果回写到 `portfolio_metric_daily`；如需持久化，另起后续任务包。

## 7. authorized files
- `src/fdc/portfolio/nav_analysis.py`
- `scripts/analyze_sample_nav.py`
- `tests/test_nav_analysis_smoke.py`
- `docs/tasks/phase1a_003_nav_analysis.md`
- `docs/reports/sample_nav_analysis_report.example.md`
- `docs/HANDOFF.md`

## 8. implementation requirements
- 仅使用 Python 标准库 + SQLAlchemy；不得把 pandas / numpy 作为核心实现前提。
- 分析输入以 SQLite 中的 `nav_daily` 为准，不从新增 CSV 或其他外部数据源直接计算。
- 默认分析 sample 数据涉及的组合；脚本应至少支持对单个 `portfolio_code` 生成报告，若仓库当前已有多个 sample 组合，可在一个报告中逐组合分节展示。
- `nav_analysis.py` 应尽量保持纯函数化或接近纯函数化的计算接口，数据库读取与指标计算职责分离，便于测试。
- NAV 读取后可在 MVP 范围内统一转换为 `float` 进行指标计算，或统一使用 `Decimal`；无论采用哪种方案，都必须在 `nav_analysis.py` 中集中处理数值转换边界，避免在脚本、报告、测试中混用口径。
- 所有计算前必须按 `trade_date` 升序排序；若同一组合无有效观察值，应显式报错或返回可识别的空结果，不得静默生成误导性指标。
- 日收益率序列应从相邻两个有效 NAV 观测值计算，首个观测日不产生日收益率。
- 脚本输出必须是 Markdown 文本，结构清晰、可直接查看，不依赖 notebook、HTML 或前端页面。
- 报告输出中的数值字段必须统一格式化规则，例如固定小数位或百分比格式；同一指标在报告不同位置不得使用不同格式。
- runtime report 路径应稳定命名为 `data/artifacts/reports/sample_nav_analysis_report.md`；脚本允许覆盖此前运行结果。
- `docs/reports/sample_nav_analysis_report.example.md` 为稳定示例文件，内容应使用固定占位值或来自当前 sample 数据的一组稳定示例，不应包含每次运行变化的时间戳、绝对路径、随机 batch key 或其他不稳定内容。
- smoke tests 应覆盖：分析脚本可运行、核心指标计算正确、Markdown 报告生成、示例报告存在且结构稳定。
- 测试不得依赖二进制浮点完全相等；若实现使用 `float`，应采用近似比较；若实现使用 `Decimal`，应断言固定量化后的结果。
- 如发现现有导入链路中的数据边界会影响分析正确性，可在 execution report 中记录风险，但本任务包不要求顺带扩展导入口径。

## 9. metric definitions
- `date range`
  - 定义：某组合在本次分析样本中的最小 `trade_date` 与最大 `trade_date`。
- `observation count`
  - 定义：参与分析的有效 NAV 观测数量，即有效 `trade_date`-`nav` 点位数。
- `latest nav`
  - 定义：样本期末最新交易日对应的 NAV 值。
- `cumulative return`
  - 定义：`latest_nav / first_nav - 1`。
  - 前提：至少有 2 个有效 NAV 观测值；若只有 1 个观测值，可返回 `0` 或显式标记为不足样本，但口径必须在代码和报告中保持一致。
- `daily return series`
  - 定义：按日期升序，对每个非首日观测计算 `current_nav / previous_nav - 1`。
  - 输出：报告中至少展示摘要信息；测试中应能访问完整序列或其核心值。
- `max drawdown`
  - 定义：基于累计最高 NAV 计算回撤，公式为 `nav / running_peak - 1`，取全样本最小值。
- `simple annualized volatility`
  - 定义：基于日收益率序列的样本标准差乘以 `sqrt(252)`。
  - 样本标准差使用 `n-1` 分母，即 sample standard deviation / `ddof=1`。
  - 前提：至少有 2 个有效日收益率观测值；若不足，annualized volatility 返回 `0` 或 `N/A`，但代码、报告、测试必须保持一致。
- `win rate`
  - 定义：日收益率大于 `0` 的天数 / 有效日收益率观测天数。
  - 说明：日收益率等于 `0` 视为非赢。
- `monthly return table`
  - 定义：按自然月分组，以月末 NAV 相对于上一个月末 NAV 的变化率计算月收益。
  - 说明：即使样例数据只覆盖一个自然月，monthly return table 也必须在报告中出现。
  - 说明：首个自然月若缺少前一月月末 NAV，可将首月标记为 `N/A`，并明确说明因为缺少前一月月末 NAV，因此不计算月收益。

## 10. runtime artifact rules
- 所有运行期生成物必须输出到 `data/artifacts/reports/`。
- 本阶段运行期分析报告文件名固定为 `sample_nav_analysis_report.md`。
- 运行期生成物不得写入 `docs/reports/`。
- `docs/reports/` 仅保留稳定 example report：`docs/reports/sample_nav_analysis_report.example.md`。
- runtime report 可以包含本次运行实际日期范围、组合代码、指标值；但应避免写入不可复现的噪声信息。
- stable example report 不应包含会在每次执行中变化的运行时间戳、绝对文件路径、随机标识符。
- 若脚本需要打印控制台摘要，控制台输出应与 Markdown 报告内容一致或为其简化版，不得出现互相矛盾的数据。

## 11. validation commands
```powershell
Cloud validation:
python scripts/init_sqlite.py
python scripts/import_sample_nav.py
python scripts/analyze_sample_nav.py
python -m pytest -q

Local Windows Gate:
D:\miniforge3\envs\data-center-py312\python.exe scripts/init_sqlite.py
D:\miniforge3\envs\data-center-py312\python.exe scripts/import_sample_nav.py
D:\miniforge3\envs\data-center-py312\python.exe scripts/analyze_sample_nav.py
D:\miniforge3\envs\data-center-py312\python.exe -m pytest -q
```

## 12. acceptance criteria
1. `D:\miniforge3\envs\data-center-py312\python.exe scripts/init_sqlite.py` 成功执行并准备 SQLite 数据库。
2. `D:\miniforge3\envs\data-center-py312\python.exe scripts/import_sample_nav.py` 成功导入 sample NAV 数据。
3. `D:\miniforge3\envs\data-center-py312\python.exe scripts/analyze_sample_nav.py` 成功生成 runtime Markdown report 到 `data/artifacts/reports/sample_nav_analysis_report.md`。
4. runtime report 至少包含以下内容：组合标识、date range、observation count、latest nav、cumulative return、max drawdown、simple annualized volatility、win rate、monthly return table。
5. `docs/reports/sample_nav_analysis_report.example.md` 已存在，结构与 runtime report 对齐，但内容保持稳定、可提交。
6. `D:\miniforge3\envs\data-center-py312\python.exe -m pytest -q` 通过，且包含 `tests/test_nav_analysis_smoke.py` 对核心分析链路的覆盖。
7. 实现中未引入 pandas / numpy，未新增真实数据，未扩展到 benchmark、market data、holdings、trades、instruments、FastAPI、frontend、PostgreSQL、Alembic。
8. 未修改已有 schema；若因明确 bug 必须修改，execution report 必须说明 bug、原因、影响范围与同步更新项。
9. 本阶段交付能够向他人直接展示一个最小但完整的 NAV 分析闭环，而不是仅提供零散函数或未落盘的计算结果。

## 13. execution report requirements
执行报告必须包含以下内容：
1. `task_id` 与 objective restatement。
2. 实际变更文件列表。
3. 实现摘要，说明数据库读取、指标计算、报告生成、测试覆盖分别如何完成。
4. 各指标口径说明，尤其是日收益率、年化波动率、最大回撤、月收益表的具体定义与边界处理。
5. runtime artifact 与 stable example report 的实际输出路径。
6. 验证命令及结果，必须逐条记录本任务包列出的 Cloud validation 与 Local Windows Gate 两组命令，或明确说明本次实际执行了其中哪一组。
7. 若存在偏离 task package 的实现决策，需明确记录偏离原因。
8. out-of-scope 项确认，说明本阶段刻意未做的内容。
9. 已知限制与后续建议，优先指向下一阶段可选增强，例如是否需要将分析结果持久化到 `portfolio_metric_daily`。