"""导出人类可读的问题报告，并在隐藏工作表中保留技术留痕。"""
import argparse
import math
import re
import unicodedata
from decimal import Decimal, InvalidOperation
from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Font, PatternFill

from 复核契约 import load_json, validate_report, save_text, backup_existing, verify_sources, guard_outputs

SHEETS = ["问题概览", "问题明细", "技术留痕"]
SEVERITY_ORDER = {"致命": 0, "重要": 1, "细节": 2}
STATUS_SEVERITY = {"确认错误": "致命", "待核实": "重要", "未执行": "重要"}
SEVERITY_LABEL = {"致命": "致命（出报前必须改）", "重要": "重要（出报前要有着落）", "细节": "细节（有空就改）"}
COLORS = {"致命": "F4CCCC", "重要": "FCE5CD", "细节": "E8F0FE"}
SCOPE_NAMES = {"quick": "快速复核", "standard": "标准复核", "deep": "全面复核"}
HIDDEN_NOTICE = "隐藏表来源记录不进入问题明细"


def load_results(path, allow_source_drift=False):
    data = load_json(path)
    verify_sources(data, allow_source_drift=allow_source_drift)
    data.setdefault("meta", {})
    data["meta"].setdefault("stage", "draft")
    data.setdefault("results", [])
    data.setdefault("coverage", {"expected_ids": []})
    validate_report(data)
    return data


def field(item, name, default=""):
    value = item.get(name, default)
    return default if value is None else str(value)


def _basis(item):
    return field(item.get("review", {}), "basis") or field(item, "description")


def _human_number(value):
    if value in (None, ""):
        return "—"
    try:
        number = Decimal(str(value)).quantize(Decimal("0.01"))
        if not number.is_finite():
            return str(value)
        if abs(number) >= Decimal("10000"):
            return format(number / Decimal("10000"), ",.2f") + " 万元"
        return format(number, ",.2f") + " 元"
    except (InvalidOperation, ValueError):
        return str(value)


