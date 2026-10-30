"""从经过来源及终审校验的结果导出七张工作表和Markdown。"""
import argparse
import math
import unicodedata
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Font,PatternFill,Alignment
from 复核契约 import load_json,validate_report,save_text,backup_existing,STATUSES,verify_sources,guard_outputs

SHEETS=["摘要","报表内勾稽","表注勾稽","附注内勾稽","横加竖加","文本格式","检查项"]
COLORS={"确认错误":"FFC7CE","待核实":"FFEB9C","未执行":"FFE6CC","通过":"C6E0B4"}

def load_results(path):
    data=load_json(path)
    verify_sources(data)
    data.setdefault("meta",{});data["meta"].setdefault("stage","draft")
    data.setdefault("results",[]);data.setdefault("coverage",{"expected_ids":[]})
    validate_report(data)
    return data

def field(item,name,default=""):
    value=item.get(name,default)
    return default if value is None else str(value)

def _category(item):
    return {"报表间":"报表内勾稽","报表内":"报表内勾稽","跨表":"报表内勾稽","表注":"表注勾稽","附注内":"附注内勾稽","横加":"横加竖加","竖加":"横加竖加","文本":"文本格式","格式":"文本格式"}.get(item.get("check_type"),"文本格式")

def _basis(item):
    return field(item.get("review",{}),"basis") or field(item,"description")

def _location(item):
    parts=[field(item,"source_file"),field(item,"chapter"),field(item,"source_location")]
    if item.get("table_id") is not None:parts.append("表格"+str(item["table_id"]))
    if item.get("page") is not None:parts.append("第"+str(item["page"])+"页")
    if item.get("row_range") is not None:parts.append("原始行范围（从0起、末端不含）"+str(item["row_range"]))
    elif item.get("source_span") is not None:parts.append("原文区间"+str(item["source_span"]))
    return "；".join(p for p in parts if p)

def _cell(ws,row,col,value,bold=False,status=None):
    cell=ws.cell(row,col,str(value) if value is not None else "")
    cell.data_type="s"
    cell.font=Font(name="微软雅黑",size=12,bold=bold,color="FFFFFF" if bold else "222222")
    cell.alignment=Alignment(vertical="top",wrap_text=True)
    if bold:cell.fill=PatternFill("solid",fgColor="4472C4")
    elif status in COLORS:cell.fill=PatternFill("solid",fgColor=COLORS[status])
    return cell

def _write_row(ws,row,values,bold=False,status=None):
    for col,value in enumerate(values,1):_cell(ws,row,col,value,bold,status)

def _protect(data,out_path,results_path=None):
    output=Path(out_path).resolve()
    if data.get("meta",{}).get("input_dir"):guard_outputs(data["meta"]["input_dir"],output)
    protected={Path(results_path).resolve()} if results_path is not None else set()
    protected.update(Path(f["path"]).resolve() for f in data.get("meta",{}).get("source_files",[]) if f.get("path"))
    for item in data.get("results",[]):
        if item.get("source_file"):protected.add(Path(item["source_file"]).resolve())
        for ref in item.get("source_refs",[]):
            if isinstance(ref,dict) and ref.get("source_file"):protected.add(Path(ref["source_file"]).resolve())
    if output in protected:raise ValueError("输出不能覆盖原始来源或结果输入")
    return output

