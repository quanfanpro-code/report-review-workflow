"""按来源及表ID定位；歧义必须显式解决。"""
from pathlib import Path
from 复核契约 import load_json

def load_extracted_tables(manifest_path):
    p=Path(manifest_path).parent/"extracted_tables.json"
    if not p.is_file():raise ValueError("找不到extracted_tables.json")
    return load_json(p)

def find_table_in_extracted(data,ref):
    tables=data.get("tables",[]) if isinstance(data,dict) else data
    if isinstance(ref,dict):
        matches=[t for t in tables if t.get("id")==ref.get("table_id") and (not ref.get("source_file") or t.get("source_file")==ref["source_file"])]
    elif type(ref) is int:matches=[t for t in tables if t.get("id")==ref]
    elif isinstance(ref,str) and ref:matches=[t for t in tables if t.get("name")==ref]
    else:matches=[]
    if len(matches)!=1:raise ValueError("来源定位缺失或存在歧义，请指定来源和表ID："+str(ref))
    return matches[0]

def iter_docx_rows(data,refs):
    for ref in refs:
        t=find_table_in_extracted(data,ref)
        if t.get("row_model")!="all_raw" and t.get("headers"):yield list(t["headers"])
        yield from t.get("rows",[])
