"""离线草筛及显式关系验算；语义工作与终审由当前agent完成。"""
import argparse
import re
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from calculator import parse_number,check_equal,reconcile,evaluate_expression,UNITS,amount_in_unit
from calculator_rules import check_balance_sheet,check_income_statement,check_cash_flow_statement,check_equity_change_statement
from 复核契约 import normalize_result,save_json,load_json,stable_id,guard_outputs

def create_result(check_type,rule_name,severity="warning",passed=False,description="",expected=None,actual=None,difference=None,source_location="",target_location="",evidence="",page=None,context="",confidence=None,**extra):
    item={"check_type":check_type,"rule_name":rule_name,"description":description,"source_location":source_location,"target_location":target_location,"evidence":evidence,"page":page,"context":context,"calculation":{"match":passed,"expected":expected,"actual":actual,"difference":difference},"expected":expected,"actual":actual,"difference":difference,**extra}
    return normalize_result(item)

def _index(value,length):
    if type(value) is not int or not 0<=value<length:raise ValueError("来源索引越界或类型无效")
    return value

def _cell(table,row,col):
    row=_index(row,len(table.get("rows",[])))
    col=_index(col,len(table["rows"][row]))
    value=table["rows"][row][col]
    if value in (None,""):raise ValueError("缺少金额，不能自动作零")
    if str(value).strip() in ("-","—","–") and table.get("dash_is_zero") is True:value="0"
    return value

def _percentage(table,col,annotation=None):
    names=[str(h) for h in table.get("headers",[])]
    if col<len(names) and re.search(r"%|比例|占比|损失率|rate",names[col],re.I):return True
    return any(c.get("col")==col and c.get("type") in ("percentage","percent","ratio") for c in (annotation or {}).get("columns",[]))

def _ref(table,row,col):
    return {"source_file":table.get("source_file",""),"table_id":table.get("id"),"row":row,"col":col,"page":table.get("page"),"chapter":table.get("chapter",""),"entity":table.get("entity"),"period":table.get("period"),"currency":table.get("currency"),"unit":table.get("unit"),"raw_value":table["rows"][row][col]}

def _amount(table,row,col):
    return amount_in_unit(_cell(table,row,col),table.get("unit","元"))

def _computed(table,kind,label,expected,actual,refs,target,tolerance="0.01"):
    result=check_equal(expected,actual,tolerance)
    loc=f'表格ID {table.get("id")} 行{target.get("row")} 列{target.get("col")}'
    item=create_result(kind,label,passed=result["match"],description="数值一致，待语义复核" if result["match"] else "存在数值差异，待回原文核实",expected=expected,actual=actual,difference=result["diff"],source_location=loc,source_file=table.get("source_file",""),page=table.get("page"),chapter=table.get("chapter",""),context=loc,source_refs=refs+[target],operands=refs,target=target)
    item["calculation"]["tolerance"]=tolerance
    return item