def _clean(value, hidden_names=()):
    text = str(value or "")
    text = re.sub(r"(?<![A-Za-z0-9_-])[a-z][a-z0-9]*(?:-[a-z0-9]+)+(?![A-Za-z0-9_-])", "", text)
    text = re.sub(r"[（(][^）)]*(?:预期|见复核|见终审)[^）)]*[）)]", "", text)
    text = re.sub(r"[（(]表\d+[）)]", "", text)
    text = re.sub(r"表\d+现流调整", "试算底稿现流调整表", text)
    text = re.sub(r"r\d+代码\d*(?:/\d+)*", "", text)
    text = re.sub(r"[\d.]*r\d+", "", text)
    text = re.sub(r"表\d{1,3}(?!\d)", "", text)
    text = re.sub(r"(?<![A-Za-z])vs(?![A-Za-z])", "与", text)
    for name in hidden_names:
        if name:
            text = text.replace(name, "隐藏工作表")
    replacements = {
        "现补表": "现金流量表补充资料",
        "CFS主表": "现金流量表主表",
        "CFS": "现金流量表",
        "BS": "资产负债表",
        "PL": "利润表",
        "relations": "核对关系",
        "计算草稿": "验算结果",
        "本地验算": "验算",
        "浮点残留": "计算尾差",
        "终审": "复核",
        "请项目组确认": "需项目组核实",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    text = re.sub(r"(?<=[：；])/", "", text)
    return re.sub(r"\s+", " ", text).strip(" ；;，,/")


def _severity(item):
    declared = item.get("review", {}).get("severity") or item.get("severity")
    return declared if declared in SEVERITY_ORDER else STATUS_SEVERITY.get(item.get("status"), "细节")


def _source_tables(data):
    directory = Path(field(data.get("meta", {}), "input_dir"))
    path = directory / "extracted_tables.json"
    if not directory.is_dir() or not path.is_file():
        return {}
    return {table.get("id"): table for table in load_json(path).get("tables", [])}


def _resolve_source(data, source):
    """源文件优先按最终来源清单的真实路径找，找不到再按提取目录拼。"""
    name = Path(source).name
    for entry in data.get("meta", {}).get("source_files", []):
        if Path(entry.get("path", "")).name == name or entry.get("name") == source:
            return Path(entry["path"])
    directory = Path(field(data.get("meta", {}), "input_dir"))
    path = Path(source)
    return path if path.is_absolute() else directory / source


def _table(item, tables, table_id=None):
    key = item.get("table_id") if table_id is None else table_id
    return tables.get(key, tables.get(str(key), {}))


def _hidden_maps(data, tables):
    """扫描源工作簿，返回（隐藏表ID集合, {表ID: (隐藏行集合, 隐藏列集合)}, 隐藏事实清单）。

    行号、列号统一换算成提取表的 0 基下标，与复核结果里的行列引用对齐。
    """
    from openpyxl.utils import column_index_from_string
    directory = Path(field(data.get("meta", {}), "input_dir"))
    states = {}
    layouts = {}
    hidden_ids = set()
    facts = []
    for table in tables.values():
        tid = table.get("id")
        source = table.get("source_file")
        if not source:
            continue
        path = _resolve_source(data, source)
        key = str(path.resolve())
        if key not in states:
            entry = {"sheets": {}, "rows": {}, "cols": {}}
            if path.suffix.lower() in (".xlsx", ".xlsm", ".xltx", ".xltm"):
                try:
                    workbook = load_workbook(path)
                    for sheet in workbook.worksheets:
                        entry["sheets"][sheet.title] = sheet.sheet_state
                        rows = {idx - 1 for idx, dim in sheet.row_dimensions.items() if dim.hidden}
                        cols = set()
                        for letter, dim in sheet.column_dimensions.items():
                            if dim.hidden:
                                start = dim.min or column_index_from_string(letter)
                                end = dim.max or start
                                cols.update(range(start - 1, end))
                        entry["rows"][sheet.title] = rows
                        entry["cols"][sheet.title] = cols
                    workbook.close()
                except (OSError, ValueError):
                    pass
            states[key] = entry
        entry = states[key]
        sheet = table.get("sheet")
        if entry["sheets"].get(sheet) not in (None, "visible"):
            hidden_ids.add(tid)
            layouts[tid] = (set(), set())
            facts.append({"file": Path(source).name, "sheet": sheet, "kind": "工作表"})
        else:
            rows = entry["rows"].get(sheet) or set()
            cols = entry["cols"].get(sheet) or set()
            layouts[tid] = (rows, cols)
            if rows or cols:
                facts.append({"file": Path(source).name, "sheet": sheet, "kind": "行或列"})
    return hidden_ids, layouts, facts


def _hidden_cell(row, hidden_ids, layouts):
    refs = [row.get("target", {}), *row.get("variables", {}).values(), *row.get("operands", [])]
    for ref in refs:
        if not isinstance(ref, dict):
            continue
        tid = ref.get("table_id")
        if tid in hidden_ids:
            return True
        rows, cols = layouts.get(tid, (set(), set()))
        if ref.get("row") in rows or ref.get("col") in cols:
            return True
    return False


def _location(item, tables=None, hidden_names=()):
    tables = tables or {}
    source = Path(field(item, "source_file")).name
    ref = item.get("_location_ref")
    table = _table(item, tables, ref.get("table_id")) if ref else _table(item, tables)
    parts = []
    detail = []
    if source:
        parts.append(source)
    for key in ("sheet", "name", "chapter"):
        value = table.get(key) or item.get(key)
        if value and str(value) not in parts:
            detail.append(_clean(value, hidden_names))
            break
    row_text = ""
    if ref and type(ref.get("row")) is int:
        rows = table.get("rows", [])
        label = ""
        if 0 <= ref["row"] < len(rows) and rows[ref["row"]]:
            label = str(rows[ref["row"]][0] or "").strip()
        row_text = "第" + str(ref["row"] + 1) + "行"
        if label:
            row_text += "（" + _clean(label, hidden_names) + "行）"
        detail.append(row_text)
    elif item.get("row_range") is not None:
        start, end = item["row_range"]
        if end - start <= 6:
            detail.append("第" + str(start + 1) + ("–" + str(end) if end > start + 1 else "") + "行")
        else:
            rows = table.get("rows", [])
            labels = [str(rows[i][0] or "").strip() for i in range(start, min(end, len(rows))) if rows[i] and rows[i][0]]
            detail.append(labels[0] + "等" if labels else "本节内")
    elif item.get("page") is not None:
        detail.append("第" + str(item["page"]) + "页")
    elif item.get("source_span") is not None and item.get("table_id") is None:
        detail.append("文中对应段落（原文见「关键差异」引述）")
    if not detail and item.get("table_id") is None:
        detail.append("跨表核对汇总")
    if not table and item.get("table_id") is not None and not any(key in item for key in ("sheet", "name", "chapter")):
        detail.insert(0, "文档内第" + str(item["table_id"] + 1) + "个表格")
    if ref and ref.get("table_id") is not None and item.get("_contrast_ref"):
        contrast = item["_contrast_ref"]
        ctable = _table(item, tables, contrast.get("table_id"))
        cname = ctable.get("sheet") or ctable.get("name") or ctable.get("chapter") or ""
        crows = ctable.get("rows", [])
        clabel = ""
        crow = contrast.get("row")
        if type(crow) is int and 0 <= crow < len(crows) and crows[crow]:
            clabel = str(crows[crow][0] or "").strip()
        contrast_text = _clean(cname, hidden_names)
        if clabel:
            contrast_text += (" · " if contrast_text else "") + ("第" + str(crow + 1) + "行（" + clabel + "行）" if type(crow) is int else clabel)
        if contrast_text:
            parts.append("对照位置：" + contrast_text)
    where = " · ".join(parts[:1] + detail)
    if len(parts) > 1:
        where += "\n" + parts[1]
    return where or "跨表核对汇总"


def _rule_name(row):
    name = re.sub(r"[（(][^）)]*[）)]", "", field(row, "rule_name"))
    return name.replace("本期", "").replace("上期", "").strip(" ：:，,")


def _relation_text(row, hidden_names=(), joiner="与", tables=None):
    raw = _clean(_rule_name(row), hidden_names)
    name = raw.replace("=", "与").replace("+", "加") if raw else ""
    sides = name.split("与") if "与" in name else [name]
    if not name or any(len(side.strip()) < 4 for side in sides):
        composed = _relation_from_refs(row, tables, hidden_names, joiner)
        if composed:
            return composed
    return (raw.replace("=", joiner).replace("+", "加") if raw else "") or "该项核对关系"


def _relation_from_refs(row, tables, hidden_names=(), joiner="与"):
    if not tables:
        return ""
    target = row.get("target", {}) or {}
    ops = row.get("operands") or []
    pieces = []
    for ref in [target, *ops[:1]]:
        if not isinstance(ref, dict) or ref.get("table_id") is None:
            continue
        table = tables.get(ref.get("table_id"), {})
        sheet = _clean(table.get("sheet") or table.get("name") or table.get("chapter") or "", hidden_names)
        rows = table.get("rows", [])
        label = ""
        if type(ref.get("row")) is int and 0 <= ref["row"] < len(rows) and rows[ref["row"]]:
            label = str(rows[ref["row"]][0] or "").strip()
        if not label or re.fullmatch(r"[\d.,%\-\s]+", label):
            continue
        pieces.append(sheet + "的「" + label + "」" if sheet else "「" + label + "」")
    return joiner.join(pieces) if len(pieces) == 2 else ""


def _preferred_mismatch(item):
    rows = _mismatches(item)
    return next((row for row in rows if "预期存在" not in field(row, "rule_name")), rows[0]) if rows else {}


def _primary_rule(item):
    return _clean(_rule_name(_preferred_mismatch(item)), item.get("_hidden_names", ()))


def _title(item):
    if item.get("issue_title"):
        return _clean(field(item, "issue_title"), item.get("_hidden_names", ()))
    rows = _mismatches(item)
    if rows:
        primary = _preferred_mismatch(item)
        relation = _relation_text(primary, item.get("_hidden_names", ()), tables=item.get("_tables"))
        diff = _human_number(primary.get("difference"))
        if diff not in ("—", "0.00 元", "0.00 万元"):
            return relation + "不一致，差 " + diff
        return relation + "不一致"
    basis = _clean(_basis(item), item.get("_hidden_names", ()))
    if basis:
        parts = [part.strip() for part in re.split(r"[。；]", basis) if part.strip()]
        selected = parts[0] if parts else basis
        return selected if len(selected) <= 90 else selected[:89] + "…"
    name = _clean(field(item, "rule_name", "复核发现的问题"), item.get("_hidden_names", ()))
    return re.sub(r"^(?:table|text|cross_relations)-?", "", name) or "复核发现的问题"


def _mismatches(item):
    rows = [c for c in item.get("calculations", []) if c.get("calculation", {}).get("match") is False]
    had_calculations = bool(item.get("calculations"))
    hidden_ids = item.get("_hidden_ids", set())
    layouts = item.get("_hidden_layouts", {})
    rows = [row for row in rows if not _hidden_cell(row, hidden_ids, layouts)]
    rows = [row for row in rows if "预期存在" not in field(row, "rule_name")]
    if not rows and not had_calculations and item.get("expected") is not None and item.get("actual") is not None and item.get("status") in STATUS_SEVERITY:
        rows = [item]
    unique = []
    seen = set()
    for row in rows:
        key = (field(row, "rule_name"), field(row, "expected"), field(row, "actual"), field(row, "difference"))
        if key not in seen:
            seen.add(key)
            unique.append(row)
    group = item.get("_rule_group")
    return [row for row in unique if _clean(_rule_name(row), item.get("_hidden_names", ())) == group] if group else unique


def _unit(item, tables):
    target = item.get("target", {})
    if target.get("unit"):
        return target["unit"]
    return _table(item, tables, target.get("table_id")).get("unit") or item.get("unit") or ""


def _check_rule(item):
    rows = _mismatches(item)
    if rows:
        primary = _preferred_mismatch(item)
        relation = _relation_text(primary, item.get("_hidden_names", ()), joiner="应该等于", tables=item.get("_tables"))
        return relation + "。"
    basis = _clean(_basis(item), item.get("_hidden_names", ()))
    return basis.split("。")[0] + "。" if basis else "按本次复核安排完成的核对。"


def _difference(item, tables):
    rows = _mismatches(item)
    if not rows:
        return "不适用"
    lines = []
    for row in rows[:5]:
        unit = _unit(row, tables)
        expected = _human_number(row.get("expected"))
        actual = _human_number(row.get("actual"))
        diff = _human_number(row.get("difference"))
        if unit and expected not in ("—",) and "元" not in expected:
            expected += unit
        relation = _relation_text(row, item.get("_hidden_names", ()), tables=item.get("_tables"))
        lines.append(relation + "：核对基准 " + expected + "，报告 " + actual + "，差 " + diff)
    if len(rows) > 5:
        lines.append("另有" + str(len(rows) - 5) + "条差异，见技术留痕。")
    return "\n".join(lines)


def _basis_text(item, tables):
    rows = _mismatches(item)
    lines = []
    if rows:
        primary = _preferred_mismatch(item)
        lines.append("核对方式：比较" + _relation_text(primary, item.get("_hidden_names", ()), tables=item.get("_tables")) + "。")
        lines.append("关键差异：")
        for row in rows[:5]:
            unit = _unit(row, tables)
            diff = _human_number(row.get("difference"))
            lines.append("- " + _relation_text(row, item.get("_hidden_names", ()), tables=item.get("_tables")) + "：差 " + diff + ("。" if "元" in diff or diff == "—" else unit + "。"))
        if len(rows) > 5:
            lines.append("- 另有" + str(len(rows) - 5) + "条同类差异，完整数据在技术留痕。")
        lines.append("判断：" + _title(item) + "，不属于容差内尾差。")
    else:
        text = _clean(_basis(item), item.get("_hidden_names", ()))
        sentences = [s.strip() for s in re.split(r"[。；]", text) if s.strip()]
        if sentences:
            lines.append("核对方式：通读核对相关资料。")
            lines.append("关键差异：" + "；".join(sentences) + "。")
            lines.append("判断：" + (sentences[0] if sentences else "需人工确认") + "，出报前应处理。")
        else:
            lines.append("核对方式：按本次复核安排完成的核对。")
            lines.append("关键差异：无量化差异。")
            lines.append("判断：按复核结论处理。")
    if item.get("_group_count", 1) > 1:
        lines.append("本项由" + str(item["_group_count"]) + " 条同类记录归并，不是" + str(item["_group_count"]) + "个独立错误。")
    return "\n".join(lines)


def _suggestion(item):
    if item.get("fix_suggestion"):
        return field(item, "fix_suggestion")
    status = item.get("status")
    relation = ""
    rows = _mismatches(item)
    if rows:
        relation = _relation_text(_preferred_mismatch(item), item.get("_hidden_names", ()), tables=item.get("_tables"))
    if status == "确认错误":
        target = relation or "该处数字"
        return "核对并更正" + target + "两侧的明细或合计，改到两边一致；修改后重新复核本项。"
    if status == "待核实":
        title = _title(item)
        return "在出报前核实「" + title + "」涉及的原文与口径，确认后修正或补充依据；完成后本项核销。"
    return "补充完成该项检查所需的资料或核对；补充完成前不作为已完成，完成后本项核销。"


def _split_doubts(item):
    basis = _basis(item)
    marks = list(re.finditer(r"[①②③④⑤]", basis))
    if len(marks) < 2:
        return [item]
    pieces = []
    for index, mark in enumerate(marks):
        start = mark.end()
        end = marks[index + 1].start() if index + 1 < len(marks) else len(basis)
        piece = basis[start:end].strip(" ；;，,")
        if piece:
            pieces.append(piece)
    items = []
    for piece in pieces:
        clone = dict(item)
        clone.pop("issue_title", None)
        clone.pop("expected", None)
        clone.pop("actual", None)
        clone.pop("difference", None)
        clone.pop("calculations", None)
        clone.pop("calculation", None)
        clone["review"] = dict(item.get("review", {}))
        clone["review"]["basis"] = piece
        items.append(clone)
    return items or [item]


def _card(item, tables):
    severity = _severity(item)
    where = _location(item, tables, item.get("_hidden_names", ()))
    contrast = ""
    if "对照位置：" in where:
        where, contrast = where.split("\n对照位置：", 1) if "\n对照位置：" in where else (where, "")
        if contrast:
            where = where + "\n对照位置：" + contrast
    return {
        "severity": severity,
        "title": _title(item),
        "severity_label": SEVERITY_LABEL[severity],
        "where": where,
        "check_rule": _check_rule(item),
        "difference": _difference(item, tables),
        "basis": _basis_text(item, tables),
        "fix": _suggestion(item),
    }


def _cards(data, tables, hidden_ids=None, layouts=None):
    hidden_ids = set() if hidden_ids is None else set(hidden_ids)
    layouts = layouts or {}
    hidden_names = {tables[tid].get("sheet") for tid in hidden_ids if tables.get(tid)}
    grouped = {}
    cards = []
    hidden_dropped = []
    for item in data["results"]:
        if item.get("status") not in STATUS_SEVERITY or item.get("use_declared_relations"):
            continue
        if item.get("table_id") in hidden_ids:
            hidden_dropped.append(item)
            continue
        basis = _basis(item)
        if "无独立验算对象" in basis or "不做独立验算" in basis:
            continue
        expanded = []
        for piece in _split_doubts(item):
            piece = dict(piece)
            piece["_hidden_ids"] = hidden_ids
            piece["_hidden_layouts"] = layouts
            piece["_hidden_names"] = hidden_names
            piece["_tables"] = tables
            calcs = piece.get("calculations", [])
            if calcs and all(_hidden_cell(c, hidden_ids, layouts) for c in calcs):
                hidden_dropped.append(piece)
                continue
            if piece.get("status") == "确认错误" and calcs and not _mismatches(piece):
                continue
            expanded.append(piece)
        for piece in expanded:
            rows = [r for r in _mismatches(piece) if r is not piece]
            if rows:
                ref = _preferred_mismatch(piece).get("target", {})
                piece["_location_ref"] = ref if ref else None
                operands = rows[0].get("operands") or []
                if operands:
                    piece["_contrast_ref"] = operands[0]
            if piece.get("status") == "确认错误":
                piece["_rule_group"] = _primary_rule(piece)
                key = ("确认错误", piece["_rule_group"] or _title(piece))
            elif piece.get("status") == "未执行":
                key = ("未执行", Path(field(piece, "source_file")).name, _clean(_basis(piece), hidden_names), _severity(piece))
            else:
                key = None
            if key is not None:
                if key in grouped:
                    grouped[key]["_group_count"] += 1
                    continue
                piece["_group_count"] = 1
                grouped[key] = piece
            cards.append(piece)
    cards.sort(key=lambda item: (SEVERITY_ORDER[_severity(item)], _location(item, tables, item.get("_hidden_names", ()))))
    return [_card(item, tables) for item in cards], hidden_dropped


def _counts(cards):
    return {severity: sum(card["severity"] == severity for card in cards) for severity in SEVERITY_ORDER}


def _conclusion(data, counts):
    if counts["致命"]:
        return "当前不建议直接出报：先处理" + str(counts["致命"]) + "项致命问题。"
    if counts["重要"]:
        return "确认" + str(counts["重要"]) + "项重要事项后再定稿。"
    if data.get("meta", {}).get("stage") != "final":
        return "复核尚未完成，当前结果仅供阶段检查。"
    return "未发现需优先处理的问题，可按既定范围完成后续出报复核。"


def _cell(ws, row, col, value, bold=False, fill=None, size=11):
    cell = ws.cell(row, col, str(value) if value is not None else "")
    cell.data_type = "s"
    cell.font = Font(name="微软雅黑", size=size, bold=bold, color="FFFFFF" if fill == "4472C4" else "222222")
    cell.alignment = Alignment(vertical="top", wrap_text=True)
    if fill:
        cell.fill = PatternFill("solid", fgColor=fill)
    return cell


def _row_height(ws, row, widths):
    lines = 1
    for col, width in widths.items():
        text = str(ws.cell(row, col).value or "")
        wrapped = sum(max(1, math.ceil(sum(2 if unicodedata.east_asian_width(ch) in "WF" else 1 for ch in line) * 1.15 / width)) for line in text.split("\n"))
        lines = max(lines, wrapped)
    ws.row_dimensions[row].height = min(409, max(24, lines * 19 + 8))


def _write_overview(wb, data, cards, counts, hidden_facts):
    ws = wb.active
    ws.title = SHEETS[0]
    company = field(data.get("meta", {}), "company", "审计报告")
    ws.merge_cells("A1:D1")
    _cell(ws, 1, 1, company + "复核结果", True, "4472C4", 16)
    ws.merge_cells("A2:D2")
    _cell(ws, 2, 1, _conclusion(data, counts), True, COLORS["致命"] if counts["致命"] else COLORS["重要"], 12)
    for col, label in enumerate(("致命", "重要", "细节", "已排除误报"), 1):
        _cell(ws, 4, col, label, True, "D9E2F3")
        value = counts.get(label, 0) if label != "已排除误报" else sum(item.get("status") == "已排除误报" for item in data["results"])
        _cell(ws, 5, col, value, True, COLORS.get(label), 15)
    ws.merge_cells("A7:D7")
    _cell(ws, 7, 1, "最需要先处理的问题", True, "D9E2F3")
    priorities = [card for card in cards if card["severity"] == "致命"] or [card for card in cards if card["severity"] == "重要"]
    row = 8
    for card in priorities[:5]:
        _cell(ws, row, 1, card["severity"], True, COLORS[card["severity"]])
        ws.merge_cells(start_row=row, start_column=2, end_row=row, end_column=4)
        _cell(ws, row, 2, card["title"] + "（" + card["where"].split("\n")[0] + "）")
        _row_height(ws, row, {2: 100})
        row += 1
    if not priorities:
        ws.merge_cells("A8:D8")
        _cell(ws, 8, 1, "当前没有需要优先展示的问题。")
        row = 9
    row += 1
    scope = SCOPE_NAMES.get(field(data.get("meta", {}), "scope"), field(data.get("meta", {}), "scope", "按本次选择范围"))
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=4)
    _cell(ws, row, 1, "复核范围：" + str(len(data.get("meta", {}).get("source_files", []))) + "份文件｜" + scope + "｜原始记录" + str(len(data["results"])) + "条")
    row += 2
    if hidden_facts:
        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=4)
        _cell(ws, row, 1, "提醒｜发现隐藏内容，默认不作为报出资料", True, "D9E2F3")
        row += 1
        for fact in hidden_facts[:3]:
            ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=4)
            _cell(ws, row, 1, "「" + fact["file"] + "」里有藏起来的" + fact["kind"] + "「" + fact["sheet"] + "」。打开文件后肉眼看不到；隐藏内容默认不算报出内容，未参与核对，也不会拿它报错。请确认是否属于报出内容。" + HIDDEN_NOTICE + "。")
            _row_height(ws, row, {1: 100})
            row += 1
    for col, width in zip("ABCD", (18, 32, 32, 24)):
        ws.column_dimensions[col].width = width
    for number in (1, 2, 4, 5):
        _row_height(ws, number, {1: 100})
    ws.sheet_view.showGridLines = False
    ws.freeze_panes = "A4"


