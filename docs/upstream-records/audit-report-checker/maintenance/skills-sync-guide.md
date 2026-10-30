# Skills 同步指南

核对日期：2026-10-30。本次按整个技能目录重新清点；当前状态以本节及以下逐项清单为准，旧日志仅保留历史。

## 一、范围与统计口径

- 技能源目录：D:\BaiduSyncdisk\workbuddy skills。
- 本轮逐个读取全部SKILL.md，检查YAML、入口名称、同名项、Git远端与本地变更、相关元数据及来源声明；未运行其他技能、未更新其内容。
- 清点不等于证明全部技能可运行、全部原创来源或全部上游最新版。普通正文中的GitHub链接可能只是参考资料，不认定为来源。
- 排除Git对象、node_modules、.venv、venv、__pycache__和.pytest_cache；不把客户凭据或缓存内容纳入文档。
- 不跟随目录链接，链接单列；顶层目录数、顶层入口数、递归SKILL.md数和不同name数分别统计，不混为技能总数。

| 项目 | 当前实测 |
|---|---:|
| 顶层目录（含.system、代码及资料目录） | 173 |
| 顶层直接含SKILL.md且头部有效的入口 | 166 |
| 递归SKILL.md文件 | 186 |
| 其中非顶层SKILL.md | 20 |
| YAML头部有效的SKILL.md | 184 |
| 有效入口不同name数量（不代表已安装可运行数量） | 159 |
| 存在.git的目录 | 36 |
| 可解析Git仓库 | 35 |
| 库内目录链接 | 0 |
| 同名入口组（含系统入口及嵌套副本） | 23 |
| 扫描读取失败 | 0 |

两份无YAML头部文件是IMA的知识库、笔记子文档，详见嵌套表；不当作两个有效独立入口，也不由此认定IMA主技能不可用。

## 二、注册路径与唯一核对技能

- C:\Users\27651\.workbuddy\skills：Junction，实际目标 D:\BaiduSyncdisk\workbuddy skills。
- C:\Users\27651\.codex\skills：Junction，实际目标 D:\BaiduSyncdisk\workbuddy skills。

核对技能仅保留audit-report-checker 2.2.0：

- 实际使用目录：D:\BaiduSyncdisk\workbuddy skills\audit-report-checker。
- Git维护目录：D:\BaiduSyncdisk\Code\audit-report-checker；远端 https://github.com/quanfanpro-code/audit-report-checker，分支main。
- 上述安装目录没有.git，不能在安装目录假装执行git pull；在维护目录核对远端和本地改动后更新，再按文件差异、备份和哈希同步安装目录。
- audit-data-assistant、financial-data-check及中文目录财务数据核对已经合并，三个旧目录及嵌套入口备份后移入Windows回收站，不保留停用或跳转技能。
- report-review-workflow数字检查步骤已改用唯一技能。其原引用文件仅为步骤说明，不含旧规则全文，不是独立技能。
- 历史日志记载audit-report-checker曾随nigo81/nigo-skills安装；当前维护以已核实的独立仓库和本地文件为准，不再从旧合集覆盖。本轮不据历史分类推定旧技能的最终原创作者。

## 三、全部顶层目录与来源登记

已核完下表全部目录。证据分类直接写明：Git远端是本地实际配置；元数据是文件自述；历史登记未重新证明；来源待确认不得改称原创。没有顶层SKILL.md的目录不计入顶层技能入口。

