import importlib
from pathlib import Path

from 复核契约 import fingerprint, save_json, save_text


def test_草筛只读取一次报告正文(验证目录, monkeypatch):
    import run_check

    save_json(验证目录 / "extracted_tables.json", {"tables": [], "sources": [], "pending": []})
    report = 验证目录 / "report.md"
    save_text(report, "报告测试")
    original = Path.read_text
    reads = 0

    def counted(path, *args, **kwargs):
        nonlocal reads
        if path == report:
            reads += 1
        return original(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", counted)
    run_check.main([str(验证目录), "--scope", "deep", "-o", str(验证目录 / "结果.json")])
    assert reads == 1


def test_回填只校验一次输入(验证目录, monkeypatch):
    task = importlib.import_module("复核任务")
    folder = 验证目录 / "输入"
    folder.mkdir()
    source = folder / "原件.txt"
    save_text(source, "合成原件")
    save_json(folder / "extracted_tables.json", {
        "sources": [source.name],
        "files": [{"name": source.name, "path": str(source), "sha256": fingerprint(source)}],
        "tables": [{"id": 0, "source_file": source.name, "headers": ["项目", "金额"], "rows": [["业务", "100"]]}],
        "segments": [{"id": 0, "source_file": source.name, "text": "合成正文"}],
        "pending": [],
    })
    save_text(folder / "report.md", "合成正文")
    save_json(folder / "relations.json", {"checks": [], "not_applicable_basis": "仅测试任务队列"})
    state = task.init_review(folder, "128k", "standard")
    batch = task.next_batch(folder)
    objects = {obj["check_id"]: obj for obj in state["objects"]}
    answer = {
        "batch_id": batch["batch_id"],
        "source_fingerprint": state["source_fingerprint"],
        "results": [{
            "check_id": cid,
            "status": "不适用",
            "review": {
                "agent": "当前agent",
                "check_id": cid,
                "source_fingerprint": state["source_fingerprint"],
                "conclusion": "不适用",
                "basis": "合成资料仅用于验证队列",
                "source_refs": [{"check_id": cid, "quote": objects[cid]["material"][:30]}],
            },
        } for cid in batch["check_ids"]],
    }
    save_json(folder / "本批结论.json", answer)
    original = task._inputs
    calls = 0

    def counted(directory):
        nonlocal calls
        calls += 1
        return original(directory)

    monkeypatch.setattr(task, "_inputs", counted)
    task.main(["回填", str(folder), str(folder / "本批结论.json")])
    assert calls == 1


def test_技能入口要求复用脚本并按需读取(技能根目录):
    text = (技能根目录 / "SKILL.md").read_text(encoding="utf-8-sig")
    for script in ("parse_report.py", "apply_manifest.py", "calculator.py", "run_check.py", "复核任务.py", "export_report.py"):
        assert script in text
    assert "不得为这些步骤临时编写 Python 脚本" in text
    assert "按需读取" in text
    assert "完整读取[业务规则]" not in text