def _write_details(wb, cards):
    ws = wb.create_sheet(SHEETS[1])
    ws.merge_cells("A1:B1")
    _cell(ws, 1, 1, "问题明细｜按致命、重要、细节排序；每项均可直接定位和修改", True, "4472C4", 12)
    row = 3
    for card in cards:
        values = (
            ("问题", card["title"]),
            ("严重程度", card["severity_label"]),
            ("错在哪", card["where"]),
            ("核对了什么", card["check_rule"]),
            ("差多少", card["difference"]),
            ("凭什么说错", card["basis"]),
            ("怎么改", card["fix"]),
        )
        for label, value in values:
            _cell(ws, row, 1, label, True, COLORS[card["severity"]] if label == "问题" else "D9E2F3")
            _cell(ws, row, 2, value, label == "问题", COLORS[card["severity"]] if label == "问题" else None)
            _row_height(ws, row, {2: 105})
            row += 1
        row += 1
    ws.column_dimensions["A"].width = 18
    ws.column_dimensions["B"].width = 110
    ws.sheet_view.showGridLines = False
    ws.freeze_panes = "A3"


def _write_technical(wb, data, results_path, drift_notes):
    ws = wb.create_sheet(SHEETS[2])
    headings = ["对象ID", "状态", "检查类型", "内部规则名", "完整文件路径", "表格ID", "行号区间", "字符区间", "来源指纹", "结果文件路径", "原始复核依据", "原始上下文"]
    for col, value in enumerate(headings, 1):
        _cell(ws, 1, col, value, True, "4472C4")
    row_number = 2
    for note in drift_notes:
        _cell(ws, row_number, 11, note)
        _row_height(ws, row_number, {11: 70})
        row_number += 1
    for item in data["results"]:
        values = [
            item["check_id"], item["status"], field(item, "check_type"), field(item, "rule_name"), field(item, "source_file"),
            field(item, "table_id"), field(item, "row_range"), field(item, "source_span"), field(item, "source_fingerprint"),
            str(Path(results_path).resolve()), _basis(item), field(item, "context"),
        ]
        for col, value in enumerate(values, 1):
            _cell(ws, row_number, col, value)
        _row_height(ws, row_number, {11: 70, 12: 45})
        row_number += 1
    for col, width in zip("ABCDEFGHIJKL", (28, 14, 16, 36, 65, 12, 18, 18, 30, 65, 75, 50)):
        ws.column_dimensions[col].width = width
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions
    ws.sheet_view.showGridLines = False
    ws.sheet_state = "hidden"