| 完整目录 | 顶层入口name | 递归SKILL.md数 | 来源证据类别 | 仓库或说明 |
|---|---|---:|---|---|
| D:\BaiduSyncdisk\workbuddy skills\.system | 无顶层入口 | 5 | 宿主系统目录 | 按本地.system路径登记，不推定Git上游 |
| D:\BaiduSyncdisk\workbuddy skills\Reasonix记忆备份 | 无顶层入口 | 0 | 来源待确认 | 未发现本地Git远端或可直接确认的来源声明 |
| D:\BaiduSyncdisk\workbuddy skills\WangEr-Audit-Sampling-Windows | wanger-audit-sampling | 1 | 来源待确认 | 未发现本地Git远端或可直接确认的来源声明 |
| D:\BaiduSyncdisk\workbuddy skills\a-stock-financial | 无顶层入口 | 0 | 历史第三方登记，待核验 | https://github.com/nigo81/nigo-skills |
| D:\BaiduSyncdisk\workbuddy skills\account-aging | account-aging | 1 | Git远端 | https://github.com/quanfanpro-code/account-aging-skill.git |
| D:\BaiduSyncdisk\workbuddy skills\agent-reach | agent-reach | 1 | 历史第三方登记，待核验 | https://github.com/Panniantong/Agent-Reach |
| D:\BaiduSyncdisk\workbuddy skills\agently-mail | agently-mail | 1 | 历史第三方登记，待核验 | https://github.com/Tencent/AgentlyMail |
| D:\BaiduSyncdisk\workbuddy skills\alternative-test-generator | alternative-test-generator | 1 | Git远端 | https://github.com/quanfanpro-code/alternative-test-generator.git |
| D:\BaiduSyncdisk\workbuddy skills\andrej-karpathy-skills | 无顶层入口 | 2 | 历史第三方登记，待核验 | https://github.com/forrestchang/andrej-karpathy-skills |
| D:\BaiduSyncdisk\workbuddy skills\android-native-dev | android-native-dev | 1 | 历史第三方登记，待核验 | https://github.com/MiniMax-AI/skills |
| D:\BaiduSyncdisk\workbuddy skills\annual-report-red-flag-auditor | annual-report-red-flag-auditor | 1 | 历史第三方登记，待核验 | https://github.com/noahnan-max/financial-red-flag-auditor-skill |
| D:\BaiduSyncdisk\workbuddy skills\archive-collect-organize | archive-collect-organize | 1 | Git远端 | https://github.com/quanfanpro-code/archive-collect-organize.git |
| D:\BaiduSyncdisk\workbuddy skills\ask-matt | ask-matt | 1 | 来源待确认 | 未发现本地Git远端或可直接确认的来源声明 |
| D:\BaiduSyncdisk\workbuddy skills\audit-doc-client-rewrite | audit-doc-client-rewrite | 1 | 来源待确认 | 未发现本地Git远端或可直接确认的来源声明 |
| D:\BaiduSyncdisk\workbuddy skills\audit-report-checker | audit-report-checker | 1 | 独立仓库已逐文件核实 | https://github.com/quanfanpro-code/audit-report-checker；维护区：D:\BaiduSyncdisk\Code\audit-report-checker |
| D:\BaiduSyncdisk\workbuddy skills\audit-report-summary | audit-report-summary | 1 | 历史列为自写，原创待证 | 仅旧指南分类记录，不是作者证明 |
| D:\BaiduSyncdisk\workbuddy skills\audit-voucher-check | audit-voucher-check | 1 | Git远端 | https://github.com/quanfanpro-code/audit-voucher-check.git |
| D:\BaiduSyncdisk\workbuddy skills\bid-writer-pro | bid-writer-pro | 1 | 来源待确认 | 未发现本地Git远端或可直接确认的来源声明 |
| D:\BaiduSyncdisk\workbuddy skills\book-to-skill | book-to-skill | 1 | Git远端 | https://github.com/virgiliojr94/book-to-skill.git |
| D:\BaiduSyncdisk\workbuddy skills\brainstorming | brainstorming | 1 | 历史第三方登记，待核验 | https://github.com/obra/superpowers |
| D:\BaiduSyncdisk\workbuddy skills\buddy-sings | buddy-sings | 1 | 来源待确认 | 未发现本地Git远端或可直接确认的来源声明 |
| D:\BaiduSyncdisk\workbuddy skills\bypass-trae-sandbox | bypass-trae-sandbox | 2 | 历史列为自写，原创待证 | 仅旧指南分类记录，不是作者证明 |
| D:\BaiduSyncdisk\workbuddy skills\cas-cashflow-direct | cas-cashflow-direct | 1 | Git远端 | https://github.com/quanfanpro-code/cas-cashflow-direct.git |
| D:\BaiduSyncdisk\workbuddy skills\cas-cashflow-indirect | cas-cashflow-indirect | 1 | Git远端 | https://github.com/quanfanpro-code/cas-cashflow-indirect.git |
| D:\BaiduSyncdisk\workbuddy skills\cas-cashflow-main-workpaper | cas-cashflow-main-workpaper | 1 | Git远端 | https://github.com/quanfanpro-code/cas-cashflow-main-workpaper.git |
| D:\BaiduSyncdisk\workbuddy skills\cavecrew | cavecrew | 1 | 来源待确认 | 未发现本地Git远端或可直接确认的来源声明 |
| D:\BaiduSyncdisk\workbuddy skills\caveman | caveman | 1 | 历史第三方登记，待核验 | https://github.com/JuliusBrussee/caveman |
| D:\BaiduSyncdisk\workbuddy skills\caveman-compress | caveman-compress | 1 | 来源待确认 | 未发现本地Git远端或可直接确认的来源声明 |
| D:\BaiduSyncdisk\workbuddy skills\caveman-stats | caveman-stats | 1 | 来源待确认 | 未发现本地Git远端或可直接确认的来源声明 |
| D:\BaiduSyncdisk\workbuddy skills\chen-yiwei-perspective | chen-yiwei-perspective | 1 | 历史第三方登记，待核验 | https://github.com/nigo81/nigo-skills |
| D:\BaiduSyncdisk\workbuddy skills\chenyiwei-bbs | chenyiwei-bbs | 1 | 来源待确认 | 未发现本地Git远端或可直接确认的来源声明 |
| D:\BaiduSyncdisk\workbuddy skills\china-bid-generator | china-bid-generator | 1 | 来源待确认 | 未发现本地Git远端或可直接确认的来源声明 |
| D:\BaiduSyncdisk\workbuddy skills\china-law-search | china-law-search | 1 | 历史第三方登记，待核验 | https://github.com/nigo81/nigo-skills |
| D:\BaiduSyncdisk\workbuddy skills\cicpa-company-query | cicpa-company-query | 1 | 历史第三方登记，待核验 | https://github.com/nigo81/nigo-skills |
| D:\BaiduSyncdisk\workbuddy skills\clarify-work-request | clarify-work-request | 1 | Git远端 | https://github.com/quanfanpro-code/clarify-work-request.git |
| D:\BaiduSyncdisk\workbuddy skills\code-review | code-review | 1 | 来源待确认 | 未发现本地Git远端或可直接确认的来源声明 |
| D:\BaiduSyncdisk\workbuddy skills\code-reviewer | code-review-skill | 2 | 历史第三方登记，待核验 | https://github.com/awesome-skills/code-review-skill |
| D:\BaiduSyncdisk\workbuddy skills\codebase-design | codebase-design | 1 | 来源待确认 | 未发现本地Git远端或可直接确认的来源声明 |
| D:\BaiduSyncdisk\workbuddy skills\complex-table-header | complex-table-header | 1 | Git远端 | https://github.com/quanfanpro-code/complex-table-header.git |
| D:\BaiduSyncdisk\workbuddy skills\config-migration-package | config-migration-package | 1 | Git远端 | https://github.com/quanfanpro-code/config-migration-package.git |
| D:\BaiduSyncdisk\workbuddy skills\copywriting | copywriting | 1 | 来源待确认 | 未发现本地Git远端或可直接确认的来源声明 |
| D:\BaiduSyncdisk\workbuddy skills\cost-reverse-reconciliation | cost-reverse-reconciliation | 1 | Git远端 | https://github.com/quanfanpro-code/cost-reverse-reconciliation.git |
| D:\BaiduSyncdisk\workbuddy skills\darwin-skill | darwin-skill | 1 | Git远端 | https://github.com/alchaincyf/darwin-skill.git |
| D:\BaiduSyncdisk\workbuddy skills\desktop-gui-style | desktop-gui-style | 1 | 历史列为自写，原创待证 | 仅旧指南分类记录，不是作者证明 |
| D:\BaiduSyncdisk\workbuddy skills\diagnosing-bugs | diagnosing-bugs | 1 | 历史第三方登记，待核验 | https://github.com/mattpocock/skills |
| D:\BaiduSyncdisk\workbuddy skills\diagnosing-superpowers | diagnosing-superpowers | 1 | 来源待确认 | 未发现本地Git远端或可直接确认的来源声明 |
| D:\BaiduSyncdisk\workbuddy skills\dingxinnuo-auxiliary-merge | dingxinnuo-auxiliary-merge | 1 | Git远端 | https://github.com/quanfanpro-code/dingxinnuo-auxiliary-merge.git |
| D:\BaiduSyncdisk\workbuddy skills\dispatching-parallel-agents | dispatching-parallel-agents | 1 | 历史第三方登记，待核验 | https://github.com/obra/superpowers |
| D:\BaiduSyncdisk\workbuddy skills\document-smart-filler | 无顶层入口 | 0 | Git不可识别 | 存在.git，但不能解析为仓库 |
| D:\BaiduSyncdisk\workbuddy skills\document-smart-filler-skill | document-smart-filler | 1 | Git远端 | https://github.com/quanfanpro-code/document-smart-filler-skill.git |
| D:\BaiduSyncdisk\workbuddy skills\domain-modeling | domain-modeling | 1 | 来源待确认 | 未发现本地Git远端或可直接确认的来源声明 |
| D:\BaiduSyncdisk\workbuddy skills\dsh-plugin-update | dsh-plugin-update | 1 | Git远端 | https://github.com/quanfanpro-code/dsh-plugin-update.git |
| D:\BaiduSyncdisk\workbuddy skills\dsh-restart-button | 无顶层入口 | 0 | Git远端 | https://github.com/quanfanpro-code/dsh-restart-button.git |
| D:\BaiduSyncdisk\workbuddy skills\economic-responsibility-audit-optimized | economic-responsibility-audit-optimized | 1 | Git远端 | https://github.com/quanfanpro-code/economic-responsibility-audit-optimized.git |
| D:\BaiduSyncdisk\workbuddy skills\eli5 | eli5 | 1 | 来源待确认 | 未发现本地Git远端或可直接确认的来源声明 |
| D:\BaiduSyncdisk\workbuddy skills\equity-structure-design | equity-structure-design | 1 | Git远端 | https://github.com/quanfanpro-code/equity-structure-design.git |
| D:\BaiduSyncdisk\workbuddy skills\excel-batch-process | excel-batch-process | 2 | 历史列为自写，原创待证 | 仅旧指南分类记录，不是作者证明 |
| D:\BaiduSyncdisk\workbuddy skills\excel-fast-writer | excel-fast-writer | 1 | Git远端 | https://github.com/quanfanpro-code/excel-fast-writer.git |
| D:\BaiduSyncdisk\workbuddy skills\excel-master | excel-master | 1 | Git远端 | https://github.com/benyichan/excel-master.git |
| D:\BaiduSyncdisk\workbuddy skills\executing-plans | executing-plans | 1 | 历史第三方登记，待核验 | https://github.com/obra/superpowers |
| D:\BaiduSyncdisk\workbuddy skills\financial-due-diligence | financial-due-diligence | 1 | Git远端 | https://github.com/quanfanpro-code/financial-due-diligence.git |
| D:\BaiduSyncdisk\workbuddy skills\financial-statement-fraud-analysis | financial-statement-fraud-analysis | 1 | 来源待确认 | 未发现本地Git远端或可直接确认的来源声明 |
| D:\BaiduSyncdisk\workbuddy skills\finishing-a-development-branch | finishing-a-development-branch | 1 | 历史第三方登记，待核验 | https://github.com/obra/superpowers |
| D:\BaiduSyncdisk\workbuddy skills\flowchart-generator | flowchart-generator | 1 | 历史第三方登记，待核验 | https://github.com/nigo81/nigo-skills |
| D:\BaiduSyncdisk\workbuddy skills\flutter-dev | flutter-dev | 1 | 历史第三方登记，待核验 | https://github.com/MiniMax-AI/skills |
| D:\BaiduSyncdisk\workbuddy skills\frontend-dev | frontend-dev | 1 | 历史第三方登记，待核验 | https://github.com/MiniMax-AI/skills |
| D:\BaiduSyncdisk\workbuddy skills\fullstack-dev | fullstack-dev | 1 | 历史第三方登记，待核验 | https://github.com/MiniMax-AI/skills |
| D:\BaiduSyncdisk\workbuddy skills\gif-sticker-maker | gif-sticker-maker | 1 | 来源待确认 | 未发现本地Git远端或可直接确认的来源声明 |
| D:\BaiduSyncdisk\workbuddy skills\git-repos-sync | git-repos-sync | 1 | 来源待确认 | 未发现本地Git远端或可直接确认的来源声明 |
| D:\BaiduSyncdisk\workbuddy skills\grill-with-docs | grill-with-docs | 1 | 历史第三方登记，待核验 | https://github.com/mattpocock/skills |
| D:\BaiduSyncdisk\workbuddy skills\huashu-excel | huashu-excel | 1 | 历史第三方登记，待核验 | https://github.com/alchaincyf/huashu-excel |
| D:\BaiduSyncdisk\workbuddy skills\huaxin-engagement-letter | huaxin-engagement-letter | 1 | 来源待确认 | 未发现本地Git远端或可直接确认的来源声明 |
| D:\BaiduSyncdisk\workbuddy skills\huaxin-oa | huaxin-oa | 2 | Git远端 | https://github.com/quanfanpro-code/huaxin-oa.git |
| D:\BaiduSyncdisk\workbuddy skills\huaxin-oa-project | huaxin-oa-project | 1 | Git远端 | https://github.com/quanfanpro-code/huaxin-oa-project.git |
| D:\BaiduSyncdisk\workbuddy skills\huaxin-oa-sign | huaxin-oa-sign | 1 | Git远端 | https://github.com/quanfanpro-code/huaxin-oa-sign.git |
| D:\BaiduSyncdisk\workbuddy skills\huaxin-word-format | huaxin-word-format | 1 | 历史列为自写，原创待证 | 仅旧指南分类记录，不是作者证明 |
| D:\BaiduSyncdisk\workbuddy skills\human-writing | human-writing | 1 | Git远端 | https://github.com/KKKKhazix/human-writing.git |
| D:\BaiduSyncdisk\workbuddy skills\humanizer-zh | humanizer-zh | 1 | Git远端 | https://github.com/op7418/Humanizer-zh.git |
| D:\BaiduSyncdisk\workbuddy skills\ima-skill | ima-skill | 3 | 来源待确认 | 未发现本地Git远端或可直接确认的来源声明 |
| D:\BaiduSyncdisk\workbuddy skills\imagegen | imagegen | 1 | 来源待确认 | 未发现本地Git远端或可直接确认的来源声明 |
| D:\BaiduSyncdisk\workbuddy skills\implement | implement | 1 | 来源待确认 | 未发现本地Git远端或可直接确认的来源声明 |
| D:\BaiduSyncdisk\workbuddy skills\improve-codebase-architecture | improve-codebase-architecture | 1 | 历史第三方登记，待核验 | https://github.com/mattpocock/skills |
| D:\BaiduSyncdisk\workbuddy skills\interview-record-polish | interview-record-polish | 1 | Git远端 | https://github.com/quanfanpro-code/interview-record-polish.git |
| D:\BaiduSyncdisk\workbuddy skills\ios-application-dev | ios-application-dev | 1 | 历史第三方登记，待核验 | https://github.com/MiniMax-AI/skills |
| D:\BaiduSyncdisk\workbuddy skills\karpathy-guidelines | karpathy-guidelines | 1 | 来源待确认 | 未发现本地Git远端或可直接确认的来源声明 |
| D:\BaiduSyncdisk\workbuddy skills\kemu-counterpart-generator | 无顶层入口 | 0 | Git远端 | https://github.com/quanfanpro-code/kemu-counterpart-generator.git |
| D:\BaiduSyncdisk\workbuddy skills\local-rag | local-rag | 1 | 来源待确认 | 未发现本地Git远端或可直接确认的来源声明 |
| D:\BaiduSyncdisk\workbuddy skills\minimax-docx | minimax-docx | 2 | 历史第三方登记，待核验 | https://github.com/MiniMax-AI/skills |
| D:\BaiduSyncdisk\workbuddy skills\minimax-multimodal-toolkit | mmx-cli | 1 | 历史第三方登记，待核验 | https://github.com/MiniMax-AI/skills |
| D:\BaiduSyncdisk\workbuddy skills\minimax-music-gen | minimax-music-gen | 1 | 来源待确认 | 未发现本地Git远端或可直接确认的来源声明 |
| D:\BaiduSyncdisk\workbuddy skills\minimax-music-playlist | minimax-music-playlist | 1 | 来源待确认 | 未发现本地Git远端或可直接确认的来源声明 |
| D:\BaiduSyncdisk\workbuddy skills\minimax-pdf | minimax-pdf | 2 | 历史第三方登记，待核验 | https://github.com/MiniMax-AI/skills |
| D:\BaiduSyncdisk\workbuddy skills\minimax-xlsx | minimax-xlsx | 2 | 历史第三方登记，待核验 | https://github.com/MiniMax-AI/skills |
| D:\BaiduSyncdisk\workbuddy skills\mmx-cli | mmx-cli | 1 | 来源待确认 | 未发现本地Git远端或可直接确认的来源声明 |
| D:\BaiduSyncdisk\workbuddy skills\name-matching | name-matching | 1 | Git远端 | https://github.com/quanfanpro-code/name-matching.git |
| D:\BaiduSyncdisk\workbuddy skills\nexus-mapper | nexus-mapper | 1 | 历史第三方登记，待核验 | https://github.com/Haaaiawd/Nexus-skills |
| D:\BaiduSyncdisk\workbuddy skills\nigo-bank-flow-reconciliation | bank-flow-reconciliation | 1 | 来源待确认 | 未发现本地Git远端或可直接确认的来源声明 |
| D:\BaiduSyncdisk\workbuddy skills\nigo-chenyiwei-bbs | chenyiwei-bbs | 1 | 来源待确认 | 未发现本地Git远端或可直接确认的来源声明 |
| D:\BaiduSyncdisk\workbuddy skills\nigo-local-rag | local-rag | 1 | 来源待确认 | 未发现本地Git远端或可直接确认的来源声明 |
| D:\BaiduSyncdisk\workbuddy skills\nigo-opencode-session-visualizer | opencode-session-visualizer | 1 | 来源待确认 | 未发现本地Git远端或可直接确认的来源声明 |
| D:\BaiduSyncdisk\workbuddy skills\officecli | officecli | 1 | 来源待确认 | 未发现本地Git远端或可直接确认的来源声明 |
| D:\BaiduSyncdisk\workbuddy skills\officecli-huaxin-format | officecli-huaxin-format | 1 | 历史列为自写，原创待证 | 仅旧指南分类记录，不是作者证明 |
| D:\BaiduSyncdisk\workbuddy skills\openai-docs | openai-docs | 1 | 来源待确认 | 未发现本地Git远端或可直接确认的来源声明 |
| D:\BaiduSyncdisk\workbuddy skills\opencode-session-visualizer | opencode-session-visualizer | 1 | 来源待确认 | 未发现本地Git远端或可直接确认的来源声明 |
| D:\BaiduSyncdisk\workbuddy skills\pdf-qr-overlay | pdf-qr-overlay | 1 | 来源待确认 | 未发现本地Git远端或可直接确认的来源声明 |
| D:\BaiduSyncdisk\workbuddy skills\pdf-seal-stamp | pdf-seal-stamp | 1 | 来源待确认 | 未发现本地Git远端或可直接确认的来源声明 |
| D:\BaiduSyncdisk\workbuddy skills\pdf-to-scan | pdf-to-scan | 1 | 历史列为自写，原创待证 | 仅旧指南分类记录，不是作者证明 |
| D:\BaiduSyncdisk\workbuddy skills\pdf二维码叠加 | pdf-qr-overlay | 1 | 历史列为自写，原创待证 | 仅旧指南分类记录，不是作者证明 |
| D:\BaiduSyncdisk\workbuddy skills\playwright-cli | playwright-cli | 1 | 来源待确认 | 未发现本地Git远端或可直接确认的来源声明 |
| D:\BaiduSyncdisk\workbuddy skills\playwright-component-testing | playwright-component-testing | 1 | 来源待确认 | 未发现本地Git远端或可直接确认的来源声明 |
| D:\BaiduSyncdisk\workbuddy skills\playwright-trace | playwright-trace | 1 | 来源待确认 | 未发现本地Git远端或可直接确认的来源声明 |
| D:\BaiduSyncdisk\workbuddy skills\plugin-creator | plugin-creator | 1 | 来源待确认 | 未发现本地Git远端或可直接确认的来源声明 |
| D:\BaiduSyncdisk\workbuddy skills\ponytail | ponytail | 1 | 历史第三方登记，待核验 | https://github.com/DietrichGebert/ponytail |
| D:\BaiduSyncdisk\workbuddy skills\ponytail-audit | ponytail-audit | 1 | 历史第三方登记，待核验 | https://github.com/DietrichGebert/ponytail |
| D:\BaiduSyncdisk\workbuddy skills\ponytail-debt | ponytail-debt | 1 | 历史第三方登记，待核验 | https://github.com/DietrichGebert/ponytail |
| D:\BaiduSyncdisk\workbuddy skills\ponytail-gain | ponytail-gain | 1 | 历史第三方登记，待核验 | https://github.com/DietrichGebert/ponytail |
| D:\BaiduSyncdisk\workbuddy skills\ponytail-help | ponytail-help | 1 | 历史第三方登记，待核验 | https://github.com/DietrichGebert/ponytail |
| D:\BaiduSyncdisk\workbuddy skills\ponytail-review | ponytail-review | 1 | 历史第三方登记，待核验 | https://github.com/DietrichGebert/ponytail |
| D:\BaiduSyncdisk\workbuddy skills\ppt-master | ppt-master | 3 | 历史第三方登记，待核验 | https://github.com/hugohe3/ppt-master |
| D:\BaiduSyncdisk\workbuddy skills\pptx-generator | pptx-generator | 1 | 历史第三方登记，待核验 | https://github.com/MiniMax-AI/skills |
| D:\BaiduSyncdisk\workbuddy skills\private-equity-investment-dd | private-equity-investment-dd | 1 | 历史第三方登记，待核验 | https://github.com/noahnan-max/private-equity-investment-dd-skill |
| D:\BaiduSyncdisk\workbuddy skills\production-task-daily-cost | production-task-daily-cost | 1 | Git远端 | https://github.com/quanfanpro-code/production-task-daily-cost.git |
| D:\BaiduSyncdisk\workbuddy skills\prototype | prototype | 1 | 来源待确认 | 未发现本地Git远端或可直接确认的来源声明 |
| D:\BaiduSyncdisk\workbuddy skills\pua | pua | 2 | 历史第三方登记，待核验 | https://github.com/tanweai/pua |
| D:\BaiduSyncdisk\workbuddy skills\python-pro | python-pro | 1 | 来源待确认 | 未发现本地Git远端或可直接确认的来源声明 |
| D:\BaiduSyncdisk\workbuddy skills\react-native-dev | react-native-dev | 1 | 历史第三方登记，待核验 | https://github.com/MiniMax-AI/skills |
| D:\BaiduSyncdisk\workbuddy skills\receivables-disclosure-review | receivables-disclosure-review | 1 | Git远端 | https://github.com/quanfanpro-code/receivables-disclosure-review.git |
| D:\BaiduSyncdisk\workbuddy skills\receiving-code-review | receiving-code-review | 1 | 历史第三方登记，待核验 | https://github.com/obra/superpowers |
| D:\BaiduSyncdisk\workbuddy skills\related-party-identification | related-party-identification | 1 | Git远端 | https://github.com/quanfanpro-code/related-party-identification.git |
| D:\BaiduSyncdisk\workbuddy skills\report-helper | report-helper | 1 | 历史第三方登记，待核验 | https://github.com/Jiaranbb/report-helper |
| D:\BaiduSyncdisk\workbuddy skills\report-review-workflow | report-review-workflow | 1 | 历史列为自写，原创待证 | 仅旧指南分类记录，不是作者证明 |
| D:\BaiduSyncdisk\workbuddy skills\request-analyzer | request-analyzer | 1 | 历史第三方登记，待核验 | https://github.com/smallnest/goskills |
| D:\BaiduSyncdisk\workbuddy skills\requesting-code-review | requesting-code-review | 1 | 历史第三方登记，待核验 | https://github.com/obra/superpowers |
| D:\BaiduSyncdisk\workbuddy skills\requirement-workflow | requirement-workflow | 1 | Git远端 | https://github.com/quanfanpro-code/requirement-workflow.git |
| D:\BaiduSyncdisk\workbuddy skills\research | research | 1 | 来源待确认 | 未发现本地Git远端或可直接确认的来源声明 |
| D:\BaiduSyncdisk\workbuddy skills\resolving-merge-conflicts | resolving-merge-conflicts | 1 | 来源待确认 | 未发现本地Git远端或可直接确认的来源声明 |
| D:\BaiduSyncdisk\workbuddy skills\review-agent | review-agent | 1 | 来源待确认 | 未发现本地Git远端或可直接确认的来源声明 |
| D:\BaiduSyncdisk\workbuddy skills\review-cash-flow-statement-supplementary-info | review-cash-flow-statement-supplementary-info | 1 | 来源待确认 | 未发现本地Git远端或可直接确认的来源声明 |
| D:\BaiduSyncdisk\workbuddy skills\setup-matt-pocock-skills | setup-matt-pocock-skills | 1 | 来源待确认 | 未发现本地Git远端或可直接确认的来源声明 |
| D:\BaiduSyncdisk\workbuddy skills\shader-dev | shader-dev | 1 | 历史第三方登记，待核验 | https://github.com/MiniMax-AI/skills |
| D:\BaiduSyncdisk\workbuddy skills\shaoniannu-perspective | shaoniannu-perspective | 1 | 历史第三方登记，待核验 | https://github.com/nigo81/nigo-skills |
| D:\BaiduSyncdisk\workbuddy skills\show-me | show-me | 1 | 来源待确认 | 未发现本地Git远端或可直接确认的来源声明 |
| D:\BaiduSyncdisk\workbuddy skills\skill-creator | skill-creator | 1 | 来源待确认 | 未发现本地Git远端或可直接确认的来源声明 |
| D:\BaiduSyncdisk\workbuddy skills\skill-installer | skill-installer | 1 | 来源待确认 | 未发现本地Git远端或可直接确认的来源声明 |
| D:\BaiduSyncdisk\workbuddy skills\slide-maker | slide-maker | 1 | 历史第三方登记，待核验 | https://github.com/addsumtech/slides_maker |
| D:\BaiduSyncdisk\workbuddy skills\solo-review | solo-review | 1 | 来源待确认 | 未发现本地Git远端或可直接确认的来源声明 |
| D:\BaiduSyncdisk\workbuddy skills\stop-slop-zh | stop-slop-zh | 1 | 历史第三方登记，待核验 | https://github.com/pencil20388-eng/stop-slop-zh |
| D:\BaiduSyncdisk\workbuddy skills\subagent-driven-development | subagent-driven-development | 1 | 历史第三方登记，待核验 | https://github.com/obra/superpowers |
| D:\BaiduSyncdisk\workbuddy skills\systematic-debugging | systematic-debugging | 1 | 历史第三方登记，待核验 | https://github.com/obra/superpowers |
| D:\BaiduSyncdisk\workbuddy skills\tcm-skill | tcm-skill | 1 | Git远端 | https://github.com/YuanZHAO321/TCM.Skill.git |
| D:\BaiduSyncdisk\workbuddy skills\tdd | tdd | 1 | 来源待确认 | 未发现本地Git远端或可直接确认的来源声明 |
| D:\BaiduSyncdisk\workbuddy skills\tender-bidding-assistant | tender-bidding-assistant | 1 | 历史第三方登记，待核验 | https://github.com/gechengling/tender-bidding-assistant |
| D:\BaiduSyncdisk\workbuddy skills\test-driven-development | test-driven-development | 1 | 历史第三方登记，待核验 | https://github.com/obra/superpowers |
| D:\BaiduSyncdisk\workbuddy skills\tianchuan-perspective | tianchuan-perspective | 1 | 历史第三方登记，待核验 | https://github.com/nigo81/nigo-skills |
| D:\BaiduSyncdisk\workbuddy skills\to-spec | to-spec | 1 | 历史第三方登记，待核验 | https://github.com/mattpocock/skills |
| D:\BaiduSyncdisk\workbuddy skills\to-tickets | to-tickets | 1 | 历史第三方登记，待核验 | https://github.com/mattpocock/skills |
| D:\BaiduSyncdisk\workbuddy skills\triage | triage | 1 | 来源待确认 | 未发现本地Git远端或可直接确认的来源声明 |
| D:\BaiduSyncdisk\workbuddy skills\ui-ux-designer | ui-ux-designer | 1 | 来源待确认 | 未发现本地Git远端或可直接确认的来源声明 |
| D:\BaiduSyncdisk\workbuddy skills\universal-solo-review | solo-review | 1 | 来源待确认 | 未发现本地Git远端或可直接确认的来源声明 |
| D:\BaiduSyncdisk\workbuddy skills\using-git-worktrees | using-git-worktrees | 1 | 历史第三方登记，待核验 | https://github.com/obra/superpowers |
| D:\BaiduSyncdisk\workbuddy skills\using-superpowers | using-superpowers | 1 | 历史第三方登记，待核验 | https://github.com/obra/superpowers |
| D:\BaiduSyncdisk\workbuddy skills\verification-before-completion | verification-before-completion | 1 | 历史第三方登记，待核验 | https://github.com/obra/superpowers |
| D:\BaiduSyncdisk\workbuddy skills\vision-analysis | vision-analysis | 2 | 历史第三方登记，待核验 | https://github.com/MiniMax-AI/skills |
| D:\BaiduSyncdisk\workbuddy skills\wanger-audit-sampling | wanger-audit-sampling | 1 | 来源待确认 | 未发现本地Git远端或可直接确认的来源声明 |
| D:\BaiduSyncdisk\workbuddy skills\wayfinder | wayfinder | 1 | 来源待确认 | 未发现本地Git远端或可直接确认的来源声明 |
| D:\BaiduSyncdisk\workbuddy skills\windows-recycle-delete | windows-recycle-delete | 1 | 来源待确认 | 未发现本地Git远端或可直接确认的来源声明 |
| D:\BaiduSyncdisk\workbuddy skills\wizard | wizard | 1 | 来源待确认 | 未发现本地Git远端或可直接确认的来源声明 |
| D:\BaiduSyncdisk\workbuddy skills\writing | writing | 1 | 历史第三方登记，待核验 | https://github.com/Anbeeld/WRITING.md |
| D:\BaiduSyncdisk\workbuddy skills\writing-plans | writing-plans | 1 | 历史第三方登记，待核验 | https://github.com/obra/superpowers |
| D:\BaiduSyncdisk\workbuddy skills\writing-skills | writing-skills | 1 | 历史第三方登记，待核验 | https://github.com/obra/superpowers |
| D:\BaiduSyncdisk\workbuddy skills\zoom-out | zoom-out | 1 | 来源待确认 | 未发现本地Git远端或可直接确认的来源声明 |
| D:\BaiduSyncdisk\workbuddy skills\反思想殖民 | fan-sixiang-zhi-min | 1 | 历史列为自写，原创待证 | 仅旧指南分类记录，不是作者证明 |
| D:\BaiduSyncdisk\workbuddy skills\表格多线程处理 | 表格多线程处理 | 1 | 来源待确认 | 未发现本地Git远端或可直接确认的来源声明 |