def execute_annotations(table,annotation):
    if table.get("row_model")=="all_raw":
        header_rows=annotation.get("header_rows",table.get("header_rows"))
        if not isinstance(header_rows,list):raise ValueError("原生表须明确表头行和列角色")
        for row in header_rows:_index(row,len(table.get("rows",[])))
        columns={c["col"]:c for c in annotation.get("columns",[])}
        used={r.get("col") for r in annotation.get("vertical",[])}
        for rule in annotation.get("horizontal",[]):used.update([rule.get("result_col"),*[o.get("col") for o in rule.get("operands",[])]])
        for col in used:
            if col not in columns or columns[col].get("type")!="amount" or not columns[col].get("period"):raise ValueError("原生表金额列须声明类型和期间，比例列不能作金额")
        width=max((len(row) for row in table.get("rows",[])),default=0)
        table={**table,"headers":["/".join(str(table["rows"][r][c]) for r in header_rows if c<len(table["rows"][r])) for c in range(width)]}
    results=[]
    for rule in annotation.get("vertical",[]):
        row=_index(rule.get("target_row"),len(table.get("rows",[])));col=_index(rule.get("col"),len(table["rows"][row]))
        if _percentage(table,col,annotation):raise ValueError("百分比列不得参与金额竖加")
        operands=rule.get("operands",[])
        if not operands:raise ValueError("缺少参与明细")
        indices=[_index(x.get("row"),len(table["rows"])) for x in operands]
        if len(indices)!=len(set(indices)) or row in indices:raise ValueError("参与行重复或包含目标行")
        try:
            expected=Decimal(0);refs=[]
            for op,r in zip(operands,indices):
                if op.get("op","+") not in ("+","-"):raise ValueError("操作符无效")
                expected+=_amount(table,r,col)*(-1 if op.get("op")=="-" else 1)
                refs.append(_ref(table,r,col))
            actual=_amount(table,row,col)
            results.append(_computed(table,"竖加",table.get("name","")+"明细合计",expected,actual,refs,_ref(table,row,col),rule.get("tolerance","0.01")))
        except ValueError as exc:
            results.append(create_result("竖加","明细合计未执行",description=str(exc),source_file=table.get("source_file",""),source_location=f'表格ID {table.get("id")} 行{row}列{col}'))
    for rule in annotation.get("horizontal",[]):
        rows=rule.get("rows",[])
        if not isinstance(rows,list) or not rows:raise ValueError("横加必须显式声明行索引")
        if len(rows)!=len(set(rows)):raise ValueError("横加行重复")
        operands=rule.get("operands",[]);columns=[x.get("col") for x in operands];target=rule.get("result_col")
        if not columns or len(columns)!=len(set(columns)) or target in columns:raise ValueError("参与列重复或包含目标列")
        for row in rows:
            row=_index(row,len(table.get("rows",[])))
            for c in columns+[target]:
                _index(c,len(table["rows"][row]))
                if _percentage(table,c,annotation):raise ValueError("百分比列不得参与金额横加")
            if rule.get("kind")!="movement":
                periods=set()
                for c in columns+[target]:
                    header=str(table.get("headers",[])[c]) if c<len(table.get("headers",[])) else ""
                    if re.search("期末|年末|本期|本年",header):periods.add("current")
                    if re.search("期初|年初|上期|上年",header):periods.add("prior")
                    for info in annotation.get("columns",[]):
                        if info.get("col")==c and info.get("period"):periods.add(info["period"])
                if len(periods)>1:raise ValueError("不同期间或时点不能混算；变动关系须明确声明movement")
            try:
                expected=Decimal(0);refs=[]
                for op in operands:
                    if op.get("op","+") not in ("+","-"):raise ValueError("操作符无效")
                    expected+=_amount(table,row,op["col"])*(-1 if op.get("op")=="-" else 1)
                    refs.append(_ref(table,row,op["col"]))
                actual=_amount(table,row,target)
                results.append(_computed(table,"横加",table.get("name","")+"列间关系",expected,actual,refs,_ref(table,row,target),rule.get("tolerance","0.01")))
            except ValueError as exc:
                results.append(create_result("横加","列间关系未执行",description=str(exc),source_file=table.get("source_file",""),source_location=f'表格ID {table.get("id")} 行{row}列{target}'))
    return results

def code_vertical_check(table):
    if table.get("row_model")=="all_raw":
        return [create_result("竖加","原生表待标注",description="先声明表头行、金额列类型和期间，再验算",source_file=table.get("source_file",""),source_location=f'表格ID {table.get("id")}')]
    rows=table.get("rows",[])
    totals=[i for i,row in enumerate(rows) if row and re.search("合计|总计|小计",str(row[0]))]
    if not totals:return []
    if len(totals)>1 or any(row and str(row[0]).startswith("其中") for row in rows):
        return [create_result("竖加","复杂层级待标注",description="有多个小计或其中子项，需显式绑定参与行",source_file=table.get("source_file",""),source_location=f'表格ID {table.get("id")}')]
    target=totals[0];output=[]
    for col in range(1,len(rows[target])):
        if _percentage(table,col):continue
        detail=[]
        for i,row in enumerate(rows[:target]):
            if len(row)<=col or row[col] in (None,""):continue
            try:parse_number(row[col])
            except ValueError:continue
            detail.append({"row":i,"op":"-" if str(row[0]).startswith(("减：","减:")) else "+"})
        if detail:
            output.extend(execute_annotations(table,{"vertical":[{"target_row":target,"col":col,"operands":detail}]}))
    return output

