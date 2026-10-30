from decimal import Decimal
import pytest
import calculator_rules as rules
import run_check as checks

def test_汇率影响不能因三类净额相等而忽略():
    vals={"经营活动产生的现金流量净额":"10","投资活动产生的现金流量净额":"20","筹资活动产生的现金流量净额":"30","汇率变动对现金的影响":"5","现金及现金等价物净增加额":"60","期初现金及现金等价物余额":"100","期末现金及现金等价物余额":"160"}
    statement={k:{"current":v,"prior":v} for k,v in vals.items()}
    assert all(not x.passed for x in rules.check_cash_flow_statement(statement) if "净增加额" in x.rule_name)

@pytest.mark.parametrize("impair,profit", [("10","60"),("-10","40")])
def test_减值计提与转回方向(impair,profit):
    vals={k:"0" for k in rules.REQUIRED_FIELDS["利润表"]}
    vals.update({"营业收入":"100","营业成本":"50","信用减值损失":impair,"营业利润":profit,"利润总额":profit,"净利润":profit})
    stmt={k:{"current":v,"prior":v} for k,v in vals.items()}
    stmt["_meta"]={"impairment_presentation":"signed_gain"}
    rows=rules.check_income_statement(stmt)
    assert all(x.passed for x in rows)

def test_只有权益余额不能通过():
    rows=rules.check_equity_change_statement({"上年年末余额":{"current":"100"},"本年年末余额":{"current":"999"}})
    assert rows and not any(x.passed for x in rows)

def test_权益矩阵逐成分():
    stmt={"_matrix":{"current":{"columns":["股本","未分配利润","合计"],"rows":[["期初","100","20","120"],["变动","0","10","10"],["期末","100","999","130"]],"beginning_row":0,"change_rows":[1],"ending_row":2,"total_col":3}}}
    rows=rules.check_equity_change_statement(stmt)
    assert any(not x.passed and "未分配利润" in x.rule_name for x in rows)

def test_净值不能用余额兜底():
    assert checks._resolve_note_value({"账面余额":"100"},"账面价值","账面余额-坏账准备") is None

def test_报表缺项目不计通过():
    results=[]
    checks.check_statement_to_note({"资产负债表":{}},{"货币资金":{"field":"期末余额"}},{},results)
    assert results and not any(r["passed"] for r in results)

def test_无法解析的变动表不崩溃():
    rows=[]
    checks.check_note_internal_reconcile({"薪酬":{}},{"薪酬":[{"values":{"期初余额":"未知","本期增加":"20","本期减少":"10","期末余额":"110"}}]},rows)
    assert rows and rows[0]["status"]=="未执行"

def test_程序不能伪造终审():
    rows=[]
    checks.check_statement_to_note({"资产负债表":{"货币资金":{"current":"100"}}},{"货币资金":{"field":"期末余额"}},{"货币资金":[{"values":{"期末余额":"100"}}]},rows)
    assert not any(r.get("review") for r in rows)
    assert all(r["status"]=="未执行" for r in rows)

def test_跨表金额引用换算并比较():
    table={"id":0,"source_file":"报告.docx","entity":"单体","period":"current","currency":"CNY","unit":"万元","rows":[["甲","1"],["乙","10000"]]}
    target={"id":1,"source_file":"另一表.docx","entity":"单体","period":"current","currency":"CNY","unit":"元","rows":[["甲","10000"]]}
    rule={"check_id":"跨表","entity":"单体","period":"current","currency":"CNY","formula":"a","variables":{"a":{"table_id":0,"row":0,"col":1}},"target":{"table_id":1,"row":0,"col":1}}
    result=checks.execute_relation(rule,{0:table,1:target})
    assert result["calculation"]["match"] is True
    assert Decimal(str(result["expected"]))==Decimal("10000")

def test_不同主体不能硬比较():
    table={"id":0,"source_file":"报告.docx","entity":"母公司","period":"prior","currency":"CNY","unit":"元","rows":[["甲","1"]]}
    rule={"check_id":"跨表","entity":"合并","period":"current","currency":"CNY","formula":"a","variables":{"a":{"table_id":0,"row":0,"col":1}},"target":{"table_id":0,"row":0,"col":1}}
    with pytest.raises(ValueError,match="主体|期间"):
        checks.execute_relation(rule,{0:table})

def test_内嵌金额单位与声明冲突不放行():
    table={"id":0,"source_file":"报告.docx","entity":"单体","period":"current","currency":"CNY","unit":"元","rows":[["甲","1万元"],["乙","10000"]]}
    rule={"check_id":"关系","entity":"单体","period":"current","currency":"CNY","formula":"a","variables":{"a":{"table_id":0,"row":0,"col":1}},"target":{"table_id":0,"row":1,"col":1}}
    with pytest.raises(ValueError,match="单位"):
        checks.execute_relation(rule,{0:table})

def test_明确零字段可以处理空值():
    statement={"甲":{"current":None},"_meta":{"zero_fields":["甲"]}}
    assert rules.get_value(statement,"甲","current")=="0"
def test_权益原始表头不当金额():
    matrix={"rows":[["项目","股本","未分配利润","合计"],["期初","100","80","180"],["变动","0","20","20"],["期末","100","100","200"]],"columns":["股本","未分配利润","合计"],"beginning_row":1,"ending_row":3,"change_rows":[2],"total_col":3}
    rows=rules.check_equity_change_statement({"_meta":{"required_periods":["current"]},"_matrix":{"current":matrix}})
    assert len(rows)==6 and all(r.passed for r in rows)

def test_万元报表不能用百元容差掩盖差异():
    fields={k:{"current":"0","prior":"0"} for k in rules.REQUIRED_FIELDS["资产负债表"]}
    fields["资产总计"]={"current":"0.001","prior":"0.001"}
    fields["_meta"]={"unit":"万元"}
    rows=rules.check_balance_sheet(fields)
    assert any(r.passed is False and r.difference==10 for r in rows)

def test_显式关系保留业务名称():
    from run_check import execute_relation
    tables={0:{"id":0,"source_file":"报告","entity":"单体","period":"current","currency":"CNY","unit":"元","rows":[["甲","100"],["乙","100"]]}}
    rule={"rule_name":"货币资金表注","entity":"单体","period":"current","currency":"CNY","formula":"x","variables":{"x":{"table_id":0,"row":0,"col":1}},"target":{"table_id":0,"row":1,"col":1}}
    assert execute_relation(rule,tables)["rule_name"]=="货币资金表注"