来源证据分类覆盖上述全部目录：Git不可识别 1项；Git远端 35项；历史列为自写，原创待证 10项；历史第三方登记，待核验 62项；宿主系统目录 1项；来源待确认 63项；独立仓库已逐文件核实 1项。

## 四、全部Git目录的本地实况

以下提交和状态为本机快照，未对全库执行fetch、pull、push或联网逐一核验上游最新提交。变更数仅含已跟踪文件，不含未跟踪文件；空白状态不等于可自动覆盖。

| 完整目录 | origin实际配置 | 当前分支 | 本地提交 | 已跟踪变更数/异常 |
|---|---|---|---|---|
| D:\BaiduSyncdisk\workbuddy skills\account-aging | https://github.com/quanfanpro-code/account-aging-skill.git | main | 6820f504e3ab | 0 |
| D:\BaiduSyncdisk\workbuddy skills\alternative-test-generator | https://github.com/quanfanpro-code/alternative-test-generator.git | master | 9e51c980be20 | 0 |
| D:\BaiduSyncdisk\workbuddy skills\archive-collect-organize | https://github.com/quanfanpro-code/archive-collect-organize.git | master | 0544d5203676 | 0 |
| D:\BaiduSyncdisk\workbuddy skills\audit-voucher-check | https://github.com/quanfanpro-code/audit-voucher-check.git | main | 6d9f4fb04e0e | 0 |
| D:\BaiduSyncdisk\workbuddy skills\book-to-skill | https://github.com/virgiliojr94/book-to-skill.git | master | a24e62f4d8ca | 0 |
| D:\BaiduSyncdisk\workbuddy skills\cas-cashflow-direct | https://github.com/quanfanpro-code/cas-cashflow-direct.git | main | c28f58134201 | 0 |
| D:\BaiduSyncdisk\workbuddy skills\cas-cashflow-indirect | https://github.com/quanfanpro-code/cas-cashflow-indirect.git | main | 4f6df44b1984 | 0 |
| D:\BaiduSyncdisk\workbuddy skills\cas-cashflow-main-workpaper | https://github.com/quanfanpro-code/cas-cashflow-main-workpaper.git | auto-optimize/20260802-2228 | 3ef195185347 | 0 |
| D:\BaiduSyncdisk\workbuddy skills\clarify-work-request | https://github.com/quanfanpro-code/clarify-work-request.git | master | 78a96438c2cf | 0 |
| D:\BaiduSyncdisk\workbuddy skills\complex-table-header | https://github.com/quanfanpro-code/complex-table-header.git | master | cbb3f5471993 | 0 |
| D:\BaiduSyncdisk\workbuddy skills\config-migration-package | https://github.com/quanfanpro-code/config-migration-package.git | main | be1204434555 | 0 |
| D:\BaiduSyncdisk\workbuddy skills\cost-reverse-reconciliation | https://github.com/quanfanpro-code/cost-reverse-reconciliation.git | master | 364c2c8c7bbb | 0 |
| D:\BaiduSyncdisk\workbuddy skills\darwin-skill | https://github.com/alchaincyf/darwin-skill.git | master | 8a8b66258e3c | 0 |
| D:\BaiduSyncdisk\workbuddy skills\dingxinnuo-auxiliary-merge | https://github.com/quanfanpro-code/dingxinnuo-auxiliary-merge.git | main | 36d4aec7ba67 | 0 |
| D:\BaiduSyncdisk\workbuddy skills\document-smart-filler | — | — | — | 无法识别Git仓库，未修复 |
| D:\BaiduSyncdisk\workbuddy skills\document-smart-filler-skill | https://github.com/quanfanpro-code/document-smart-filler-skill.git | main | 2a0da25fdd35 | 0 |
| D:\BaiduSyncdisk\workbuddy skills\dsh-plugin-update | https://github.com/quanfanpro-code/dsh-plugin-update.git | main | 5120a9df9be8 | 0 |
| D:\BaiduSyncdisk\workbuddy skills\dsh-restart-button | https://github.com/quanfanpro-code/dsh-restart-button.git | master | 5e7377ba809d | 0 |
| D:\BaiduSyncdisk\workbuddy skills\economic-responsibility-audit-optimized | https://github.com/quanfanpro-code/economic-responsibility-audit-optimized.git | master | 90b7ebc9d0db | 0 |
| D:\BaiduSyncdisk\workbuddy skills\equity-structure-design | https://github.com/quanfanpro-code/equity-structure-design.git | main | 74aaf253b12b | 0 |
| D:\BaiduSyncdisk\workbuddy skills\excel-fast-writer | https://github.com/quanfanpro-code/excel-fast-writer.git | main | 3022b8aabbe8 | 0 |
| D:\BaiduSyncdisk\workbuddy skills\excel-master | https://github.com/benyichan/excel-master.git | master | 7856e3520212 | 0 |
| D:\BaiduSyncdisk\workbuddy skills\financial-due-diligence | https://github.com/quanfanpro-code/financial-due-diligence.git | main | 7c3e32aa2bc4 | 0 |
| D:\BaiduSyncdisk\workbuddy skills\huaxin-oa | https://github.com/quanfanpro-code/huaxin-oa.git | main | bccf9b74a546 | 0 |
| D:\BaiduSyncdisk\workbuddy skills\huaxin-oa-project | https://github.com/quanfanpro-code/huaxin-oa-project.git | main | 658b49c79df8 | 0 |
| D:\BaiduSyncdisk\workbuddy skills\huaxin-oa-sign | https://github.com/quanfanpro-code/huaxin-oa-sign.git | main | 36602658bee1 | 0 |
| D:\BaiduSyncdisk\workbuddy skills\human-writing | https://github.com/KKKKhazix/human-writing.git | main | 4fda173f3fef | 11 |
| D:\BaiduSyncdisk\workbuddy skills\humanizer-zh | https://github.com/op7418/Humanizer-zh.git | main | f4518a8eab97 | 0 |
| D:\BaiduSyncdisk\workbuddy skills\interview-record-polish | https://github.com/quanfanpro-code/interview-record-polish.git | main | 2d91d1f31dcf | 0 |
| D:\BaiduSyncdisk\workbuddy skills\kemu-counterpart-generator | https://github.com/quanfanpro-code/kemu-counterpart-generator.git | main | 204a2c631355 | 0 |
| D:\BaiduSyncdisk\workbuddy skills\name-matching | https://github.com/quanfanpro-code/name-matching.git | main | c0916f033625 | 0 |
| D:\BaiduSyncdisk\workbuddy skills\production-task-daily-cost | https://github.com/quanfanpro-code/production-task-daily-cost.git | main | a66f18580ca9 | 0 |
| D:\BaiduSyncdisk\workbuddy skills\receivables-disclosure-review | https://github.com/quanfanpro-code/receivables-disclosure-review.git | main | f7317240a4f5 | 0 |
| D:\BaiduSyncdisk\workbuddy skills\related-party-identification | https://github.com/quanfanpro-code/related-party-identification.git | main | 48027ddd5bc8 | 0 |
| D:\BaiduSyncdisk\workbuddy skills\requirement-workflow | https://github.com/quanfanpro-code/requirement-workflow.git | main | 39c8037ee431 | 0 |
| D:\BaiduSyncdisk\workbuddy skills\tcm-skill | https://github.com/YuanZHAO321/TCM.Skill.git | main | 966a88acf942 | 1 |