def code_horizontal_check(table):
    headers=[str(h) for h in table.get("headers",[])]
    def find(words):
        cols=[i for i,h in enumerate(headers) if any(w in h for w in words)]
        return cols[0] if len(cols)==1 else None
    patterns=[
        ([find(["原价","原值"]),find(["累计折旧","累计摊销"]),find(["减值准备"])],find(["账面价值","净值"]),["+","-","-"]),
        ([find(["期初","年初"]),find(["增加"]),find(["减少"])],find(["期末","年末"]),["+","+","-"]),
        ([find(["账面余额"]),find(["坏账准备","减值准备"])],find(["账面价值","净值"]),["+","-"])
    ]
    for cols,target,ops in patterns:
        if target is not None and all(c is not None for c in cols):
            ann={"horizontal":[{"rows":list(range(len(table.get("rows",[])))),"operands":[{"col":c,"op":op} for c,op in zip(cols,ops)],"result_col":target,"kind":"movement" if ops==["+","+","-"] else "same_period"}]}
            return execute_annotations(table,ann)
    return []

def _source_amount(ref,tables,rule):
    table=tables.get(ref.get("table_id"),tables.get(str(ref.get("table_id"))))
    if table is None:raise ValueError("来源表不存在")
    for key,label in (("entity","主体"),("period","期间"),("currency","币种")):
        value=ref.get(key,table.get(key))
        if not value or value!=rule.get(key):raise ValueError(label+"缺失或不一致")
        if table.get(key) not in (None,"mixed",value):raise ValueError(label+"与来源表冲突")
    if ref.get("source_file") and ref["source_file"]!=table.get("source_file"):raise ValueError("源文件不一致")
    value=_cell(table,ref.get("row"),ref.get("col"))
    unit=ref.get("unit",table.get("unit"))
    if ref.get("kind") not in ("quantity","ratio") and table.get("unit") is not None and (unit not in UNITS or table["unit"] not in UNITS or UNITS[unit]!=UNITS[table["unit"]]):raise ValueError("引用金额单位与来源表冲突")
    if ref.get("kind")=="quantity":
        amount=parse_number(value)
    elif ref.get("kind")=="ratio":
        amount=parse_number(str(value).replace("%",""))/(100 if "%" in str(value) else 1)
    else:
        if unit not in UNITS or not unit:raise ValueError("金额单位不明确")
        amount=amount_in_unit(value,unit)
    return amount,{**_ref(table,ref["row"],ref["col"]),**ref,"raw_value":value,"normalized_value":amount,"unit":unit}

def execute_relation(rule,tables):
    values={};refs=[]
    for name,ref in rule.get("variables",{}).items():
        amount,source=_source_amount(ref,tables,rule);values[name]=amount;refs.append(source)
    actual,target=_source_amount(rule["target"],tables,rule)
    identities=[(r["source_file"],r["table_id"],r["row"],r["col"]) for r in refs]
    identity=(target["source_file"],target["table_id"],target["row"],target["col"])
    if len(set(identities))!=len(identities) or identity in identities:raise ValueError("来源重复或自己比较自己")
    expected=evaluate_expression(rule["formula"],values)
    result=_computed(tables.get(target["table_id"],tables.get(str(target["table_id"]))),rule.get("check_type","表注"),rule.get("rule_name",rule.get("name","显式关系验算")),expected,actual,refs,target,rule.get("tolerance","0.01"))
    result["check_id"]=rule.get("check_id") or stable_id(rule)
    result["entity"]=rule["entity"];result["period"]=rule["period"];result["currency"]=rule["currency"];result["formula"]=rule["formula"]
    return result

def _merge_located_values(items):
    out={}
    for item in items:
        for key,value in item.get("values",{}).items():
            if value in (None,""):continue
            if key in out and out[key]!=value:raise ValueError("附注值冲突："+key)
            out[key]=value
    return out

def _pick_value(values,keys):
    return next((values[k] for k in keys if k in values and values[k] not in (None,"")),None)

def _resolve_note_value(values,field,formula):
    expr=formula.split("=")[0].strip() if formula else ""
    if any(op in expr for op in "+-*/"):
        try:return evaluate_expression(expr,{k:parse_number(v) for k,v in values.items() if v not in (None,"")})
        except ValueError:return None
    return values.get(field)

