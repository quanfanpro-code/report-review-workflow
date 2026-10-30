"""报表确定性验算；最终结论仍须当前agent核实取数与适用性。"""
from dataclasses import dataclass
from decimal import Decimal
from calculator import parse_number, check_equal,UNITS,amount_in_unit

@dataclass
class CheckItem:
    rule_name: str
    passed: bool
    expected: object
    actual: object
    difference: object
    description: str
    severity: str = "warning"

REQUIRED_FIELDS = {
    "资产负债表": ["流动资产合计","非流动资产合计","资产总计","流动负债合计","非流动负债合计","负债合计","所有者权益合计","负债和所有者权益总计"],
    "利润表": ["营业收入","营业成本","税金及附加","销售费用","管理费用","研发费用","财务费用","其他收益","投资收益","公允价值变动收益","净敞口套期收益","信用减值损失","资产减值损失","资产处置收益","营业利润","营业外收入","营业外支出","利润总额","所得税费用","净利润"],
    "现金流量表": ["经营活动产生的现金流量净额","投资活动产生的现金流量净额","筹资活动产生的现金流量净额","现金及现金等价物净增加额","期初现金及现金等价物余额","期末现金及现金等价物余额"],
    "所有者权益变动表": ["上年年末余额","本年年末余额"],
}

def get_value(statement, name, period):
    value = statement.get(name)
    result = value.get(period) if isinstance(value, dict) else None
    zeros = statement.get("_meta", {}).get("zero_fields", [])
    confirmed = name in zeros if isinstance(zeros, list) else name in zeros.get(period, [])
    if result in (None, "") and confirmed:
        return "0"
    if result not in (None, ""):
        unit=statement.get("_meta",{}).get("unit","元")
        if unit not in UNITS:return "单位未确认"
        try:return format(amount_in_unit(result,unit),"f")
        except ValueError:return "金额或单位冲突"
    return result

def pending(name, reason):
    return CheckItem(name, False, None, None, None, "未执行：" + reason)

def comparison(name, expected, actual, tolerance="0.01"):
    result = check_equal(expected, actual, tolerance)
    if result.get("error"):
        return pending(name, result["error"])
    return CheckItem(name, result["match"], format(parse_number(expected),"f"), actual, result["diff"], "计算一致" if result["match"] else "发现数值差异，须回原文核实", "info" if result["match"] else "warning")

def check_balance_sheet(statement, tolerance="0.01"):
    results=[]
    definitions=[("资产合计",["流动资产合计","非流动资产合计"],"资产总计"),("负债合计",["流动负债合计","非流动负债合计"],"负债合计"),("权益平衡",["负债合计","所有者权益合计"],"负债和所有者权益总计"),("资产负债平衡",["资产总计"],"负债和所有者权益总计")]
    for period in ("current","prior"):
        for name, inputs, target in definitions:
            name += "（本期）" if period=="current" else "（上期）"
            values=[get_value(statement,k,period) for k in inputs+[target]]
            if any(v in (None,"") for v in values):
                results.append(pending(name,"必要项目缺失"));continue
            try:
                results.append(comparison(name,sum((parse_number(v) for v in values[:-1]),Decimal(0)),values[-1],tolerance))
            except ValueError as exc:results.append(pending(name,str(exc)))
    return results

def check_income_statement(statement, tolerance="0.01"):
    results=[]
    expenses=["营业成本","税金及附加","销售费用","管理费用","研发费用","财务费用"]
    gains=["其他收益","投资收益","公允价值变动收益","净敞口套期收益","资产处置收益"]
    for period in ("current","prior"):
        suffix="（本期）" if period=="current" else "（上期）"
        fields=["营业收入"]+expenses+gains+["信用减值损失","资产减值损失","营业利润"]
        values={k:get_value(statement,k,period) for k in fields}
        if any(v in (None,"") for v in values.values()):results.append(pending("营业利润推导"+suffix,"缺少项目；未列示项目须在结构契约中确认零值"))
        else:
            try:
                numbers={k:parse_number(v) for k,v in values.items()}
                mode=statement.get("_meta",{}).get("impairment_presentation")
                if mode not in ("signed_gain","positive_loss") and any(numbers[k] for k in ("信用减值损失","资产减值损失")):
                    results.append(pending("营业利润推导"+suffix,"未确认减值损益列示方式"))
                else:
                    expected=numbers["营业收入"]-sum((numbers[k] for k in expenses),Decimal(0))+sum((numbers[k] for k in gains),Decimal(0))
                    impair=numbers["信用减值损失"]+numbers["资产减值损失"]
                    expected += -impair if mode=="positive_loss" else impair
                    results.append(comparison("营业利润推导"+suffix,expected,values["营业利润"],tolerance))
            except ValueError as exc:results.append(pending("营业利润推导"+suffix,str(exc)))
        for name,inputs,target in [("利润总额推导",[("营业利润",1),("营业外收入",1),("营业外支出",-1)],"利润总额"),("净利润推导",[("利润总额",1),("所得税费用",-1)],"净利润")]:
            try:
                expected=sum((parse_number(get_value(statement,k,period))*sign for k,sign in inputs),Decimal(0))
                results.append(comparison(name+suffix,expected,get_value(statement,target,period),tolerance))
            except ValueError as exc:results.append(pending(name+suffix,str(exc)))
        if get_value(statement,"综合收益总额",period) is not None:
            try:
                expected=parse_number(get_value(statement,"净利润",period))+parse_number(get_value(statement,"其他综合收益的税后净额",period))
                results.append(comparison("综合收益总额"+suffix,expected,get_value(statement,"综合收益总额",period),tolerance))
            except ValueError as exc:results.append(pending("综合收益总额"+suffix,str(exc)))
    return results

