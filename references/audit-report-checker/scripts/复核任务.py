"""当前agent的本地资料队列；本工具不调用任何模型。"""
import argparse
import json
from pathlib import Path
from 复核契约 import load_json,save_json,fingerprint,stable_id,normalize_result,validate_report,STATUSES,guard_outputs
from run_check import execute_annotations,execute_relation

STATE="复核进度.json"
POLICY_VERSION=3
LIMITS={"128k":20000,"1m":80000,"unknown":20000}

def _inputs(directory):
    names=("extracted_tables.json","report.md","manifest.json","statements.json","note_map.json","relations.json")
    values={name:fingerprint(directory/name) for name in names if (directory/name).is_file()}
    root=Path(__file__).resolve().parents[1]
    values["policy_version"]=POLICY_VERSION
    for folder,pattern in ((root/"scripts","*.py"),(root/"references","*.md")):
        for path in sorted(folder.rglob(pattern)):
            values["rule:"+str(path.relative_to(root))]=fingerprint(path)
    values["rule:SKILL.md"]=fingerprint(root/"SKILL.md")
    if "extracted_tables.json" not in values or "report.md" not in values:raise ValueError("缺少原始提取文件")
    data=load_json(directory/"extracted_tables.json")
    for file in data.get("files",[]):
        path=Path(file["path"])
        if not path.is_file() or fingerprint(path)!=file["sha256"]:raise ValueError("原始来源变化，旧结论已失效")
        values["source:"+file["name"]]=file["sha256"]
    return stable_id(values)

def _load(directory):
    directory=Path(directory)
    state=load_json(directory/STATE)
    if state["source_fingerprint"]!=_inputs(directory):raise ValueError("来源变化，旧批次及结论已失效，请重新初始化")
    return state

