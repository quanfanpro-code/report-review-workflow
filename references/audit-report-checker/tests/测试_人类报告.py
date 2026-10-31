from openpyxl import Workbook, load_workbook

import export_report as export
from 复核契约 import save_json


def issue(cid, status, basis, **extra):
    item = {
        "check_id": cid,
        "status": status,
        "rule_name": "table-" + cid,
        "check_type": "表注",
        "source_file": "D:/项目/03报出报表.xlsx",
        "table_id": 17,
        "row_range": [0, 8],
        "context": "科控集团3,500,000.00；科控酒店593,600.00",
        "expected": "4093600.00",
        "actual": "4060000.00",
        "difference": "33600.00",
        "calculation": {"match": status != "通过"},
        "review": {
            "agent": "当前agent",
            "check_id": cid,
            "source_fingerprint": "internal-fingerprint",
            "conclusion": status,
            "basis": basis,
            "source_refs": [{"quote": "科控酒店593,600.00"}],
        },
    }
    item.update(extra)
    return item


def visible_text(wb):
    return "\n".join(
        str(cell.value or "")
        for ws in wb.worksheets if ws.sheet_state == "visible"
        for row in ws.iter_rows() for cell in row
    )


MACHINE = ("error1", "pending1", "internal-fingerprint", "D:/项目/", "results.json", "table-error1",
           "row_range", "表格ID", "对象ID", "现补表", "CFS", "r5代码", "r6代码", "表8", "表17", "表50",
           "表54", "表60", "unaud", "supp-", "rpart-", "11449812.430000007", "430000007", " | ")


def test_七栏目齐全且机器信息默认隐藏(验证目录):
    items = [
        issue("error1", "确认错误", "关联方应收明细比合计多33,600.00元，确认错误。", issue_title="关联方明细加总比附注合计多3.36万元", fix_suggestion="核实这两家关联方的应收账款余额，改到明细与合计一致；修改后重新复核本项。"),
        issue("pending1", "待核实", "封面编号仍为占位符，请项目组核实后替换为正式编号，完成后本项核销。"),
        issue("false1", "已排除误报", "差异系同笔重分类，已排除误报。"),
    ]
    data = {"meta": {"stage": "final", "company": "甲公司"}, "coverage": {"expected_ids": [x["check_id"] for x in items]}, "results": items}
    path = 验证目录 / "复核.xlsx"
    export.write_excel(data, 验证目录 / "results.json", path)
    wb = load_workbook(path, data_only=False)

    assert wb.sheetnames == ["问题概览", "问题明细", "技术留痕"]
    assert wb["技术留痕"].sheet_state == "hidden"
    text = visible_text(wb)
    for required in ("致命", "重要", "细节", "关联方明细加总比附注合计多3.36万元", "问题", "严重程度", "错在哪",
                     "核对了什么", "差多少", "凭什么说错", "怎么改", "03报出报表.xlsx", "409.36 万元", "406.00 万元", "3.36 万元"):
        assert required in text
    for machine in MACHINE:
        assert machine not in text
    assert wb["技术留痕"]["A2"].value == "error1"
    wb.close()


def test_标题是结论句且碎尾不出现(验证目录):
    item = issue("error1", "确认错误", "补充资料空白，确认错误。")
    item["calculations"] = [
        {"rule_name": "现金流量表补充资料经营净额本期=现金流量表主表本期(预期不符:补充资料为0,见复核)",
         "expected": "11449812.430000007", "actual": "0", "difference": "11449812.430000007",
         "target": {"table_id": 8, "row": 22, "col": 1}, "calculation": {"match": False}},
    ]
    data = {"meta": {"stage": "final"}, "coverage": {"expected_ids": ["error1"]}, "results": [item]}
    path = 验证目录 / "复核.xlsx"
    export.write_excel(data, 验证目录 / "结果.json", path)
    text = visible_text(load_workbook(path))
    assert "1,144.98 万元" in text
    assert "430000007" not in text
    assert "不一致，差 1,144.98 万元" in text


