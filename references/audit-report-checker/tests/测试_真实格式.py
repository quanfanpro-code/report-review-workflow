import pytest
from pathlib import Path
import parse_report,apply_manifest
from 复核契约 import save_json,fingerprint

@pytest.mark.parametrize("kind",["xlsx","pdf"])
def test_真实文件解析至契约取数不改变原件(验证目录,kind):
    source=验证目录/("原件."+kind)
    rows=[["Item","Current","Prior"],["Cash","100.25","90.12"]]
    if kind=="xlsx":
        from openpyxl import Workbook
        wb=Workbook();ws=wb.active;ws.title="Balance"
        for row in rows:ws.append(row)
        wb.save(source);wb.close()
    else:
        from reportlab.platypus import SimpleDocTemplate,Table,TableStyle
        from reportlab.lib import colors
        table=Table(rows,colWidths=[150]*3)
        table.setStyle(TableStyle([("GRID",(0,0),(-1,-1),1,colors.black)]))
        SimpleDocTemplate(str(source)).build([table])
    sha=fingerprint(source);out=验证目录/"提取"
    assert parse_report.main([str(source),"-o",str(out)])==0
    cfg={"source":source.name,"loader":kind,"first_data_row":1,"item_col":0,"current_col":1,"prior_col":2,"entity":"单体","currency":"CNY","unit":"元","field_aliases":{"Cash":"货币资金"}}
    cfg.update({"sheets":["Balance"]} if kind=="xlsx" else {"source_table":0})
    save_json(out/"manifest.json",{"files":{source.name:{"loader":kind}},"statements_map":{"资产负债表":cfg}})
    data=apply_manifest.apply_manifest(out/"manifest.json")
    assert data["资产负债表"]["货币资金"]=={"current":"100.25","prior":"90.12"}
    assert fingerprint(source)==sha