def _protect(data, out_path, results_path=None):
    output = Path(out_path).resolve()
    if data.get("meta", {}).get("input_dir"):
        guard_outputs(data["meta"]["input_dir"], output)
    protected = {Path(results_path).resolve()} if results_path is not None else set()
    protected.update(Path(f["path"]).resolve() for f in data.get("meta", {}).get("source_files", []) if f.get("path"))
    for item in data.get("results", []):
        if item.get("source_file"):
            protected.add(Path(item["source_file"]).resolve())
        for ref in item.get("source_refs", []):
            if isinstance(ref, dict) and ref.get("source_file"):
                protected.add(Path(ref["source_file"]).resolve())
    if output in protected:
        raise ValueError("输出不能覆盖原始来源或结果输入")
    return output


def _drift_notes(data):
    notes = []
    for source in data.get("meta", {}).get("source_files", []):
        path = Path(source["path"])
        try:
            from 复核契约 import fingerprint
            if path.is_file() and source.get("sha256") and fingerprint(path) != source["sha256"]:
                notes.append("来源变化：" + path.name + " 在复核后被修改，本报告结论基于复核时版本的资料，未重跑复核。")
        except OSError:
            notes.append("来源变化：" + path.name + " 无法读取，本报告结论基于复核时版本的资料。")
    return notes