def test_黑话与底稿语言清零(验证目录):
    item = issue("error1", "确认错误",
                 "unaud-cfs-op-cur/supp-op-net-cur属重分类；表60现流调整r5代码34吸收投资收到的现金贷方24,800,000，系表8现补表空白，确认错误。",
                 issue_title="补充资料未填列导致与主表差1,144.98万元")
    item["calculations"] = [
        {"rule_name": "现补表经营净额本期=CFS主表本期(预期不符:现补表为0,见复核)", "expected": "11449812.43", "actual": "0",
         "difference": "11449812.43", "target": {"table_id": 8, "row": 22, "col": 1}, "calculation": {"match": False}},
    ]
    data = {"meta": {"stage": "final"}, "coverage": {"expected_ids": ["error1"]}, "results": [item]}
    path = 验证目录 / "复核.xlsx"
    export.write_excel(data, 验证目录 / "结果.json", path)
    wb = load_workbook(path)
    text = visible_text(wb)
    assert "现金流量表补充资料" in text and "现金流量表主表" in text
    for residue in ("unaud", "supp-", "现补表", "CFS", "表60", "r5代码", "表8", "见复核", "见终审", "预期不符"):
        assert residue not in text
    md = 验证目录 / "复核.md"
    export.write_markdown(data, md)
    md_text = md.read_text(encoding="utf-8-sig")
    for residue in ("unaud", "supp-", "现补表", "CFS", "表60", "r5代码"):
        assert residue not in md_text
    wb.close()


def test_隐藏工作表来源转提醒且不进问题清单(验证目录):
    folder = 验证目录 / "输入"
    folder.mkdir()
    wb = Workbook()
    visible = wb.active
    visible.title = "现金流量表主表"
    visible.append(["项目", "本期金额"])
    visible.append(["经营活动现金流量净额", "11449812.43"])
    hidden = wb.create_sheet("现金流量表补充资料")
    hidden.sheet_state = "hidden"
    hidden.append(["项目", "本期金额"])
    hidden.append(["经营活动现金流量净额", "0"])
    wb.save(folder / "03报出报表.xlsx")
    save_json(folder / "extracted_tables.json", {
        "files": [],
        "tables": [
            {"id": 5, "source_file": "03报出报表.xlsx", "sheet": "现金流量表主表", "rows": [["项目", "本期金额"], ["经营活动现金流量净额", "11449812.43"]]},
            {"id": 8, "source_file": "03报出报表.xlsx", "sheet": "现金流量表补充资料", "rows": [["项目", "本期金额"], ["经营活动现金流量净额", "0"]]},
        ],
    })
    visible_calc = {"rule_name": "报出现金流量表补充资料未编制(预期不符)", "expected": "11449812.43", "actual": "0",
                    "difference": "11449812.43", "target": {"table_id": 5, "row": 1, "col": 1}, "calculation": {"match": False}}
    hidden_calc = {"rule_name": "隐藏表现金流量净额与主表不符(预期不符)", "expected": "11449812.43", "actual": "0",
                   "difference": "11449812.43", "target": {"table_id": 8, "row": 1, "col": 1}, "calculation": {"match": False}}
    first = issue("error1", "确认错误", "隐藏表不得作为报出资料。", table_id=None, row_range=None, context='"row_range"')
    first["calculations"] = [visible_calc, hidden_calc]
    second = issue("error2", "确认错误", "隐藏表来源不得报错。", table_id=8, row_range=[0, 2])
    second["calculations"] = [hidden_calc]
    data = {"meta": {"stage": "draft", "input_dir": str(folder)}, "coverage": {"expected_ids": ["error1", "error2"]}, "results": [first, second]}
    path = 验证目录 / "复核.xlsx"
    export.write_excel(data, 验证目录 / "结果.json", path)
    wb2 = load_workbook(path)
    text = visible_text(wb2)
    detail = "\n".join(str(c.value or "") for row in wb2["问题明细"].iter_rows() for c in row)
    assert sum(cell.value == "问题" for row in wb2["问题明细"].iter_rows() for cell in row if cell.column == 1) == 1
    assert "现金流量表补充资料" not in detail
    assert "隐藏表来源记录不进入问题明细" in text
    assert "提醒" in text
    wb2.close()


