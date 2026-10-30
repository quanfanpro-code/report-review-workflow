"""按显式列读取原始行，不猜期间和金额口径。"""
import re

def clean_name(value):
    s=re.sub(r"\s+","",str(value))
    s=re.sub(r"^(?:[一二三四五六七八九十]+[、.．]|[（(][一二三四五六七八九十\d]+[)）]|\d+[、.．])","",s)
    return s.strip()

def canonical_name(name):
    return {"股东权益合计":"所有者权益合计","负债和所有者权益合计":"负债和所有者权益总计","负债和股东权益总计":"负债和所有者权益总计","年初现金及现金等价物余额":"期初现金及现金等价物余额","年末现金及现金等价物余额":"期末现金及现金等价物余额"}.get(name,name)

def fmt(value):
    if value is None or isinstance(value,bool):return None
    return str(value).strip() or None

def extract_linear(rows,item_col,current_col,prior_col):
    if any(type(c) is not int or c<0 for c in (item_col,current_col,prior_col)) or len({item_col,current_col,prior_col})<3:raise ValueError("列索引无效或重复")
    result={}
    for cells in rows:
        if not cells or len(cells)<=max(item_col,current_col,prior_col):continue
        raw=cells[item_col]
        if raw is None:continue
        name=canonical_name(clean_name(raw))
        if not name or name in ("项目","项次","行次") or str(raw).strip().startswith("其中"):continue
        values={"current":fmt(cells[current_col]),"prior":fmt(cells[prior_col])}
        if name in result and result[name]!=values:raise ValueError("同名项目取数冲突："+name)
        result[name]=values
    return result