human-writing和tcm-skill已有本地已跟踪变更，本轮未修改、恢复或同步这些内容。document-smart-filler中存在.git但Git不能识别，本轮只记录，不初始化、不重建。

## 五、全部嵌套SKILL.md

包括.system系统入口、嵌套安装副本及无YAML的子文档；逐项列出，不把目录数当文件数。

| 完整文件路径 | name | 头部/分类说明 |
|---|---|---|
| D:\BaiduSyncdisk\workbuddy skills\.system\imagegen\SKILL.md | imagegen | 系统目录入口 |
| D:\BaiduSyncdisk\workbuddy skills\.system\openai-docs\SKILL.md | openai-docs | 系统目录入口 |
| D:\BaiduSyncdisk\workbuddy skills\.system\review-agent\SKILL.md | review-agent | 系统目录入口 |
| D:\BaiduSyncdisk\workbuddy skills\.system\skill-creator\SKILL.md | skill-creator | 系统目录入口 |
| D:\BaiduSyncdisk\workbuddy skills\.system\skill-installer\SKILL.md | skill-installer | 系统目录入口 |
| D:\BaiduSyncdisk\workbuddy skills\andrej-karpathy-skills\andrej-karpathy-skills\skills\karpathy-guidelines\SKILL.md | karpathy-guidelines | 嵌套入口，已计入递归文件总数 |
| D:\BaiduSyncdisk\workbuddy skills\andrej-karpathy-skills\skills\karpathy-guidelines\SKILL.md | karpathy-guidelines | 嵌套入口，已计入递归文件总数 |
| D:\BaiduSyncdisk\workbuddy skills\bypass-trae-sandbox\bypass-trae-sandbox\SKILL.md | bypass-trae-sandbox | 嵌套入口，已计入递归文件总数 |
| D:\BaiduSyncdisk\workbuddy skills\code-reviewer\code-reviewer\SKILL.md | code-review-skill | 嵌套入口，已计入递归文件总数 |
| D:\BaiduSyncdisk\workbuddy skills\excel-batch-process\excel-batch-process\SKILL.md | 表格多线程处理 | 嵌套入口，已计入递归文件总数 |
| D:\BaiduSyncdisk\workbuddy skills\huaxin-oa\huaxin-oa\SKILL.md | huaxin-oa | 嵌套入口，已计入递归文件总数 |
| D:\BaiduSyncdisk\workbuddy skills\ima-skill\knowledge-base\SKILL.md | — | 缺少完整YAML头部 |
| D:\BaiduSyncdisk\workbuddy skills\ima-skill\notes\SKILL.md | — | 缺少完整YAML头部 |
| D:\BaiduSyncdisk\workbuddy skills\minimax-docx\minimax-docx\SKILL.md | minimax-docx | 嵌套入口，已计入递归文件总数 |
| D:\BaiduSyncdisk\workbuddy skills\minimax-pdf\minimax-pdf\SKILL.md | minimax-pdf | 嵌套入口，已计入递归文件总数 |
| D:\BaiduSyncdisk\workbuddy skills\minimax-xlsx\minimax-xlsx\SKILL.md | minimax-xlsx | 嵌套入口，已计入递归文件总数 |
| D:\BaiduSyncdisk\workbuddy skills\ppt-master\ppt-master\skills\ppt-master\SKILL.md | ppt-master | 嵌套入口，已计入递归文件总数 |
| D:\BaiduSyncdisk\workbuddy skills\ppt-master\skills\ppt-master\SKILL.md | ppt-master | 嵌套入口，已计入递归文件总数 |
| D:\BaiduSyncdisk\workbuddy skills\pua\pua\SKILL.md | pua | 嵌套入口，已计入递归文件总数 |
| D:\BaiduSyncdisk\workbuddy skills\vision-analysis\vision-analysis\SKILL.md | vision-analysis | 嵌套入口，已计入递归文件总数 |

