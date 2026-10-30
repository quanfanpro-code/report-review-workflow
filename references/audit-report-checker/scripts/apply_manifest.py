"""依据当前agent给出的结构契约取数；来源和冲突必须显式校验。"""
import argparse
from pathlib import Path
from 复核契约 import load_json,save_json,guard_outputs
from extractors.base import extract_linear,clean_name,canonical_name
from extractors.docx import load_extracted_tables,find_table_in_extracted
from extractors.xlsx import load_xlsx_sheets

def apply_aliases(data,aliases):
    result={}
    for key,value in data.items():
        name=aliases.get(key,key)
        if name in result and result[name]!=value:raise ValueError("别名映射冲突："+name)
        result[name]=value
    return result

def find_source_file(base_dir,source,source_root=None):
    candidates=[Path(source)] if Path(source).is_absolute() else [Path(base_dir)/source]
    if source_root:candidates.append(Path(source_root)/source)
    else:candidates.append(Path(base_dir).parent/source)
    existing={p.resolve() for p in candidates if p.is_file()}
    if len(existing)!=1:raise ValueError("源文件不存在或存在多个候选："+source)
    return next(iter(existing))

def apply_manifest(manifest_path):
    manifest_path=Path(manifest_path);mf=load_json(manifest_path);base=manifest_path.parent
    extracted=load_extracted_tables(manifest_path) if (base/"extracted_tables.json").exists() else {}
    statements={};jobs=[];books={}
    try:
        for name,cfg in mf.get("statements_map",{}).items():
            source=cfg.get("source")
            if not source:raise ValueError("报表缺少来源："+name)
            source_path=find_source_file(base,source,extracted.get("source_root"))
            file_cfg=mf.get("files",{}).get(source,{})
            loader=cfg.get("loader",file_cfg.get("loader"))
            if not loader:raise ValueError("缺少来源读取方式")
            frames=[]
            if loader in ("xlsx","xlsm"):
                if source_path not in books:books[source_path]=load_xlsx_sheets(source_path)
                refs=cfg.get("sheets",[]) if cfg.get("kind")!="matrix" else cfg.get("sheets_main",[])+cfg.get("sheets_prior",[])
                for sn in refs:
                    if sn not in books[source_path]:raise ValueError("工作表不存在："+str(sn))
                    frames.append({"id":sn,"sheet":sn,"source_file":source,"rows":[list(r) for r in books[source_path][sn].iter_rows(values_only=True)],"row_model":"all_raw"})
            elif loader in ("docx","pdf"):
                refs=cfg.get("sheets",[])
                if cfg.get("kind")=="matrix":refs=cfg.get("sheets_main",[])+cfg.get("sheets_prior",[])
                if not refs:
                    ref=cfg.get("source_table")
                    refs=ref if isinstance(ref,list) else [ref]
                for ref in refs:
                    t=find_table_in_extracted(extracted,{"source_file":source,"table_id":ref} if type(ref) is int else ref)
                    if t.get("source_file")!=source:raise ValueError("报表来源与契约不一致")
                    frames.append(t)
            else:raise ValueError("不支持的读取方式："+str(loader))
            if not frames:raise ValueError("没有明确的来源表")
            meta={k:cfg[k] for k in ("entity","currency","unit","zero_fields","fx_absent_confirmed","impairment_presentation") if k in cfg}
            meta["periods"]=cfg.get("periods",{})
            aliases=cfg.get("field_aliases",{})
            data={};positions={};raw=[]
            for frame in frames:
                rows=frame.get("rows",[])
                if frame.get("row_model")!="all_raw" and frame.get("headers"):rows=[frame["headers"]]+rows
                start=cfg.get("first_data_row",0);end=cfg.get("last_data_row",len(rows))
                if any(type(i) is not int for i in (start,end)) or not 0<=start<=end<=len(rows):raise ValueError("数据行索引越界")
                raw.extend(rows[start:end])
                if cfg.get("kind")=="matrix":continue
                part=extract_linear(rows[start:end],cfg["item_col"],cfg["current_col"],cfg["prior_col"])
                part=apply_aliases(part,aliases)
                for key,value in part.items():
                    if key in data and data[key]!=value:raise ValueError("续表取数冲突："+key)
                    data[key]=value
                for row_no,row in enumerate(rows[start:end],start):
                    if len(row)<=max(cfg["item_col"],cfg["current_col"],cfg["prior_col"]) or row[cfg["item_col"]] is None:continue
                    key=aliases.get(canonical_name(clean_name(row[cfg["item_col"]])),canonical_name(clean_name(row[cfg["item_col"]])))
                    if key not in data:continue
                    positions.setdefault(key,{})
                    for period,col in (("current",cfg["current_col"]),("prior",cfg["prior_col"])):
                        positions[key][period]={"source_file":source,"table_id":frame["id"],"sheet":frame.get("sheet"),"row":row_no,"col":col,"period":period,"raw_value":row[col],**{k:meta.get(k) for k in ("entity","currency","unit")}}
            if cfg.get("kind")=="matrix":
                # 全矩阵原文保留；具体期初、变动、期末及列角色由当前agent声明。
                data["_matrix_raw"]={str(f["id"]):f["rows"] for f in frames}
                if cfg.get("matrix"):
                    data["_matrix"]={}
                    for period,matrix in cfg["matrix"].items():
                        table=next((f for f in frames if f["id"]==matrix.get("table_id")),None)
                        if table is None:raise ValueError("矩阵声明指向未知来源")
                        data["_matrix"][period]={**matrix,"rows":table["rows"]}
            data["_meta"]=meta;data["_source_map"]=positions
            jobs.append((cfg.get("merge_into") or name,data))
        for name,data in jobs:
            if name not in statements:statements[name]=data;continue
            target=statements[name]
            if target["_meta"]!=data["_meta"]:raise ValueError("续表主体、期间或单位冲突")
            for key,value in data.items():
                if key=="_source_map":target[key].update(value)
                elif key=="_meta":continue
                elif key in target and target[key]!=value:raise ValueError("续表项目冲突："+key)
                else:target[key]=value
        return statements
    finally:
        for sheets in books.values():
            if sheets:next(iter(sheets.values())).parent.close()

def main(argv=None):
    parser=argparse.ArgumentParser(description="按当前agent的显式结构契约取数")
    parser.add_argument("manifest");parser.add_argument("-o","--output",default="statements.json")
    args=parser.parse_args(argv);path=Path(args.manifest).resolve()
    if path.is_dir():path=path/"manifest.json"
    output=Path(args.output).resolve()
    if output==path:parser.error("输出不能覆盖结构契约")
    try:
        guard_outputs(path.parent,output,allow_names=("statements.json",))
        mf=load_json(path)
        extracted=load_json(path.parent/"extracted_tables.json") if (path.parent/"extracted_tables.json").exists() else {}
        sources=set(mf.get("files",{}))|{cfg["source"] for cfg in mf.get("statements_map",{}).values() if cfg.get("source")}
        protected={find_source_file(path.parent,s,extracted.get("source_root")) for s in sources}
        protected.update((path.parent/"extracted_tables.json",path.parent/"report.md"))
        if output in {p.resolve() for p in protected}:raise ValueError("输出不能覆盖原始来源或提取输入")
        result=apply_manifest(path);save_json(output,result)
    except (ValueError,KeyError,OSError,TypeError) as exc:parser.error(str(exc))
    print("已按结构契约取数，尚需业务复核："+str(output))
    return 0

if __name__=="__main__":raise SystemExit(main())