def check_statement_to_note(statements,note_map,located_values,results):
    if note_map.get("schema_version")==2:
        for rule in note_map.get("checks",[]):
            try:results.append(execute_relation(rule,located_values.get("tables",{})))
            except ValueError as exc:results.append(create_result("表注",rule.get("name","表注未执行"),description=str(exc)))
        return
    for subject,info in note_map.items():
        if not isinstance(info,dict):continue
        candidates=[s.get(subject,{}).get(info.get("period","current")) for name,s in statements.items() if isinstance(s,dict) and (not info.get("statement") or info["statement"]==name) and subject in s]
        actual=None
        try:actual=_resolve_note_value(_merge_located_values(located_values.get(subject,[])),info.get("field",""),info.get("formula",""))
        except ValueError:pass
        if len(candidates)!=1 or actual is None:
            results.append(create_result("表注",subject+"表注勾稽",description="来源、主体或必要金额缺失，需当前agent明确定位"));continue
        check=check_equal(candidates[0],actual)
        results.append(create_result("表注",subject+"表注勾稽",passed=check["match"],expected=candidates[0],actual=actual,difference=check["diff"],description="旧取数格式仅作草稿，请补充单元格来源及终审"))

def check_note_internal_reconcile(note_map,located_values,results):
    for subject,info in note_map.items():
        if not isinstance(info,dict):continue
        try:
            values=_merge_located_values(located_values.get(subject,[]))
            fields=[_pick_value(values,keys) for keys in (["期初余额","年初余额"],["本期增加","本年增加"],["本期减少","本年减少"],["期末余额","年末余额"])]
            if all(v is None for v in fields):continue
            data=reconcile(*fields)
            results.append(create_result("附注内",subject+"变动表",passed=data["match"],expected=data.get("calculated_ending"),actual=data.get("actual_ending"),difference=data.get("diff"),description=data.get("error","计算完成，待原文复核")))
        except ValueError as exc:results.append(create_result("附注内",subject+"变动表",description=str(exc)))

def run_l1_checks(statements,results,extracted_tables_path=None):
    funcs={"资产负债表":check_balance_sheet,"利润表":check_income_statement,"现金流量表":check_cash_flow_statement,"权益变动表":check_equity_change_statement}
    for name,statement in statements.items():
        if name.startswith("_") or not isinstance(statement,dict):continue
        function=next((f for key,f in funcs.items() if key in name),None)
        if function is None:continue
        for item in function(statement):
            results.append(create_result("报表间",name+"-"+item.rule_name,passed=item.passed,expected=item.expected,actual=item.actual,difference=item.difference,description=item.description,source_location=name,context=item.rule_name,statement=name,source_refs=statement.get("_source_map",{}),entity=statement.get("_meta",{}).get("entity"),period="prior" if "上期" in item.rule_name else "current"))

def _marker(text,position):
    sources=list(re.finditer(r'<!-- SOURCE file="([^"]+)"([^>]*)-->',text[:position]))
    if not sources:return {}
    match=sources[-1];page=re.search(r"page=(\d+)",match.group(2))
    return {"source_file":match.group(1),"page":int(page.group(1)) if page else None}

def check_page_continuity(report_md,results,report_text=None):
    text=Path(report_md).read_text(encoding="utf-8-sig") if report_text is None else report_text;files={}
    for match in re.finditer(r'<!-- SOURCE file="([^"]+)"[^>]*page=(\d+)[^>]*-->',text):
        files.setdefault(match.group(1),set()).add(int(match.group(2)))
    for source,pages in files.items():
        missing=sorted(set(range(min(pages),max(pages)+1))-pages)
        results.append(create_result("格式","提取页面索引-"+source,passed=None,description="物理页索引供定位；印刷页码须当前agent回原页核查。索引缺口："+str(missing),source_file=source,context=str(sorted(pages))))

def check_unit_consistency(report_md,results,report_text=None):
    text=Path(report_md).read_text(encoding="utf-8-sig") if report_text is None else report_text
    units=[m.group(0) for m in re.finditer(r"单位\s*[:：]\s*(?:人民币)?\s*(?:百万元|万元|千元|元)",text)]
    results.append(create_result("格式","金额单位定位",passed=None,description="声明须绑定对应表格；不同表使用不同单位不当然错误" if units else "未提取到单位声明，不能记为通过",context="；".join(units)))

TYPO_WORDS={"先讲先出":"先进先出","其本":"基本","员债":"负债","所有都权益":"所有者权益","润表":"利润表","计报告":"审计报告","资负债表":"资产负债表","现金流理表":"现金流量表","财国报表":"财务报表","合计师事务所":"会计师事务所","特殊普通合饮":"特殊普通合伙","财务报麦":"财务报告","审诉报告":"审计报告"}

