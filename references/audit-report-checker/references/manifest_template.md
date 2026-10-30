# 显式结构契约

先读完整原表，确定主体、期间、单位、币种、来源和行列。索引从0开始；all_raw保留表头，first_data_row必须看原文确定，last_data_row不含末端。以下是有效结构，实际文件名和位置由当前agent替换：
```json
{
  "files":{"审计报告.docx":{"loader":"docx"}},
  "statements_map":{
    "资产负债表":{
      "source":"审计报告.docx","loader":"docx","source_table":0,
      "entity":"单体","currency":"CNY","unit":"元",
      "periods":{"current":"2025-12-31","prior":"2024-12-31"},
      "first_data_row":1,"item_col":0,"current_col":1,"prior_col":2,
      "zero_fields":[],"field_aliases":{}
    }
  }
}
```
DOCX/PDF source_table用已提取全局ID，0有效；Excel用loader=xlsx、sheets=["资产负债表"]。
利润表按原列示增加impairment_presentation="signed_gain"（损失负号，转回正号）或"positive_loss"（正数损失扣减）。现金表没列汇率时只有确认零才设fx_absent_confirmed=true。
zero_fields可以是两期均零的项目名列表，或{"current":["某项目"],"prior":[]}。所有零值声明另留原文终审依据。

权益完整矩阵示例（作为statements_map里一项）：
```json
{
 "source":"审计报告.docx","loader":"docx","kind":"matrix","source_table":[3,4],
 "entity":"单体","currency":"CNY","unit":"元",
 "matrix":{
  "current":{"table_id":3,"beginning_row":1,"change_rows":[2,3],"ending_row":4,"columns":["股本","未分配利润","合计"],"total_col":3},
  "prior":{"table_id":4,"beginning_row":1,"change_rows":[2,3],"ending_row":4,"columns":["股本","未分配利润","合计"],"total_col":3}
 }
}
```
变动行选择不重叠层级，column_ops声明库存股等抵减。综合收益、投入、分配是变动行，不是权益成分列。只取余额不算矩阵全验。
输出金额字符串和_meta、_source_map、_matrix/_matrix_raw。续表sheets或merge_into必须同主体/期间/币种单位；冲突停止。合并和母公司分别生成标准名statements文件执行，不能混合merge_into。没有四表时不虚构manifest。
跨表用relations明确完整源单元格，见structure_annotation.md，包含两期表注、权益期末、净利润及现金构成桥接。
