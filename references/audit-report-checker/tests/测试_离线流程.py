import importlib
import runpy
import sys
import pytest

def test_旧通过标记不能代替终审(契约):
    item = 契约.normalize_result({"passed": True, "severity": "info", "description": "跳过"})
    assert item["status"] == "未执行"
    assert item["passed"] is False

def test_未完成不能作为最终报告(契约):
    data = {"meta": {"stage": "final"}, "coverage": {"expected_ids": ["a"]}, "results": []}
    with pytest.raises(ValueError, match="未完成|覆盖"):
        契约.validate_report(data)

def test_默认入口不访问模型(技能根目录, 验证目录, monkeypatch):
    import json
    (验证目录 / "extracted_tables.json").write_text(json.dumps({"tables": [], "sources": []}), encoding="utf-8")
    (验证目录 / "report.md").write_text("报告测试", encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["run_check.py", str(验证目录), "-o", str(验证目录 / "结果.json")])
    try:
        runpy.run_path(str(技能根目录 / "scripts" / "run_check.py"), run_name="__main__")
    except SystemExit as exc:
        assert exc.code in (0, None)
    result = json.loads((验证目录 / "结果.json").read_text(encoding="utf-8-sig"))
    assert result["meta"]["stage"] == "draft"

def test_JSON金额精度与BOM(契约, 验证目录):
    from decimal import Decimal
    path = 验证目录 / "金额.json"
    契约.save_json(path, {"金额": Decimal("9999999999999999.99")})
    assert path.read_bytes().startswith(b"\xef\xbb\xbf")
    assert 契约.load_json(path)["金额"] == "9999999999999999.99"

def test_已有文件覆盖有可验证备份(契约, 验证目录):
    path = 验证目录 / "进度.json"
    契约.save_json(path, {"版本": 1})
    before = path.read_bytes()
    saved = 契约.backup_existing(path)
    assert saved.read_bytes() == before
    assert saved.is_relative_to(__import__("pathlib").Path.home() / "BackUp")
    契约.save_json(path, {"版本": 2})
    assert 契约.load_json(path)["版本"] == 2

def test_正确词不能屏蔽别处错字(验证目录):
    import run_check
    path=验证目录/"文本.md";path.write_text("利润表为正确标题。另一处写为润表。",encoding="utf-8")
    rows=[];run_check.check_typos(path,rows)
    assert any("润表" in r.get("context","") for r in rows)

def test_有终审字样但计算实际不一致不能通过(契约):
    item={"check_id":"a","status":"通过","expected":"100","actual":"99","calculation":{"match":True},"review":{"agent":"当前agent","check_id":"a","source_fingerprint":"s","conclusion":"通过","basis":"声称核过","source_refs":[{"quote":"原文"}]}}
    with pytest.raises(ValueError,match="计算|差异"):
        契约.normalize_result(item)
def test_技能正文明确上下文与当前模型(技能根目录):
    text=(技能根目录/"SKILL.md").read_text(encoding="utf-8-sig")
    assert "128K" in text and "1M" in text
    assert "复核任务.py" in text
    assert "当前agent" in text or "当前 agent" in text