## 六、同名入口与目录名差异

下表是需要区分的同名入口，不是自动删除清单。系统入口与用户入口、同名但内容不同的版本、嵌套文件分别保留证据；本轮不清理本次核对技能以外的目录。

| name | 完整入口路径 | 字节内容 |
|---|---|---|
| bypass-trae-sandbox | D:\BaiduSyncdisk\workbuddy skills\bypass-trae-sandbox\SKILL.md<br>D:\BaiduSyncdisk\workbuddy skills\bypass-trae-sandbox\bypass-trae-sandbox\SKILL.md | 完全相同 |
| chenyiwei-bbs | D:\BaiduSyncdisk\workbuddy skills\chenyiwei-bbs\SKILL.md<br>D:\BaiduSyncdisk\workbuddy skills\nigo-chenyiwei-bbs\SKILL.md | 完全相同 |
| code-review-skill | D:\BaiduSyncdisk\workbuddy skills\code-reviewer\SKILL.md<br>D:\BaiduSyncdisk\workbuddy skills\code-reviewer\code-reviewer\SKILL.md | 存在不同内容，不能直接删 |
| huaxin-oa | D:\BaiduSyncdisk\workbuddy skills\huaxin-oa\SKILL.md<br>D:\BaiduSyncdisk\workbuddy skills\huaxin-oa\huaxin-oa\SKILL.md | 存在不同内容，不能直接删 |
| imagegen | D:\BaiduSyncdisk\workbuddy skills\.system\imagegen\SKILL.md<br>D:\BaiduSyncdisk\workbuddy skills\imagegen\SKILL.md | 完全相同 |
| karpathy-guidelines | D:\BaiduSyncdisk\workbuddy skills\andrej-karpathy-skills\andrej-karpathy-skills\skills\karpathy-guidelines\SKILL.md<br>D:\BaiduSyncdisk\workbuddy skills\andrej-karpathy-skills\skills\karpathy-guidelines\SKILL.md<br>D:\BaiduSyncdisk\workbuddy skills\karpathy-guidelines\SKILL.md | 完全相同 |
| local-rag | D:\BaiduSyncdisk\workbuddy skills\local-rag\SKILL.md<br>D:\BaiduSyncdisk\workbuddy skills\nigo-local-rag\SKILL.md | 完全相同 |
| minimax-docx | D:\BaiduSyncdisk\workbuddy skills\minimax-docx\SKILL.md<br>D:\BaiduSyncdisk\workbuddy skills\minimax-docx\minimax-docx\SKILL.md | 存在不同内容，不能直接删 |
| minimax-pdf | D:\BaiduSyncdisk\workbuddy skills\minimax-pdf\SKILL.md<br>D:\BaiduSyncdisk\workbuddy skills\minimax-pdf\minimax-pdf\SKILL.md | 完全相同 |
| minimax-xlsx | D:\BaiduSyncdisk\workbuddy skills\minimax-xlsx\SKILL.md<br>D:\BaiduSyncdisk\workbuddy skills\minimax-xlsx\minimax-xlsx\SKILL.md | 完全相同 |
| mmx-cli | D:\BaiduSyncdisk\workbuddy skills\minimax-multimodal-toolkit\SKILL.md<br>D:\BaiduSyncdisk\workbuddy skills\mmx-cli\SKILL.md | 完全相同 |
| openai-docs | D:\BaiduSyncdisk\workbuddy skills\.system\openai-docs\SKILL.md<br>D:\BaiduSyncdisk\workbuddy skills\openai-docs\SKILL.md | 完全相同 |
| opencode-session-visualizer | D:\BaiduSyncdisk\workbuddy skills\nigo-opencode-session-visualizer\SKILL.md<br>D:\BaiduSyncdisk\workbuddy skills\opencode-session-visualizer\SKILL.md | 完全相同 |
| pdf-qr-overlay | D:\BaiduSyncdisk\workbuddy skills\pdf-qr-overlay\SKILL.md<br>D:\BaiduSyncdisk\workbuddy skills\pdf二维码叠加\SKILL.md | 完全相同 |
| ppt-master | D:\BaiduSyncdisk\workbuddy skills\ppt-master\SKILL.md<br>D:\BaiduSyncdisk\workbuddy skills\ppt-master\ppt-master\skills\ppt-master\SKILL.md<br>D:\BaiduSyncdisk\workbuddy skills\ppt-master\skills\ppt-master\SKILL.md | 存在不同内容，不能直接删 |
| pua | D:\BaiduSyncdisk\workbuddy skills\pua\SKILL.md<br>D:\BaiduSyncdisk\workbuddy skills\pua\pua\SKILL.md | 存在不同内容，不能直接删 |
| review-agent | D:\BaiduSyncdisk\workbuddy skills\.system\review-agent\SKILL.md<br>D:\BaiduSyncdisk\workbuddy skills\review-agent\SKILL.md | 完全相同 |
| skill-creator | D:\BaiduSyncdisk\workbuddy skills\.system\skill-creator\SKILL.md<br>D:\BaiduSyncdisk\workbuddy skills\skill-creator\SKILL.md | 完全相同 |
| skill-installer | D:\BaiduSyncdisk\workbuddy skills\.system\skill-installer\SKILL.md<br>D:\BaiduSyncdisk\workbuddy skills\skill-installer\SKILL.md | 完全相同 |
| solo-review | D:\BaiduSyncdisk\workbuddy skills\solo-review\SKILL.md<br>D:\BaiduSyncdisk\workbuddy skills\universal-solo-review\SKILL.md | 完全相同 |
| vision-analysis | D:\BaiduSyncdisk\workbuddy skills\vision-analysis\SKILL.md<br>D:\BaiduSyncdisk\workbuddy skills\vision-analysis\vision-analysis\SKILL.md | 完全相同 |
| wanger-audit-sampling | D:\BaiduSyncdisk\workbuddy skills\WangEr-Audit-Sampling-Windows\SKILL.md<br>D:\BaiduSyncdisk\workbuddy skills\wanger-audit-sampling\SKILL.md | 完全相同 |
| 表格多线程处理 | D:\BaiduSyncdisk\workbuddy skills\excel-batch-process\excel-batch-process\SKILL.md<br>D:\BaiduSyncdisk\workbuddy skills\表格多线程处理\SKILL.md | 完全相同 |