def check_cash_flow_statement(statement,tolerance="0.01"):
    results=[]
    for period in ("current","prior"):
        suffix="（本期）" if period=="current" else "（上期）"
        try:
            expected=sum((parse_number(get_value(statement,k,period)) for k in REQUIRED_FIELDS["现金流量表"][:3]),Decimal(0))
            fx=None
            for key in ("汇率变动对现金的影响","汇率变动对现金及现金等价物的影响","汇率变动对现金的影响额"):
                if get_value(statement,key,period) is not None:fx=get_value(statement,key,period);break
            if fx is not None:expected+=parse_number(fx)
            elif not statement.get("_meta",{}).get("fx_absent_confirmed",False):
                results.append(pending("现金流量净增加额"+suffix,"需确认汇率影响为零或不适用"))
                expected=None
            if expected is not None:results.append(comparison("现金流量净增加额"+suffix,expected,get_value(statement,"现金及现金等价物净增加额",period),tolerance))
        except ValueError as exc:results.append(pending("现金流量净增加额"+suffix,str(exc)))
        try:
            expected=parse_number(get_value(statement,"期初现金及现金等价物余额",period))+parse_number(get_value(statement,"现金及现金等价物净增加额",period))
            results.append(comparison("现金余额勾稽"+suffix,expected,get_value(statement,"期末现金及现金等价物余额",period),tolerance))
        except ValueError as exc:results.append(pending("现金余额勾稽"+suffix,str(exc)))
    return results

def check_equity_change_statement(statement,tolerance="0.01"):
    results=[]
    matrices=statement.get("_matrix",{})
    if not matrices:return [pending("权益变动矩阵","只有余额或缺完整矩阵，不能代表期初加变动等于期末")]
    required=statement.get("_meta",{}).get("required_periods") or list(statement.get("_meta",{}).get("periods",{})) or ["current","prior"]
    for period in required:
        if period not in matrices:results.append(pending("权益矩阵-"+period,"缺少该期完整矩阵"))
    for period,matrix in matrices.items():
        try:
            rows=matrix["rows"]; names=matrix["columns"];begin=matrix["beginning_row"];end=matrix["ending_row"];changes=matrix["change_rows"];total=matrix["total_col"]
            indices=[begin,end,*changes]
            if begin==end or not changes or any(type(x) is not int or x<0 or x>=len(rows) for x in indices) or len(set(changes))!=len(changes) or begin in changes or end in changes:raise ValueError("矩阵期初期末或变动行无效，不能自比较")
            if type(total) is not int or total<1 or total>len(names):raise ValueError("矩阵合计列无效")
            for col,name in enumerate(names,1):
                unit=statement.get("_meta",{}).get("unit","元")
                expected=amount_in_unit(rows[begin][col],unit)+sum((amount_in_unit(rows[r][col],unit) for r in changes),Decimal(0))
                unit=statement.get("_meta",{}).get("unit","元")
                if unit not in UNITS:raise ValueError("矩阵金额单位未确认")
                results.append(comparison("权益变动-"+name+"-"+period,expected,amount_in_unit(rows[end][col],unit),tolerance))
            operations=matrix.get("column_ops",{})
            for i in sorted(set(indices)):
                row=rows[i]
                expected=sum((amount_in_unit(row[col],unit)*(-1 if operations.get(str(col))=="-" else 1) for col in range(1,len(names)+1) if col!=total),Decimal(0))
                results.append(comparison("权益横向合计-"+str(i)+"-"+period,expected,amount_in_unit(row[total],unit),tolerance))
        except (ValueError,KeyError,IndexError,TypeError) as exc:results.append(pending("权益矩阵-"+period,str(exc)))
    return results

if __name__=="__main__":
    import json
    print(json.dumps(REQUIRED_FIELDS,ensure_ascii=False,indent=2))
