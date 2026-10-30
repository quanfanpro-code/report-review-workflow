# report-review-workflow 自包含改造与开源 · 需求文档

- 日期：2026-10-30
- 流程：requirement-workflow 阶段 1（需求澄清）
- 状态：待 CHECKPOINT 1 用户确认

---

## 一、背景与问题

report-review-workflow 是财务/审计/专项报告全面复核的"指挥家"技能（七步法编排层）。当前存在三个问题：

1. **不自包含**：第二步实时引用外部技能 audit-report-checker（相对路径指向技能库邻居目录），第三至七步引用 2026-07-09 冻结的上游副本（tianchuan-perspective、chen-yiwei-perspective、private-equity-investment-dd、writing、huaxin-format）。上游更新需手动同步，换机或缺邻居目录即失效。
2. **未开源**：GitHub 上没有 report-review-workflow 仓库（2026-10-30 经 gh 检索确认）。
3. **文字质量审查不含去 AI 味能力**：用户明确要求并入 humanizer-zh（去 AI 味）与 human-writing（活人感写作）。

## 二、用户与使用场景

- **用户**：Q老师，审计实务工作者，零编程基础。
- **场景一（日常复核）**：在 WorkBuddy 中说"复核报告 / 审报告 / 全面复核"触发，对报告做七步复核，产出问题清单 + 修改版报告。要求改造后在本机技能库中继续直接可用。
- **场景二（开源分发）**：GitHub 访客访问 quanfanpro-code/report-review-workflow，零基础读者仅凭 README 即可看懂这个技能是干什么的、怎么用、内部怎么运转。

## 三、功能范围

1. **整合七个上游为包内资源**，运行时只读本技能目录，不再依赖任何外部技能：
   | 上游 | 用途 | 许可 |
   |---|---|---|
   | audit-report-checker | 第二步数据核对（含 scripts、tests） | AGPL-3.0（原创） |
   | tianchuan-perspective | 第三步审计逻辑审查 | MIT |
   | chen-yiwei-perspective | 第四步会计准则审查 | MIT |
   | officecli-huaxin-format | 第七步华信排版审查 | 权利人授权并入（选项 A） |
   | writing | 第六步文字质量审查（写作规范） | MIT |
   | humanizer-zh | 第六步新增（去 AI 味） | MIT |
   | human-writing | 第六步新增（活人感写作） | MIT |
2. **文字质量审查扩充**：writing + humanizer-zh + human-writing 三家内容并入，实现"去 AI 味"。
3. **形态对齐 requirement-workflow**：SKILL.md 编排层 + references/ 内置全部资料 + references/SOURCES.json 来源台账 + NOTICE 第三方声明 + references/licenses/ 原始许可全文 + LICENSE（AGPL-3.0）+ docs/ 开发档案（文字记录）+ scripts/。
4. **打包范围（选项 B）**：运行时必需内容 + 开发档案的文字记录进 docs/；**不搬**大体积样本文件（合成原件、提取产物等，约 153M）。
5. **改造完成后用达尔文技能（darwin-skill）评估并优化**。
6. **写 README.md**：带 emoji；禁止代码块、变量名、命令行；禁止非常用英文缩写；详述使用方式、运行逻辑、输入要求、输出内容；零基础读者可懂。
7. **开源推送**：公开仓库 quanfanpro-code/report-review-workflow，主协议 AGPL-3.0。

## 四、明确不做的内容

- **不整合 private-equity-investment-dd（PE 尽调视角）的任何内容**（其许可为"保留所有权利、仅供私用"，与 AGPL 公开分发不兼容）；技能内保留"该视角未整合"标注。
- 不搬运 audit-report-checker docs/reviews 下约 153M 的开发留痕样本（合成原件、提取产物、大型 JSON）。
- 不修改各上游技能的原目录（只读复制，原技能照常独立可用）。
- 不做 Gitee 同步（用户未要求）。
- 不改技能名称与触发词（复核报告、审报告、全面复核）。

## 五、约束与风险