目录名与入口name不同不自动视为错误；以下逐项登记供查找：

| 完整目录 | 实际name |
|---|---|
| D:\BaiduSyncdisk\workbuddy skills\WangEr-Audit-Sampling-Windows | wanger-audit-sampling |
| D:\BaiduSyncdisk\workbuddy skills\code-reviewer | code-review-skill |
| D:\BaiduSyncdisk\workbuddy skills\document-smart-filler-skill | document-smart-filler |
| D:\BaiduSyncdisk\workbuddy skills\minimax-multimodal-toolkit | mmx-cli |
| D:\BaiduSyncdisk\workbuddy skills\nigo-bank-flow-reconciliation | bank-flow-reconciliation |
| D:\BaiduSyncdisk\workbuddy skills\nigo-chenyiwei-bbs | chenyiwei-bbs |
| D:\BaiduSyncdisk\workbuddy skills\nigo-local-rag | local-rag |
| D:\BaiduSyncdisk\workbuddy skills\nigo-opencode-session-visualizer | opencode-session-visualizer |
| D:\BaiduSyncdisk\workbuddy skills\pdf二维码叠加 | pdf-qr-overlay |
| D:\BaiduSyncdisk\workbuddy skills\universal-solo-review | solo-review |
| D:\BaiduSyncdisk\workbuddy skills\反思想殖民 | fan-sixiang-zhi-min |