def write_excel(data, results_path, out_path, allow_source_drift=False):
    verify_sources(data, allow_source_drift=allow_source_drift)
    validate_report(data)
    out = _protect(data, out_path, results_path)
    tables = _source_tables(data)
    hidden_ids, layouts, hidden_facts = _hidden_maps(data, tables)
    cards, _ = _cards(data, tables, hidden_ids, layouts)
    counts = _counts(cards)
    wb = Workbook()
    _write_overview(wb, data, cards, counts, hidden_facts)
    _write_details(wb, cards)
    _write_technical(wb, data, results_path, _drift_notes(data) if allow_source_drift else [])
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        backup_existing(out)
    wb.save(out)
    wb.close()


def write_markdown(data, out_path, allow_source_drift=False):
    verify_sources(data, allow_source_drift=allow_source_drift)
    validate_report(data)
    out = _protect(data, out_path)
    tables = _source_tables(data)
    hidden_ids, layouts, hidden_facts = _hidden_maps(data, tables)
    cards, _ = _cards(data, tables, hidden_ids, layouts)
    counts = _counts(cards)
    company = field(data.get("meta", {}), "company", "审计报告")
    false_count = sum(item.get("status") == "已排除误报" for item in data["results"])
    lines = [
        "# " + company + "复核结果", "", "> " + _conclusion(data, counts), "",
        "## 问题概览", "",
        "- 致命：" + str(counts["致命"]) + "项",
        "- 重要：" + str(counts["重要"]) + "项",
        "- 细节：" + str(counts["细节"]) + "项",
        "- 已排除误报：" + str(false_count) + "条，不列入待办", "",
    ]
    priorities = [card for card in cards if card["severity"] == "致命"] or [card for card in cards if card["severity"] == "重要"]
    if priorities:
        lines.append("最需要先处理的问题：")
        lines.extend("- **" + card["severity"] + "｜" + card["title"] + "**：" + card["where"].split("\n")[0] for card in priorities[:5])
    if hidden_facts:
        lines.extend(["", "### 提醒｜发现隐藏内容，默认不作为报出资料", ""])
        for fact in hidden_facts[:3]:
            lines.append("- 「" + fact["file"] + "」里有藏起来的" + fact["kind"] + "「" + fact["sheet"] + "」。打开文件后肉眼看不到；隐藏内容默认不算报出内容，未参与核对，也不会拿它报错。请确认是否属于报出内容。" + HIDDEN_NOTICE + "。")
    lines.extend(["", "## 问题明细", ""])
    for card in cards:
        lines.extend([
            "### " + card["title"], "",
            "- **严重程度**：" + card["severity_label"],
            "- **错在哪**：" + card["where"].replace("\n", "；"),
            "- **核对了什么**：" + card["check_rule"],
            "- **差多少**：" + card["difference"].replace("\n", "；"),
            "- **凭什么说错**：" + card["basis"].replace("\n", "；"),
            "- **怎么改**：" + card["fix"], "",
        ])
    save_text(out, "\n".join(lines).rstrip() + "\n")