def _parts(text,size=5500):
    start=0
    while start<len(text):
        end=min(start+size,len(text))
        if end<len(text):
            boundary=text.rfind("\n",start+size//2,end)
            if boundary>start:end=boundary+1
        yield start,end,text[start:end]
        if end==len(text):break
        start=max(start+1,end-64)

def _tables(directory,data,plan):
    tables={t["id"]:dict(t) for t in data.get("tables",[])}
    declarations=[]
    if (directory/"manifest.json").exists():
        for cfg in load_json(directory/"manifest.json").get("statements_map",{}).values():
            ids=cfg.get("source_table",[]);ids=ids if isinstance(ids,list) else [ids]
            sheets=cfg.get("sheets",[])+cfg.get("sheets_main",[])+cfg.get("sheets_prior",[])
            for table in tables.values():
                if table.get("source_file")==cfg.get("source") and (table["id"] in ids or table.get("sheet") in sheets):declarations.append((table,cfg))
    for rule in (plan or {}).get("checks",[]):
        for ref in [*rule.get("variables",{}).values(),rule.get("target",{})]:
            if ref.get("table_id") in tables:declarations.append((tables[ref["table_id"]],ref))
    for table,decl in declarations:
        for key in ("entity","currency","unit"):
            value=decl.get(key)
            if value is None:continue
            if table.get(key) not in (None,value):raise ValueError("已声明来源口径冲突："+key)
            table[key]=value
        if decl.get("periods"):table["periods"]=decl["periods"]
    return tables

def init_review(input_dir,context_window,scope,check_types=None):
    directory=Path(input_dir).resolve()
    if context_window not in LIMITS:raise ValueError("上下文档位应为128k、1m或unknown")
    if scope not in ("quick","standard","deep"):raise ValueError("检查深度无效")
    token=_inputs(directory);state_path=directory/STATE
    if state_path.exists():
        previous=load_json(state_path)
        if previous.get("source_fingerprint")==token and previous.get("scope")==scope and previous.get("check_types")==check_types:
            previous["context_window"]=context_window
            old_attempted=list(previous.get("attempted_ids",[]))
            previous["attempted_ids"]=[cid for cid in previous.get("attempted_ids",[]) if previous.get("results",{}).get(cid,{}).get("status")!="未执行"]
            if old_attempted!=previous["attempted_ids"]:previous["attempt"]=previous.get("attempt",0)+1
            save_json(state_path,previous)
            return previous
    data=load_json(directory/"extracted_tables.json");objects=[]
    plan=load_json(directory/"relations.json") if (directory/"relations.json").exists() else None
    def add(kind,text,**meta):
        for start,end,part in _parts(text):
            identity={"kind":kind,"span":[start,end],**meta}
            cid=stable_id(identity)
            material=json.dumps(identity,ensure_ascii=False)+"\n"+part
            objects.append({"check_id":cid,"kind":kind,"span":[start,end],"material":material,**meta})
    inventory={"来源文件":data.get("sources",[]),"表格数":len(data.get("tables",[])),"深度":scope,"类别":check_types or "按深度档执行"}
    add("structure",json.dumps(inventory,ensure_ascii=False)+"\n请识别单体/合并/附注-only，确认主体、期间、币种单位、报表范围及检查适用性；不得按出现顺序猜主体。")
    for table in _tables(directory,data,plan).values():
        rows=table.get("rows",[]);start=0
        context={k:table.get(k) for k in ("source_file","chapter","page","entity","period","periods","currency","unit")}
        context.update(kind="table",table_id=table["id"],headers=table.get("headers",[]),source_top=rows[:2])
        while start<len(rows) or not rows and start==0:
            end=start;part=[]
            while end<len(rows):
                candidate=json.dumps({**context,"row_range":[start,end+1],"rows":part+[rows[end]]},ensure_ascii=False,indent=1)
                if len(candidate)>5300:
                    if not part:raise ValueError("单行或表头背景超过材料预算，需先分解该单元格并保留来源")
                    break
                part.append(rows[end]);end+=1
            material=json.dumps({**context,"row_range":[start,end],"rows":part},ensure_ascii=False,indent=1)
            identity={"kind":"table","table_id":table["id"],"source_file":table.get("source_file",""),"row_range":[start,end]}
            objects.append({**identity,"check_id":stable_id(identity),"span":[start,end],"span_unit":"row","material":material})
            if not rows:break
            start=end
    segments=data.get("segments")
    if segments is None:segments=[{"id":0,"source_file":"report.md","text":(directory/"report.md").read_text(encoding="utf-8-sig")}]
    for segment in segments:
        if "table_id" in segment:continue
        text=segment.get("text","")
        if text:add("text",text,segment_id=segment.get("id"),source_file=segment.get("source_file",""),page=segment.get("page"),part=segment.get("part",""))
    for i,pending in enumerate(data.get("pending",[])):
        add("extraction",json.dumps(pending,ensure_ascii=False),pending_id=i,source_file=pending.get("source_file",""))
    add("cross_relations","跨批核对：同主体同期间的四表、表注、权益矩阵、现金构成、比较期和适用披露。请显式提供来源关系；不适用须写依据，缺数据保留未执行。")
    if not objects:raise ValueError("没有应检资料")
    plan=load_json(directory/"relations.json") if (directory/"relations.json").exists() else None
    if plan is not None:
        checks=plan.get("checks",[]);ids=[r.get("check_id") for r in checks]
        if any(not cid for cid in ids) or len(ids)!=len(set(ids)):raise ValueError("应检关系须有唯一check_id")
    state={"version":3,"source_fingerprint":token,"context_window":context_window,"scope":scope,"check_types":check_types,"relation_plan":plan,"coverage":{"expected_ids":[o["check_id"] for o in objects]},"objects":objects,"results":{},"attempted_ids":[],"batches":{},"attempt":0}
    save_json(state_path,state)
    return state

def next_batch(input_dir,max_chars=None):
    state=_load(input_dir)
    limit=LIMITS[state["context_window"]] if max_chars is None else max_chars
    if type(limit) is not int or not 6000<=limit<=LIMITS[state["context_window"]]:raise ValueError("批次材料上限无效")
    selected=[];parts=[];size=0
    for obj in state["objects"]:
        cid=obj["check_id"]
        if cid in state.get("attempted_ids",[]):continue
        material="\n\nCHECK_ID="+cid+"\n"+obj["material"]
        if len(material)>limit:raise ValueError("单个结构片段超过材料上限，需要进一步拆分")
        if size+len(material)>limit:break
        selected.append(cid);parts.append(material);size+=len(material)
    return {"batch_id":stable_id({"source":state["source_fingerprint"],"ids":selected,"attempt":state.get("attempt",0)}),"source_fingerprint":state["source_fingerprint"],"check_ids":selected,"material":"".join(parts),"remaining":len(state["coverage"]["expected_ids"])-len(state.get("attempted_ids",[]))}

def submit_batch(input_dir,batch_result):
    directory=Path(input_dir);state=_load(directory)
    if batch_result.get("source_fingerprint")!=state["source_fingerprint"]:raise ValueError("批次来源变化或不匹配")
    digest=stable_id(batch_result);batch_id=batch_result.get("batch_id")
    if batch_id in state["batches"]:
        if state["batches"][batch_id]!=digest:raise ValueError("同批次提交内容冲突")
        return state
    batch=next_batch(directory)
    answers=batch_result.get("results",[])
    if batch_id!=batch["batch_id"] or sorted(r.get("check_id","") for r in answers)!=sorted(batch["check_ids"]) or not answers:raise ValueError("回填范围必须与当前批次完整对应")
    objects={o["check_id"]:o for o in state["objects"]}
    data=load_json(directory/"extracted_tables.json");tables=_tables(directory,data,state.get("relation_plan"))
    changed={}
    for answer in answers:
        item=dict(answer);cid=item["check_id"];obj=objects[cid];status=item.get("status")
        if status not in STATUSES:raise ValueError("结论状态无效")
        review=item.get("review",{})
        refs=review.get("source_refs",[])
        if status!="未执行":
            if not review.get("agent") or not review.get("basis") or review.get("source_fingerprint")!=state["source_fingerprint"] or review.get("check_id")!=cid or review.get("conclusion")!=status:raise ValueError("缺少当前agent的有效终审记录")
            if not refs:raise ValueError("缺少原文引用")
            for ref in refs:
                quote=ref.get("quote","")
                if not quote or quote not in obj["material"] or ref.get("check_id",cid)!=cid:raise ValueError("终审引文不在对应原文片段内")
        calculations=[]
        if obj["kind"]=="cross_relations" and status!="未执行":
            plan=state.get("relation_plan")
            if plan is None:raise ValueError("缺少已声明的应检关系清单，跨表检查只能保留未执行")
            expected=plan.get("checks",[])
            if item.get("use_declared_relations"):item["relations"]=expected
            actual=item.get("relations",[])
            if expected:
                if status in ("不适用","已排除误报") or {r.get("check_id"):r for r in actual}!={r["check_id"]:r for r in expected} or len(actual)!=len(expected):raise ValueError("回填必须完整对应应检关系清单，不能省略或改写")
            elif status!="不适用" or not plan.get("not_applicable_basis") or actual:raise ValueError("无适用跨表关系须在清单声明依据并标不适用")
        if item.get("annotation"):
            if obj["kind"]!="table":raise ValueError("结构标注必须对应表格范围")
            table=dict(tables[obj["table_id"]])
            for k,v in item.get("table_meta",{}).items():
                if k not in ("entity","period","currency","unit","dash_is_zero"):raise ValueError("不支持的表格口径字段")
                if table.get(k) is not None and table[k]!=v:raise ValueError("表格口径冲突")
                table[k]=v
            calculations=execute_annotations(table,item["annotation"])
        for relation in item.get("relations",[]):calculations.append(execute_relation(relation,tables))
        matches=[c.get("calculation",{}).get("match") for c in calculations]
        if status=="通过":
            if any(x is not True for x in matches):raise ValueError("计算不平或未执行，不能标通过")
            if obj["kind"]=="table" and not calculations:raise ValueError("表格通过须提供结构验算或记录不适用的依据")
            if obj["kind"]=="structure" and not item.get("structure"):raise ValueError("结构范围尚未声明")
            if obj["kind"]=="cross_relations" and not calculations:raise ValueError("跨表范围尚未验算；不适用必须明确说明")
            if obj["kind"]=="extraction":raise ValueError("提取缺口须先补充原始资料并重新建立清单，不能直接标通过")
        item["calculations"]=calculations
        item["calculation"]={"match":all(matches) if matches else None}
        item.setdefault("check_type",{"table":"横加","cross_relations":"报表间","text":"文本","structure":"格式","extraction":"格式"}[obj["kind"]])
        item.setdefault("rule_name",obj["kind"]+"-"+cid[:8]);item["source_file"]=obj.get("source_file","")
        source_paths={f["name"]:f["path"] for f in data.get("files",[]) if f.get("name") and f.get("path")}
        item["source_file"]=source_paths.get(item["source_file"],item["source_file"])
        if obj.get("table_id") is not None:
            table=tables[obj["table_id"]]
            item.update(table_id=obj["table_id"],chapter=table.get("chapter",""),page=table.get("page"))
        item["context"]="；".join(ref.get("quote","") for ref in refs)
        item["source_span"]=obj["span"];item["source_fingerprint"]=state["source_fingerprint"]
        if obj.get("row_range") is not None:item["row_range"]=obj["row_range"]
        changed[cid]=normalize_result(item)
    state["results"].update(changed);state["attempted_ids"].extend(changed);state["batches"][batch_id]=digest
    save_json(directory/STATE,state)
    return state

def audit_coverage(input_dir):
    state=_load(input_dir)
    data={"meta":{"stage":"draft"},"coverage":state["coverage"],"results":list(state["results"].values())}
    return validate_report(data)

def finalize_results(input_dir,output,draft=False):
    directory=Path(input_dir);state=_load(directory)
    output=Path(output).resolve()
    guard_outputs(directory,output)
    protected={directory/STATE,directory/"extracted_tables.json",directory/"report.md",directory/"manifest.json",directory/"statements.json"}
    if output in {p.resolve() for p in protected}:raise ValueError("输出不能覆盖输入或进度")
    items=[]
    for obj in state["objects"]:
        cid=obj["check_id"]
        items.append(state["results"].get(cid,{"check_id":cid,"status":"未执行","rule_name":obj["kind"]+"待处理","check_type":"格式","source_file":obj.get("source_file","")}))
    original=load_json(directory/"extracted_tables.json")
    if output in {Path(f["path"]).resolve() for f in original.get("files",[]) if f.get("path")}:raise ValueError("输出不能覆盖原始来源")
    data={"meta":{"stage":"draft" if draft else "final","scope":state["scope"],"context_window":state["context_window"],"source":original.get("sources",[""])[0] if original.get("sources") else "","company":original.get("company",""),"period":original.get("period","")},"coverage":state["coverage"],"results":items,"source_fingerprint":state["source_fingerprint"]}
    data["summary"]=validate_report(data)
    data["meta"]["source_files"]=original.get("files",[])
    data["meta"]["input_dir"]=str(directory.resolve())
    save_json(output,data)
    return data

def main(argv=None):
    parser=argparse.ArgumentParser(description="当前agent本地复核任务，不调用模型")
    sub=parser.add_subparsers(dest="command",required=True)
    for name in ("初始化","下一批","回填","覆盖","汇总"):
        p=sub.add_parser(name);p.add_argument("input_dir")
        if name=="初始化":
            p.add_argument("--context-window",choices=list(LIMITS),required=True);p.add_argument("--scope",choices=["quick","standard","deep"],default="standard");p.add_argument("--types",nargs="+")
        if name=="回填":p.add_argument("result_file")
        if name=="汇总":p.add_argument("-o","--output",required=True);p.add_argument("--draft",action="store_true")
        if name=="下一批":p.add_argument("-o","--output")
    args=parser.parse_args(argv)
    try:
        if args.command=="初始化":
            state=init_review(args.input_dir,args.context_window,args.scope,args.types);result={"应检对象":len(state["objects"]),"source_fingerprint":state["source_fingerprint"]}
        elif args.command=="下一批":
            result=next_batch(args.input_dir)
            if args.output:
                guard_outputs(args.input_dir,args.output);save_json(args.output,result)
                result={"batch_id":result["batch_id"],"文件":str(Path(args.output).resolve()),"对象数":len(result["check_ids"])}
        elif args.command=="回填":submit_batch(args.input_dir,load_json(args.result_file));result=audit_coverage(args.input_dir)
        elif args.command=="覆盖":result=audit_coverage(args.input_dir)
        else:result=finalize_results(args.input_dir,args.output,args.draft)["summary"]
        print(json.dumps(result,ensure_ascii=False,default=str));return 0
    except (ValueError,KeyError,TypeError,OSError) as exc:parser.error(str(exc))

if __name__=="__main__":raise SystemExit(main())