## 七、其他根文件与参考链接

根目录非技能文件仅按文件名登记，未读取凭据值，不计为技能入口：

- D:\BaiduSyncdisk\workbuddy skills\.cicpa_cookies.json
- D:\BaiduSyncdisk\workbuddy skills\.disable_to_model_invocation_migration.json
- D:\BaiduSyncdisk\workbuddy skills\.gitignore
- D:\BaiduSyncdisk\workbuddy skills\.model_invocation_to_override_migration.json
- D:\BaiduSyncdisk\workbuddy skills\.user_invocable_only_to_off_migration.json
- D:\BaiduSyncdisk\workbuddy skills\_bm_skillid_migration.json
- D:\BaiduSyncdisk\workbuddy skills\skills-sync-guide.md
- D:\BaiduSyncdisk\workbuddy skills\Trae挂载技能目录的正确做法.md

以下链接仅证明文件中出现过相关引用，不自动证明上游来源。Git证据或明确元数据之外仍待核验：

| 完整入口文件 | 文中引用的仓库链接（不作为作者证明） |
|---|---|
| D:\BaiduSyncdisk\workbuddy skills\agent-reach\SKILL.md | https://github.com/Panniantong/Agent-Reach |
| D:\BaiduSyncdisk\workbuddy skills\annual-report-red-flag-auditor\SKILL.md | https://github.com/noahnan-max/financial-red-flag-auditor-skill.git |
| D:\BaiduSyncdisk\workbuddy skills\caveman-compress\SKILL.md | https://github.com/JuliusBrussee/caveman |
| D:\BaiduSyncdisk\workbuddy skills\chen-yiwei-perspective\SKILL.md | https://github.com/alchaincyf/nuwa-skill |
| D:\BaiduSyncdisk\workbuddy skills\code-reviewer\SKILL.md | https://github.com/awesome-skills<br>https://github.com/awesome-skills/code-review-skill.git<br>https://github.com/awesome-skills/code-review-skill/blob/main/LICENSE |
| D:\BaiduSyncdisk\workbuddy skills\flowchart-generator\SKILL.md | https://github.com/jgraph/drawio-desktop/releases<br>https://github.com/jgraph/drawio-desktop/releases/download/v26.0.16/draw.io-26.0.16-windows-installer.exe<br>https://github.com/jgraph/drawio-desktop/releases/download/v26.0.16/draw.io-amd64-26.0.16.deb<br>https://github.com/jgraph/drawio-desktop/releases/download/v26.0.16/draw.io-arm64-26.0.16.deb<br>https://github.com/jgraph/drawio-desktop/releases/download/v26.0.16/draw.io-arm64-26.0.16.dmg<br>https://github.com/jgraph/drawio-desktop/releases/download/v26.0.16/draw.io-x86_64-26.0.16.dmg |
| D:\BaiduSyncdisk\workbuddy skills\flutter-dev\SKILL.md | https://github.com/Jeffallan/claude-skills |
| D:\BaiduSyncdisk\workbuddy skills\frontend-dev\SKILL.md | https://github.com/Leonxlnx/taste-skill<br>https://github.com/anthropics/skills/tree/main/skills/algorithmic-art<br>https://github.com/anthropics/skills/tree/main/skills/canvas-design |
| D:\BaiduSyncdisk\workbuddy skills\huashu-excel\SKILL.md | https://github.com/alchaincyf<br>https://github.com/alchaincyf/huashu-design<br>https://github.com/alchaincyf/huashu-design）。<br>https://github.com/alchaincyf/huashu-excel<br>https://github.com/alchaincyf/huashu-excel/releases |
| D:\BaiduSyncdisk\workbuddy skills\officecli-huaxin-format\SKILL.md | https://github.com/iOfficeAI/OfficeCLI/releases |
| D:\BaiduSyncdisk\workbuddy skills\ponytail-help\SKILL.md | https://github.com/DietrichGebert/ponytail |
| D:\BaiduSyncdisk\workbuddy skills\ppt-master\SKILL.md | https://github.com/farion1231/cc-switch<br>https://github.com/features/copilot<br>https://github.com/hugohe3/ppt-master<br>https://github.com/hugohe3/ppt-master-examples<br>https://github.com/hugohe3/ppt-master.git<br>https://github.com/hugohe3/ppt-master/discussions<br>https://github.com/hugohe3/ppt-master/issues<br>https://github.com/hugohe3/ppt-master/releases<br>https://github.com/hugohe3/ppt-master/stargazers<br>https://github.com/microsoft/ResearchStudio<br>https://github.com/openai/codex<br>https://github.com/phosphor-icons/core<br>https://github.com/simple-icons/simple-icons<br>https://github.com/tabler/tabler-icons |
| D:\BaiduSyncdisk\workbuddy skills\pptx-generator\SKILL.md | https://github.com/microsoft/markitdown |
| D:\BaiduSyncdisk\workbuddy skills\private-equity-investment-dd\SKILL.md | https://github.com/noahnan-max/private-equity-investment-dd-skill.git |
| D:\BaiduSyncdisk\workbuddy skills\react-native-dev\SKILL.md | https://github.com/expo/skills |
| D:\BaiduSyncdisk\workbuddy skills\report-helper\SKILL.md | https://github.com/Jiaranbb<br>https://github.com/Jiaranbb/autoskin-codex<br>https://github.com/Jiaranbb/content-reader<br>https://github.com/Jiaranbb/dreamy-photo<br>https://github.com/Jiaranbb/ecommerce-helper<br>https://github.com/Jiaranbb/jiucai-helper<br>https://github.com/Jiaranbb/pdf-reader<br>https://github.com/Jiaranbb/report-helper<br>https://github.com/Jiaranbb/report-helper/issues<br>https://github.com/Jiaranbb/report-helper`、`交流和建议可联系作者：嘉然<br>https://github.com/Jiaranbb/report-helper。安装完成后提醒我按当前工具要求重启或刷新<br>https://github.com/Jiaranbb/xhs-reader |
| D:\BaiduSyncdisk\workbuddy skills\shaoniannu-perspective\SKILL.md | https://github.com/alchaincyf/nuwa-skill |
| D:\BaiduSyncdisk\workbuddy skills\skill-installer\SKILL.md | https://github.com/openai/skills/tree/main/skills/.curated<br>https://github.com/openai/skills/tree/main/skills/.curated`<br>https://github.com/openai/skills/tree/main/skills/.experimental<br>https://github.com/openai/skills/tree/main/skills/.system |
| D:\BaiduSyncdisk\workbuddy skills\stop-slop-zh\SKILL.md | https://github.com/Leonxlnx/taste-skill/issues<br>https://github.com/anthropics/knowledge-work-plugins/issues<br>https://github.com/hardikpandya/stop-slop<br>https://github.com/pencil20388-eng/content-topic-judgment<br>https://github.com/pencil20388-eng/stop-slop-zh.git |
| D:\BaiduSyncdisk\workbuddy skills\tender-bidding-assistant\SKILL.md | https://github.com/gechengling/tender-bidding-assistant<br>https://github.com/gechengling/tender-bidding-assistant* |
| D:\BaiduSyncdisk\workbuddy skills\tianchuan-perspective\SKILL.md | https://github.com/alchaincyf/nuwa-skill |

## 八、后续同步规则

1. 以当前实况表为起点，再核实目标的实际.git、origin、分支及本地变更；没有.git的目录按其已证实来源比对，不能猜仓库或把引用链接当上游。
2. 历史登记或来源待确认项，先查明再更新；自维护分支和已经独立发布的技能，不用旧合集覆盖。
3. 修改已有文件前备份到C:\Users\27651\BackUp\项目名_年月日_时分秒并校验；只写实际差异，保留编码和BOM，写后回读。
4. 本地有改动或历史分叉时不自动覆盖；同名目录不等于可删除。删除按用户确认的精确清单移入Windows回收站。
5. 同步结束重新核验入口链接、文件哈希和真实读取范围，不把启动成功当功能完成，不自动重启应用。
6. 不继续使用旧指南中的批量覆盖示例；本次只改两个授权任务，没有同步全库代码或运行所有技能。