def test_隐藏行与隐藏列的值不参与(验证目录):
    folder = 验证目录 / "输入"
    folder.mkdir()
    wb = Workbook()
    ws = wb.active
    ws.title = "现流表"
    ws.append(["项目", "本期金额", "内部列"])
    ws.append(["经营活动现金流量净额", "11449812.43", "999"])
    ws.append(["隐藏行内容", "0", "888"])
    ws.row_dimensions[3].hidden = True
    ws.column_dimensions["C"].hidden = True
    wb.save(folder / "03报出报表.xlsx")
    save_json(folder / "extracted_tables.json", {
        "files": [],
        "tables": [{"id": 5, "source_file": "03报出报表.xlsx", "sheet": "现流表",
                    "rows": [["项目", "本期金额", "内部列"], ["经营活动现金流量净额", "11449812.43", "999"], ["隐藏行内容", "0", "888"]]}],
    })
    hidden_row_calc = {"rule_name": "隐藏行合计不符(预期不符)", "expected": "1", "actual": "0", "difference": "1",
                       "target": {"table_id": 5, "row": 2, "col": 1}, "calculation": {"match": False}}
    hidden_col_calc = {"rule_name": "隐藏列勾稽不符(预期不符)", "expected": "1", "actual": "0", "difference": "1",
                       "target": {"table_id": 5, "row": 1, "col": 2}, "calculation": {"match": False}}
    item = issue("error1", "确认错误", "隐藏内容不得报错。", table_id=None, row_range=None, context='"row"')
    item["calculations"] = [hidden_row_calc, hidden_col_calc]
    data = {"meta": {"stage": "draft", "input_dir": str(folder)}, "coverage": {"expected_ids": ["error1"]}, "results": [item]}
    path = 验证目录 / "复核.xlsx"
    export.write_excel(data, 验证目录 / "结果.json", path)
    text = visible_text(load_workbook(path))
    assert "隐藏行内容" not in text
    assert "999" not in text and "888" not in text
    assert "问题明细" in text


def test_定位落到具体行并给出对照位置(验证目录):
    folder = 验证目录 / "输入"
    folder.mkdir()
    rows8 = [["项目", "本期金额", "上期金额"]] + [["补填占位", "0", "0"]] * 21 + [["经营活动产生的现金流量净额", "0", "0"]]
    save_json(folder / "extracted_tables.json", {
        "files": [],
        "tables": [
            {"id": 5, "source_file": "03报出报表.xlsx", "sheet": "现金流量表主表",
             "rows": [["项目", "本期金额"], ["经营活动产生的现金流量净额", "11449812.43"]]},
            {"id": 8, "source_file": "03报出报表.xlsx", "sheet": "现金流量表补充资料", "rows": rows8},
        ],
    })
    first = issue("error1", "确认错误", "补充资料未填列，确认错误。", table_id=5, row_range=[0, 75], context='"row_range": [0, 75]')
    first["calculations"] = [
        {"rule_name": "现金流量表补充资料经营净额本期=现金流量表主表本期(预期不符)", "expected": "11449812.43", "actual": "0",
         "difference": "11449812.43", "target": {"table_id": 8, "row": 22, "col": 1},
         "operands": [{"table_id": 5, "row": 1, "col": 1}], "calculation": {"match": False}},
    ]
    data = {"meta": {"stage": "draft", "input_dir": str(folder)}, "coverage": {"expected_ids": ["error1"]}, "results": [first]}
    path = 验证目录 / "复核.xlsx"
    export.write_excel(data, 验证目录 / "结果.json", path)
    text = visible_text(load_workbook(path))
    assert "现金流量表补充资料 · 第23行（经营活动产生的现金流量净额行）" in text
    assert "现金流量表主表" in text
    assert "现流表 · 第1–75行" not in text
    assert "第1–75行" not in text