def check_typos(report_md,results,report_text=None):
    text=Path(report_md).read_text(encoding="utf-8-sig") if report_text is None else report_text
    for wrong,right in TYPO_WORDS.items():
        for match in re.finditer(re.escape(wrong),text):
            # 仅排除同一处完整正确词，不能屏蔽其他位置的错字。
            left=max(0,match.start()-len(right));right_edge=min(len(text),match.end()+len(right))
            nearby=text[left:right_edge]
            full=[m for m in re.finditer(re.escape(right),nearby) if left+m.start()<=match.start() and left+m.end()>=match.end()]
            if full:continue
            context=text[max(0,match.start()-30):match.end()+30]
            results.append(create_result("文本","疑似错别字-"+str(match.start()),passed=None,description=wrong+" → "+right+"；须当前agent回原文确认",context=context,source_location="字符"+str(match.start()),**_marker(text,match.start())))

def check_company_consistency(extracted_tables,report_md,results,report_text=None):
    text=Path(report_md).read_text(encoding="utf-8-sig") if report_text is None else report_text
    matches=list(re.finditer(r"编制单位\s*[:：]\s*([^\n|]+)",text))
    if not matches:
        results.append(create_result("格式","主体名称待定位",passed=None,description="未找到结构化编制单位；由当前agent识别抬头、报表主体和关联方，不按全文出现频率猜主体"))
    for match in matches:
        results.append(create_result("格式","编制单位-"+str(match.start()),passed=None,description="核对主体身份位置，正文关联方名称不应混入比较",context=match.group(0),source_location="字符"+str(match.start()),**_marker(text,match.start())))

def check_note_number_continuity(report_md,results,report_text=None):
    text=Path(report_md).read_text(encoding="utf-8-sig") if report_text is None else report_text
    headings=[m.group(0) for m in re.finditer(r"(?m)^\s*(?:附注[一二三四五六七八九十]+[、.]|[（(]\d+[）)]|\d+[、.])[^\n]{0,50}",text)]
    results.append(create_result("格式","附注编号待分组核查",passed=None,description="需区分章节、子项、续表及比较期，再判断编号连续和引用对应；未匹配不代表通过",context="\n".join(headings)))

def check_firm_consistency(report_md,results,report_text=None):
    text=Path(report_md).read_text(encoding="utf-8-sig") if report_text is None else report_text
    names=[m.group(0) for m in re.finditer(r"[^\s,，。；;\n|]{1,40}会计师事务所(?:[（(][^）)\n]{1,15}[）)])?",text)]
    results.append(create_result("格式","事务所及文号待核查",passed=None,description="核对正文、签字和盖章处的事务所名称及报告文号；其他报告引用须单独区分",context="；".join(names)))

def scan_tables(tables):
    return {"four_statements":[t for t in tables if t.get("role")=="statements"],"note_detail":[t for t in tables if t.get("role")!="statements" and t.get("rows")],"title":[t for t in tables if not t.get("rows")]}

def scan_candidates(tables):
    return [{"id":t.get("id"),"source_file":t.get("source_file"),"page":t.get("page"),"rows_count":len(t.get("rows",[])),"reason":"需当前agent明确结构及适用关系"} for t in tables]

def build_subjects_index(tables):
    result={}
    for t in tables:
        name=t.get("name") or t.get("chapter")
        if name:result.setdefault(name,[]).append({"table_id":t["id"],"source_file":t.get("source_file")})
    return result