def derive_output_paths(results_path, meta, output_arg):
    stem = Path(str(meta.get("source") or "审计报告")).stem
    for ch in '/\\:*?"<>|':
        stem = stem.replace(ch, "_")
    if output_arg and Path(output_arg).suffix.lower() == ".xlsx":
        path = Path(output_arg).resolve()
        return path, path.with_name(path.stem + "_复核报告.md")
    directory = Path(output_arg).resolve() if output_arg else Path(results_path).parent
    return directory / (stem + "_检查报告.xlsx"), directory / (stem + "_复核报告.md")


def main(argv=None):
    parser = argparse.ArgumentParser(description="导出问题概览、问题明细、Markdown及默认隐藏的技术留痕")
    parser.add_argument("results")
    parser.add_argument("-o", "--output")
    parser.add_argument("--allow-source-drift", action="store_true", help="源文件在复核后有修改时放行导出，并在技术留痕披露")
    args = parser.parse_args(argv)
    try:
        path = Path(args.results).resolve()
        data = load_results(path, allow_source_drift=args.allow_source_drift)
        excel, markdown = derive_output_paths(path, data["meta"], args.output)
        write_excel(data, path, excel, allow_source_drift=args.allow_source_drift)
        write_markdown(data, markdown, allow_source_drift=args.allow_source_drift)
        print("已导出：" + str(excel) + "；" + str(markdown))
        return 0
    except (ValueError, KeyError, TypeError, OSError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    raise SystemExit(main())