def test_凭什么说错固定三句且怎么改有完成标志(验证目录):
    item = issue("error1", "确认错误", "这是给人看的依据短句。")
    item["calculations"] = [
        {"rule_name": "应收合计=科控集团+科控酒店(本期)", "expected": "4093600.00", "actual": "4060000.00",
         "difference": "33600.00", "target": {"table_id": 17, "row": 3, "col": 1}, "calculation": {"match": False}},
    ]
    data = {"meta": {"stage": "final"}, "coverage": {"expected_ids": ["error1"]}, "results": [item]}
    path = 验证目录 / "复核.xlsx"
    export.write_excel(data, 验证目录 / "结果.json", path)
    text = visible_text(load_workbook(path))
    assert "核对方式：" in text and "关键差异：" in text and "判断：" in text
    assert "核对方式：比较应收合计与科控集团加科控酒店。" in text
    assert "怎么改" in text
    assert ("修改后" in text or "完成后" in text or "重新复核" in text)
    assert "请项目组确认" not in text


def test_无差异数据写不适用且依据拆句改写(验证目录):
    item = issue("minor1", "待核实", "第一处疑点：封面编号占位符；第二处疑点：更名年份晚于报告日。")
    item["expected"] = None
    item["actual"] = None
    item["difference"] = None
    data = {"meta": {"stage": "final"}, "coverage": {"expected_ids": ["minor1"]}, "results": [item]}
    path = 验证目录 / "复核.xlsx"
    export.write_excel(data, 验证目录 / "结果.json", path)
    text = visible_text(load_workbook(path))
    assert "不适用" in text
    assert "第一处疑点" in text
    assert "table-" not in text


def test_两个疑点拆成两条问题(验证目录):
    item = issue("error1", "待核实", "通读发现两处疑点：①该段称子公司于2026年7月完成更名，晚于报告日，疑年份笔误；②子公司表与单体口径不一致，请核实归属关系。")
    data = {"meta": {"stage": "final"}, "coverage": {"expected_ids": ["error1"]}, "results": [item]}
    path = 验证目录 / "复核.xlsx"
    export.write_excel(data, 验证目录 / "结果.json", path)
    wb = load_workbook(path)
    detail = "\n".join(str(c.value or "") for row in wb["问题明细"].iter_rows() for c in row)
    assert sum(cell.value == "问题" for row in wb["问题明细"].iter_rows() for cell in row if cell.column == 1) == 2
    assert "2026年7月" in detail
    assert "归属关系" in detail
    wb.close()


def test_人工严重程度优先于程序状态(验证目录):
    item = issue("minor1", "确认错误", "附注格式存在一处细节问题。")
    item["review"]["severity"] = "细节"
    data = {"meta": {"stage": "final"}, "coverage": {"expected_ids": ["minor1"]}, "results": [item]}
    path = 验证目录 / "复核.xlsx"
    export.write_excel(data, 验证目录 / "结果.json", path)
    wb = load_workbook(path)
    assert "细节" in visible_text(wb)
    assert "致命｜" not in visible_text(wb)
    wb.close()


def test_相同原因归并且不淹没主要问题(验证目录):
    items = [issue("u1", "未执行", "缺少必要资料，尚未完成核对"), issue("u2", "未执行", "缺少必要资料，尚未完成核对", table_id=18)]
    data = {"meta": {"stage": "draft"}, "coverage": {"expected_ids": ["u1", "u2"]}, "results": items}
    path = 验证目录 / "复核.xlsx"
    export.write_excel(data, 验证目录 / "结果.json", path)
    wb = load_workbook(path)
    ws = wb["问题明细"]
    assert sum(cell.value == "问题" for row in ws.iter_rows() for cell in row if cell.column == 1) == 1
    assert "2 条同类记录归并" in visible_text(wb)
    wb.close()