def write_excel(data,results_path,out_path):
    verify_sources(data)
    counts=validate_report(data)
    out=_protect(data,out_path,results_path)
    wb=Workbook();wb.active.title=SHEETS[0]
    for name in SHEETS[1:]:wb.create_sheet(name)
    summary=wb["摘要"]
    _write_row(summary,1,[field(data.get("meta",{}),"company","审计报告")+"复核摘要","值"],True)
    status="完整复核记录" if data.get("meta",{}).get("stage")=="final" and counts["完整"] else "未完成：阶段草稿"
    lines=[("完成情况",status),("检查深度",field(data.get("meta",{}),"scope")),("应检对象",counts["应检"]),("已记录对象",counts["已记录"])]
    lines.extend((s,counts[s]) for s in STATUSES)
    lines.append(("计数口径","按应检对象统计；具体计算关系在明细及原始JSON留痕"))
    for i,(label,value) in enumerate(lines,2):_write_row(summary,i,[label,value])
    headings=["对象ID","状态","检查规则","位置","应为","实际","差额","复核依据","原文摘录","证据"]
    for name in SHEETS[1:]:_write_row(wb[name],1,headings,True)
    for item in data["results"]:
        evidence=str(Path(results_path).resolve())+"；对象ID："+item["check_id"]
        values=[item["check_id"],item["status"],field(item,"rule_name"),_location(item),field(item,"expected"),field(item,"actual"),field(item,"difference"),_basis(item),field(item,"context"),evidence]
        sheet=wb["检查项"];row=sheet.max_row+1;_write_row(sheet,row,values,status=item["status"])
        source=item.get("source_file")
        if source and Path(source).is_absolute():
            sheet.cell(row,4).hyperlink=Path(source).as_uri()+(("#page="+str(item["page"])) if item.get("page") and Path(source).suffix.lower()==".pdf" else "")
        if item["status"] in ("确认错误","待核实","未执行"):
            sheet=wb[_category(item)]
            _write_row(sheet,sheet.max_row+1,values,status=item["status"])
            for calculation in item.get("calculations",[]):
                if calculation.get("calculation",{}).get("match") is False:
                    detail=wb[_category(calculation)]
                    _write_row(detail,detail.max_row+1,[item["check_id"],"数值差异",field(calculation,"rule_name"),_location(calculation),field(calculation,"expected"),field(calculation,"actual"),field(calculation,"difference"),"该关系须结合本对象终审结论理解","",evidence])
    for sheet in wb:
        sheet.freeze_panes="A2";sheet.auto_filter.ref=sheet.dimensions
        for col,width in zip("ABCDEFGHIJ",[28,15,30,50,20,20,18,65,55,60]):sheet.column_dimensions[col].width=width
        for row in range(2,sheet.max_row+1):
            lines=1
            for cell in sheet[row]:
                width=max(1,sheet.column_dimensions[cell.column_letter].width-2)
                wrapped=sum(max(1,math.ceil(sum(2 if unicodedata.east_asian_width(ch) in "WF" else 1 for ch in line)*1.2/width)) for line in str(cell.value or "").split("\n"))
                lines=max(lines,wrapped)
            sheet.row_dimensions[row].height=min(409,max(30,lines*18+8))
    out.parent.mkdir(parents=True,exist_ok=True)
    if out.exists():backup_existing(out)
    wb.save(out);wb.close()

def write_markdown(data,out_path):
    verify_sources(data)
    counts=validate_report(data);out=_protect(data,out_path)
    final=data.get("meta",{}).get("stage")=="final" and counts["完整"]
    lines=["# "+field(data.get("meta",{}),"company","审计报告")+"复核记录","",
           "完成情况："+("已完成所选范围内的复核记录" if final else "未完成：以下为阶段草稿，不能代表完整检查结论"),"",
           "应检对象："+str(counts["应检"])+"；已记录对象："+str(counts["已记录"])]
    lines.extend(s+"："+str(counts[s]) for s in STATUSES)
    lines.extend(["","以上按应检对象计数，具体算式及原始引用保留在结果JSON。",""])
    if final and counts["通过"]>0 and not any(counts[s] for s in ("确认错误","待核实","未执行")):lines.append("所选范围检查通过；不适用事项另列，不计入通过。")
    for status in ("确认错误","待核实","未执行","不适用","已排除误报"):
        items=[x for x in data["results"] if x["status"]==status]
        if not items:continue
        lines.extend(["","## "+status,""])
        for item in items:
            lines.extend(["### "+field(item,"rule_name",item["check_id"]),_location(item),_basis(item),"对象ID："+item["check_id"]])
            if item.get("expected") is not None:lines.append("应为："+str(item["expected"])+"；实际："+str(item.get("actual"))+"；差额："+str(item.get("difference")))
            for c in item.get("calculations",[]):
                lines.append("计算关系："+field(c,"rule_name")+"；应为："+field(c,"expected")+"；实际："+field(c,"actual")+"；差额："+field(c,"difference"))
            lines.append("")
    save_text(out,"\n".join(lines)+"\n")

def derive_output_paths(results_path,meta,output_arg):
    stem=Path(str(meta.get("source") or "审计报告")).stem
    for ch in '/\\:*?"<>|':stem=stem.replace(ch,"_")
    if output_arg and Path(output_arg).suffix.lower()==".xlsx":
        p=Path(output_arg).resolve();return p,p.with_name(p.stem+"_复核报告.md")
    directory=Path(output_arg).resolve() if output_arg else Path(results_path).parent
    return directory/(stem+"_检查报告.xlsx"),directory/(stem+"_复核报告.md")

def main(argv=None):
    parser=argparse.ArgumentParser(description="导出7张工作表及Markdown，终审不足只能输出草稿")
    parser.add_argument("results");parser.add_argument("-o","--output")
    args=parser.parse_args(argv)
    try:
        path=Path(args.results).resolve();data=load_results(path)
        excel,markdown=derive_output_paths(path,data["meta"],args.output)
        write_excel(data,path,excel);write_markdown(data,markdown)
        print("已导出："+str(excel)+"；"+str(markdown));return 0
    except (ValueError,KeyError,TypeError,OSError) as exc:parser.error(str(exc))

if __name__=="__main__":raise SystemExit(main())
