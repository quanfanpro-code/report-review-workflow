# 显式标注与回填

结构由当前agent判断，运算走execute_annotations/execute_relation。小计只绑本组明细，“其中”不重计，小计与其明细不能同时加。零合计也检查。超过20行、多币种、收入成本表不能按名称跳过。比例不当金额；互斥完整同一期账龄金额列可合计。空白和负号先查语义。

以下rows[0]是表头，第1/2行为明细、第3行为合计，列1/2/3分别同期间余额/准备/净值：
```json
{
 "header_rows":[0],
 "vertical":[{"target_row":3,"col":1,"operands":[{"row":1,"op":"+"},{"row":2,"op":"+"}]}],
 "horizontal":[{"rows":[1,2,3],"operands":[{"col":1,"op":"+"},{"col":2,"op":"-"}],"result_col":3}],
 "columns":[{"col":1,"type":"amount","period":"current"},{"col":2,"type":"amount","period":"current"},{"col":3,"type":"amount","period":"current"}]
}
```
op是业务符号，保留源数字正负。期初+增加-减少=期末须设kind="movement"，避免跨期金额混加；比例列声明type="percentage"。
跨表关系示例：
```json
{
 "check_id":"货币资金本期","rule_name":"货币资金表注",
 "entity":"单体","period":"current","currency":"CNY","formula":"cash+bank",
 "variables":{
  "cash":{"table_id":5,"row":1,"col":1,"entity":"单体","period":"current","currency":"CNY","unit":"元"},
  "bank":{"table_id":5,"row":2,"col":1,"entity":"单体","period":"current","currency":"CNY","unit":"元"}
 },
 "target":{"table_id":0,"row":1,"col":1,"entity":"单体","period":"current","currency":"CNY","unit":"元"}
}
```
源引用须精确且目标不得自比；主体/期间/币种及单位与已确认来源冲突时报错，不能用引用覆盖来源单位。金额先换成元再比较；内嵌单位冲突不能放行。数量/比率用kind="quantity"/"ratio"，EPS需正确加权分母和稀释分子调整。

初始化前由当前agent依据原文完整声明relations.json，顶层checks列出所有适用跨表关系，每条有唯一check_id。清单绑定输入指纹，回填须逐条完整对应，缺项、增加或改写公式均拒绝。无适用关系用{"checks":[],"not_applicable_basis":"实际依据"}并将跨表对象标不适用；没有清单不能宣称已检查。大清单可在跨表回填写use_declared_relations=true，程序执行全部已确认关系，避免重复抄写；当前agent仍须先核实完整清单及每条来源。程序验证声明的关系是否全部执行，不能代替agent发现未声明的业务关系。

回填须恰好覆盖本批所有check_ids，原样复制batch_id/source_fingerprint。每个result至少check_id、rule_name、status、description、review；table通过还需annotation或relations，structure通过需structure声明，cross_relations通过需验算。extraction缺口先补提取重新初始化，不能直接通过。

review结构示例（占位必须换实际值）：
```json
{
 "agent":"实际执行的当前agent","check_id":"与外层一致","conclusion":"通过",
 "source_fingerprint":"与批次一致","basis":"说明实际核对的主体、期间、结构和公式",
 "source_refs":[{"quote":"本对象material中真实存在的逐字引文"}]
}
```
回填顶层{"batch_id":"实际值","source_fingerprint":"实际值","results":[]}。
对象另有table_meta可声明entity/period/currency/unit/dash_is_zero。程序验证范围、指纹、引文及计算，不能替代真实语义判断。算术不平不能标通过。无法判断保留待核实或未执行，不删问题；误报记已排除误报并留原计算和依据。

原生all_raw表必须声明header_rows和每个参与列的type=amount、period；没有表头时显式header_rows=[]，列角色仍须完整。比例或期间不明不能默认放行。权益矩阵须有不同的期初、期末及变动行，默认两期均检查；实际只有一期时在_meta.required_periods中明确，并留适用性依据。

长表按完整行分片，row_range是原始行范围，从0起且末端不含；每片含原始首部、表头及章节、主体、期间、币种单位背景，不明口径标待确认。单行或背景超过限额时明确停止该提取契约，先有依据地拆解该单元格，不截断丢失。长文字仍按字符span分片并重叠。最后cross_relations按全部已声明关系核实跨表，不能只检查单片内部。两档应检一致，下一批读取不等于完成复核。