def test_同源错误合并且依据三句干净(验证目录):
    first = issue("error1", "确认错误", "现补表空白导致不符，确认错误。")
    first["calculations"] = [
        {"rule_name": "现金流量表补充资料经营净额本期=现金流量表主表本期(预期不符)", "expected": "11449812.43", "actual": "0",
         "difference": "11449812.43", "target": {"table_id": 8, "row": 22, "col": 1}, "calculation": {"match": False}},
        {"rule_name": "现金流量表补充资料经营净额上期=现金流量表主表上期(预期不符)", "expected": "-19487512.21", "actual": "0",
         "difference": "19487512.21", "target": {"table_id": 8, "row": 22, "col": 2}, "calculation": {"match": False}},
    ]
    second = issue("error2", "确认错误", "补充资料空白，确认错误。", calculations=first["calculations"][:1])
    summary = issue("summary", "确认错误", "跨表关系汇总", use_declared_relations=True)
    routine = issue("routine", "未执行", "明细中段，无小计行，本项无独立验算对象")
    items = [first, second, summary, routine]
    data = {"meta": {"stage": "draft"}, "coverage": {"expected_ids": [x["check_id"] for x in items]}, "results": items}
    path = 验证目录 / "复核.xlsx"
    export.write_excel(data, 验证目录 / "结果.json", path)
    wb = load_workbook(path)
    text = visible_text(wb)
    assert sum(cell.value == "问题" for row in wb["问题明细"].iter_rows() for cell in row if cell.column == 1) == 1
    assert "现金流量表补充资料经营净额" in text
    for residue in ("unaud", "supp-op", "rpart-", "cross_relations", "无独立验算对象", "：/", "；/", "现补表", "CFS", "r5代码", "未审"):
        assert residue not in text
    assert "核对方式：比较现金流量表补充资料经营净额与现金流量表主表。" in text
    assert "关键差异：" in text and "判断：" in text
    wb.close()


def test_Markdown同步七栏目(验证目录):
    item = issue("error1", "确认错误", "关联方明细与合计不符，确认错误。",
                 issue_title="关联方明细加总比附注合计多3.36万元",
                 fix_suggestion="核实两家关联方余额后改到一致；修改后重新复核本项。")
    data = {"meta": {"stage": "final", "company": "甲公司"}, "coverage": {"expected_ids": ["error1"]}, "results": [item]}
    path = 验证目录 / "复核.md"
    export.write_markdown(data, path)
    text = path.read_text(encoding="utf-8-sig")
    for required in ("问题概览", "问题明细", "严重程度", "错在哪", "核对了什么", "差多少", "凭什么说错", "怎么改", "关联方明细加总比附注合计多3.36万元"):
        assert required in text
    for machine in MACHINE:
        assert machine not in text
    assert "技术留痕" not in text


def test_来源漂移默认拦截显式放行并披露(验证目录):
    source = 验证目录 / "原件.xlsx"
    source.write_bytes(b"changed")
    item = issue("error1", "确认错误", "存在问题。", issue_title="测试问题", fix_suggestion="改正后重新复核本项。")
    data = {"meta": {"stage": "draft", "source_files": [{"path": str(source), "sha256": "0" * 64}]},
            "coverage": {"expected_ids": ["error1"]}, "results": [item]}
    path = 验证目录 / "漂移.xlsx"
    import pytest
    with pytest.raises(ValueError, match="失效|变化"):
        export.write_excel(data, 验证目录 / "结果.json", path)
    export.write_excel(data, 验证目录 / "结果.json", path, allow_source_drift=True)
    wb = load_workbook(path)
    tech = "\n".join(str(c.value or "") for row in wb["技术留痕"].iter_rows() for c in row)
    assert "来源变化" in tech
    wb.close()
