# 数字核对步骤

2026-10-30：原 financial-data-check 规则已统一到 audit-report-checker，其内容以整包形式随本技能携带。本文件只保留主工作流的引用指引，不注册独立技能，也不保存旧规则副本。

完整读取包内[核对技能](references/audit-report-checker/SKILL.md)和[统一数据核对规则](references/audit-report-checker/references/数据核对规则.md)（路径自包根出发），复用其提取、确定性计算、来源记录与逐项复核能力。其 scripts/ 本地脚本位于 references/audit-report-checker/scripts/，全部算术交其 Decimal 接口确定性计算。

按本次授权检查期初衔接、同口径数据、表内与表间关系和数字出处，当前agent负责适用性和终审。逐项记录双方文件、位置、原值、单位、差额及状态；聊天展示重点，完整明细进入交付文件。发现差异不自动扩大目标，也不按数量反复确认。

后续专业视角仍按主工作流执行，本次迁移不扩大其他步骤的范围。