## 九、本次变更与历史日志

### 2026-10-30

- 全量重建当前目录、来源证据、Git、嵌套入口、同名组和链接清单，纠正旧统计及Codex链接描述。
- 将核对技能统一为audit-report-checker 2.2.0；原两个技能及中文、嵌套入口备份后回收，更新调用步骤、README及changelog。
- 其他重复入口、未知来源和Git异常仅登记；未擅自清理或更新其他技能。
- 备份：C:\Users\27651\BackUp\audit-report-checker整合_20261030_181000；逐项实况与回收证据见本次交付目录。

### 以下为旧日志，不代表当前目录、上游最新版或来源已全部查实

| 时间 | 操作 | 详情 |
|------|------|------|
| 2026-10-15 | 按实时来源增量更新 | 核验 46 个 GitHub 上游地址，另核验关联方登记的 Gitee OpenCLI 镜像；更新 **37 个技能内容**，另为 requirement-workflow 和 related-party-identification 更新来源核验记录。Book-to-skill 快进 `526f362`→`a24e62f`，保留两份旧的未跟踪附加文件；Humanizer-zh 合并上游正文并保留本地元数据。PPT Master **6.6.0→6.7.0**，同步三个现存入口，只写差异，主入口和标准嵌套入口各约 12,880 个未变文件不重写；深层旧副本额外补齐早于基线的 548 份官方文件。excel-master 保留本地分支，其他自维护改动保留；未删除文件、未自动重启、未安装上游新增技能。requirement-workflow 的 9 个内嵌来源已核验，6 个有上游变化但保留本地适配与固定基线；关联方两个上游固定版本一致。**验证限制**：关联方识别技能更新前已有同步冲突副本导致编码校验及部分旧测试失败，本轮未删除这些副本或修改其运行代码。备份：`C:\Users\27651\BackUp\workbuddy-skills-sync_20261015_141231`。 |
| 2026-07-10 | 首次同步 | 同步 5 个：code-reviewer、excel-master、a-stock-financial、chen-yiwei-perspective、tianchuan-perspective。<br>跳过（仓库太大）：ppt-master。 |
| 2026-07-10 | 安装新技能 | 从 nigo81/nigo-skills 安装 5 个：audit-report-checker、china-law-search、cicpa-company-query、related-party-identification、shaoniannu-perspective。排除 local-rag、chenyiwei-bbs。 |
| 2026-07-26 | 全面盘点 | 总数 55→95。新增来源：mattpocock/skills（5个）、MiniMax-AI/skills 扩至 13 个、nigo-skills 新增 flowchart-generator、独立仓库新增 9 个、自写新增 6 个。<br>重新分类：obra(14)、MiniMax(13)、mattpocock(5)、nigo(9)、ponytail(6)、独立仓库(21)、自写(18)、待确认(7)。 |
| 2026-07-26 | 全量同步 | 同步 35 个 skill 至最新：obra/superpowers（14个→07-24 v6.2.0）、ponytail（6个→07-16）、nigo-skills（9个→07-17）、book-to-skill（1个→07-24）。<br>mattpocock/skills 上游重构：diagnose→diagnosing-bugs、to-issues→to-tickets、to-prd→to-spec，grill-me 已删除，skill 移至 `skills/engineering/` 子目录。<br>暂不同步：excel-master（本地有自定义增强，与远程分叉）。<br>已最新：darwin-skill、humanizer-zh、stop-slop、tcm-skill、MiniMax-AI/skills（13个）。 |
| 2026-07-26 | 全量同步 | obra/superpowers（14个）、ponytail（6个）、nigo-skills（9个）、book-to-skill 同步至最新。mattpocock/skills 重构：diagnose→diagnosing-bugs、to-issues→to-tickets、to-prd→to-spec、grill-me 上游已删除。 |
| 2026-08-06 | 全量同步 | 更新 book-to-skill、darwin-skill、diagnosing-bugs、improve-codebase-architecture、to-spec、annual-report-red-flag-auditor、private-equity-investment-dd、slide-maker 至 GitHub 当前版本；annual-report-red-flag-auditor、private-equity-investment-dd 恢复为单层目录。ppt-master 发现上游更新但本轮继续单独处理；未安装上游新增 skill。 |
| 2026-09-04 | 现有 Skill 更新 | 更新现有已安装第三方 Skill，不自动安装上游新增 Skill。主目录合并 49 个合集/独立来源 Skill，另更新 ppt-master、pua，并快进 book-to-skill、darwin-skill；excel-master 因本地历史独立且内容更新日期晚于上游，保留本地版本。requirement-workflow 逐项检查 9 个登记来源，更新 7 个来源固定提交并保留自包含、本地路径和授权边界。全过程未创建备份，未执行永久删除。 |
| 2026-09-21 | 全量检查与同步 | 实测 138 个顶层目录、137 个 `SKILL.md`、22 个含 `.git` 的仓库。**更新 12 个 Skill**：obra/superpowers 9 个（brainstorming、executing-plans、requesting-code-review、subagent-driven-development、systematic-debugging、test-driven-development、using-superpowers、writing-plans、writing-skills）、mattpocock/domain-modeling、slide-maker（5.3.0→5.5.0）、caveman；快进 book-to-skill（`a6cad12`→`526f362`）、darwin-skill（`5539516`→`8a8b662`）。**保留本地版本**：nigo81 全部 9 个、mattpocock 4 个（grill-with-docs、improve-codebase-architecture、to-spec、to-tickets）、ponytail、minimax-docx、agently-mail、code-reviewer、tender-bidding-assistant、stop-slop-zh——差异均为本地 frontmatter 适配；related-party-identification 本地为自有仓库扩展版。**ppt-master 单独同步**：顶层与 `skills/ppt-master` 均更新至上游 v6.6.0（顶层 `SKILL.md` 由 73794 字节的自包含旧版替换为上游 10185 字节版本，references / scripts / templates / workflows 全量同步，复检 0 处上游侧差异）。**新增安装 24 个上游 Skill**：diagnosing-superpowers；MiniMax 的 buddy-sings、gif-sticker-maker、minimax-music-gen、minimax-music-playlist；mattpocock 的 ask-matt、code-review、codebase-design、implement、prototype、research、resolving-merge-conflicts、setup-matt-pocock-skills、tdd、triage、wayfinder、wizard；nigo81 的 bank-flow-reconciliation、opencode-session-visualizer、chenyiwei-bbs、local-rag；caveman 的 cavecrew、caveman-compress、caveman-stats。**excel-master 按用户决定保留本地版**（本地领先 5、落后 30）。备份：`C:\Users\27651\BackUp\workbuddy-skills-sync_20260921_121342`（含 ppt-master 备份共约 25592 个文件），全过程未执行永久删除。 |
| 2026-09-21 | 补充收录 3 个来源 | 经 GitHub 核实后，把 3 个此前未收录的 Skill 纳入管理并同步至上游最新：**agent-reach**（Panniantong/Agent-Reach，上游新增 Boss直聘支持，15→16 平台，更新 `SKILL.md`、`SKILL_en.md`、`references/career.md`）；**huashu-excel**（alchaincyf/huashu-excel，更新 `references/charts.md` 焦点色章节与 `references/xlsx-craft.md` 表格落法，修复 `scripts/profile_table.py` 的 CSV 误报 bug）；**writing / writing-md**（Anbeeld/WRITING.md，1.3.1→1.4.2，新增 `references/editing-integrity.md`、`medium-routing.md`、`voice-calibration.md`，并同步更新本地保留的 `WRITING.md`、`WRITING-compact.md`、`WRITING-mini.md`）。三处复检均为 0 处上游侧差异。备份：`C:\Users\27651\BackUp\workbuddy-skills-sync2_20260921_123303`（49 个文件）。 |
| 2026-09-21 | 重复目录去重 | 顶层 `writing` 与 `writing-md` 内容逐字节相同、`name` 同为 `writing`，属重复安装。按用户决定保留 `writing`、删除 `writing-md`：先备份 21 个文件至 `C:\Users\27651\BackUp\writing-md_20260921_123937`，再经 Windows 回收站删除，未永久删除。**过程中发现顶层 `writing` 实为指向 `writing-md` 的目录联接（Junction）**，删除后成为悬空链接，已移除链接并用备份还原为真实目录（21 个文件、版本 1.4.2、逐字节一致）。随后又清理 `writing/` 内残留的上游 1.3.1 旧版嵌套副本（9 个文件），`writing` 最终为 12 个文件的标准结构，与上游一致。详见 `技能同步记录_20260921.md` 第九节。 |