- **许可合规**：MIT 组件并入 AGPL 仓库合法，但须在 NOTICE + references/licenses/ 保留各自 MIT 许可全文；officecli-huaxin-format 原文无许可声明，已获权利人明确授权（选项 A）以 AGPL-3.0 并入，NOTICE 中注明"由权利人授权并入"。
- **第五步空缺**：PE 尽调视角排除后，七步法第五步降级为"标注未整合 + 按现行 Fallback 手动检查资产/负债端明显异常项"，步骤不删减，避免流程断裂。
- **命名澄清**：技能库无 humanizer-cn，实名 **humanizer-zh**（去 AI 味，MIT，© 歸藏），按它整合。
- **本机开源惯例**（已核实）：技能文件夹本身作为 git 仓库，远程 github.com/quanfanpro-code/<同名仓库>，提交作者 quanfanpro-code；推送用 gh 凭据助手。
- **备份要求**（宿主规则）：任何文件修改前备份到 Documents/Code/BackUp。已完成：`report-review-workflow_20261030_231521`（8 个文件全量）。
- **大文件风险**：GitHub 单文件上限 100M，排除 153M 样本后整仓约 4M，无风险。
- **human-writing / humanizer-zh 附属物**（CHANGELOG、dist、assets 等）按选项 B 标准取舍：运行时必需优先，文字类档案保留，构建产物不留——具体取舍清单在阶段 2 设计文档中定稿。

## 六、验收标准

1. **自包含**：七步法全程只读本技能目录；原 audit-report-checker 外部路径引用全部改为包内路径。
2. **来源可追溯**：SOURCES.json 记录全部 7 个来源（名称、原路径、同步日期、许可）；NOTICE 列第三方组件表；references/licenses/ 存 MIT 全文。
3. **许可完备**：LICENSE = AGPL-3.0；officecli-huaxin-format 授权注明；全库检索 private-equity 仅剩"该视角未整合"标注，无内容残留。
4. **功能等价 + 增强**：七步法步骤不减（第五步为标注 + 降级路径）；第六步含 writing + humanizer-zh + human-writing 三家内容（去 AI 味到位）。
5. **达尔文评估完成**并按其结论优化。
6. **README 达标**：emoji、无代码块/命令行/变量名、无非常用英文缩写、含"使用方式 / 运行逻辑 / 输入要求 / 输出内容"四块、零基础可懂。
7. **推送成功**：quanfanpro-code/report-review-workflow 公开仓库 main 分支内容与本地一致，根目录含 LICENSE 与 README。
8. **本机可用**：改造后在 WorkBuddy 触发"复核报告"能正常走完七步法。

## 七、调研摘要与来源（均 2026-10-30 实时核验）

| 事实 | 结论 | 来源 |
|---|---|---|
| GitHub 有无同名仓库 | 无 report-review-workflow；audit-report-checker 已开源（AGPL-3.0） | gh search / gh repo list |
| 七上游许可 | MIT×5、AGPL-3.0×1、无声明×1（已授权）、保留所有权利×1（排除） | 各技能 LICENSE / SKILL.md 头部 |
| audit-report-checker 体量 | 154M，其中 docs/reviews 153M 为开发留痕样本，运行时必需 <1M | du / find |
| 本机开源惯例 | 技能文件夹即 git 仓库，远程 quanfanpro-code/<同名>，作者 quanfanpro-code | Documents/Code 多仓库 git remote / log |
| requirement-workflow 形态样本 | LICENSE+NOTICE+SKILL.md+references/（含 SOURCES.json、licenses/）+docs/+scripts/ | 目录实测 |
| humanizer-cn 命名 | 不存在；实为 humanizer-zh（去 AI 味，MIT，© 歸藏） | 技能库目录检索 |
| 达尔文技能 | darwin-skill：技能质量评估 + 优化工具，适配"改造后评估优化"要求 | SKILL.md 头部 |

## 八、已确认决策（用户拍板）

| 决策点 | 结论 |
|---|---|
| PE 尽调视角 | 排除，保留"该视角未整合"标注 |
| 华信排版源头 | officecli-huaxin-format |
| officecli-huaxin-format 权属与许可 | 选项 A：权利人授权以 AGPL-3.0 并入 |
| 打包范围 | 选项 B：运行时必需 + 开发档案文字记录，不搬 153M 大样本 |
| 仓库形态 | report-review-workflow、公开仓库、quanfanpro-code 账号、AGPL-3.0 |
| 文字质量审查 | 并入 humanizer-zh + human-writing（去 AI 味），保留 writing |
| 流程要求 | 走需求优先工作流六阶段；改造完达尔文评估优化；写通俗 README；最后开源推送 |

## 九、待确认项

1. **humanizer-cn → humanizer-zh**：用户口称"humanizer-cn"，技能库实名 humanizer-zh，本需求按 humanizer-zh 执行。若指的是其他来源，请指出。
2. 无其他待确认项。