def main(argv=None):
    parser=argparse.ArgumentParser(description="本地确定性草筛；语义复核由当前agent执行")
    parser.add_argument("input_dir");parser.add_argument("-o","--output",required=True)
    parser.add_argument("--statements");parser.add_argument("--note-map");parser.add_argument("--note-values")
    parser.add_argument("--annotations");parser.add_argument("--relations")
    parser.add_argument("--scope",choices=["quick","standard","deep"],default="standard")
    parser.add_argument("--types",nargs="+",choices=["勾稽","横加竖加","表注","文本","格式"])
    parser.add_argument("--scan",action="store_true")
    args=parser.parse_args(argv)
    directory=Path(args.input_dir).resolve();output=Path(args.output).resolve()
    if not directory.is_dir():parser.error("输入目录不存在")
    table_path=directory/"extracted_tables.json";report_path=directory/"report.md"
    if not table_path.exists() or not report_path.exists():parser.error("缺少原始提取文件")
    def input_path(value,default):
        if value:
            p=Path(value)
            if not p.is_absolute():p=directory/p
            if not p.is_file():raise ValueError("输入文件不存在："+str(p))
            return p.resolve()
        p=directory/default
        return p if p.is_file() else None
    data=load_json(table_path)
    if not isinstance(data,dict) or not isinstance(data.get("tables"),list):parser.error("原始表格格式无效")
    tables=data["tables"];by_id={t["id"]:t for t in tables}
    results=[];used=[table_path,report_path]
    selected=set(args.types or (["勾稽","格式"] if args.scope=="quick" else ["勾稽","格式","文本","横加竖加","表注"]))
    statements={}
    try:
        guard_outputs(directory,output)
        path=input_path(args.statements,"statements.json")
        if path:statements=load_json(path);used.append(path)
        if "勾稽" in selected:
            if statements:run_l1_checks(statements,results,table_path)
            else:results.append(create_result("报表间","四表未提取",description="需当前agent生成manifest并精确取数；附注-only应有明确不适用结论"))
        report_text=report_path.read_text(encoding="utf-8-sig") if selected.intersection(("格式","文本")) else None
        if "格式" in selected:
            check_page_continuity(report_path,results,report_text);check_unit_consistency(report_path,results,report_text)
            check_company_consistency(table_path,report_path,results,report_text);check_note_number_continuity(report_path,results,report_text);check_firm_consistency(report_path,results,report_text)
        if "文本" in selected:check_typos(report_path,results,report_text)
        if args.scan and "横加竖加" in selected:
            for table in tables:
                results.extend(code_vertical_check(table));results.extend(code_horizontal_check(table))
            guard_outputs(directory,output.parent/"candidates.json",output.parent/"subjects_index.json")
            save_json(output.parent/"candidates.json",scan_candidates(tables))
            save_json(output.parent/"subjects_index.json",build_subjects_index(tables))
        path=input_path(args.annotations,"annotations.json")
        if path:
            used.append(path);annotations=load_json(path)
            for record in annotations.get("tables",[]):
                if record.get("table_id") not in by_id:raise ValueError("标注指向不存在的来源表")
                results.extend(execute_annotations(by_id[record["table_id"]],record["annotation"]))
        path=input_path(args.relations,"relations.json")
        if path:
            used.append(path)
            for rule in load_json(path).get("checks",[]):results.append(execute_relation(rule,by_id))
        path=input_path(args.note_map,"note_map.json")
        if path and "表注" in selected:
            used.append(path);note_map=load_json(path)
            if note_map.get("schema_version")==2:check_statement_to_note(statements,note_map,{"tables":by_id},results)
            else:
                values_path=input_path(args.note_values,"located_values.json")
                if values_path:
                    used.append(values_path);located=load_json(values_path)
                    check_statement_to_note(statements,note_map,located,results);check_note_internal_reconcile(note_map,located,results)
                else:results.append(create_result("表注","旧取数格式待迁移",description="请当前agent提供v2来源引用，不能再调用外部模型取值"))
        elif "表注" in selected:results.append(create_result("表注","表注关系未提供",description="需当前agent确认主体、期间和附注净额口径"))
        for i,pending in enumerate(data.get("pending",[])):
            results.append(create_result("格式","提取待核实-"+str(i),description=pending.get("reason","资料未提取"),source_file=pending.get("source_file",""),page=pending.get("page")))
        protected={p.resolve() for p in used}
        protected.update(Path(f["path"]).resolve() for f in data.get("files",[]) if f.get("path"))
        if output in protected:raise ValueError("输出不能覆盖输入来源")
        payload={"meta":{"stage":"draft","scope":args.scope,"types":sorted(selected),"company":data.get("company",""),"period":data.get("period",""),"checked_at":datetime.now().isoformat(),"source":data.get("sources",[""])[0] if data.get("sources") else ""},"coverage":{"expected_ids":[r["check_id"] for r in results],"basis":"仅代码草筛对象；完整应检范围须由复核任务清单建立"},"results":results}
        save_json(output,payload)
        print("本地草筛已保存；所有项目仍需当前agent语义复核，不能据此宣布检查通过")
        return 0
    except (ValueError,TypeError,KeyError,OSError) as exc:
        parser.error(str(exc))

if __name__=="__main__":raise SystemExit(main())
