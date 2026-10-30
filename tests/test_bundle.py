"""技能包完整性校验：先于组装编写，红灯起步。"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_skill_refs_exist():
    # 扫描运行时指引文件：SKILL.md 与文字审查速查（均从包根出发引用 references/... 路径）
    checked = []
    for name in ("SKILL.md", "references/文字审查速查.md"):
        text = (ROOT / name).read_text(encoding="utf-8")
        checked += [(name, r) for r in re.findall(r"references/[\w\-/\.]+\.(?:md|json)", text)]
    missing = [f"{src} -> {r}" for src, r in checked if not (ROOT / r).exists()]
    assert not missing, f"引用了不存在的文件: {missing}"


def test_no_external_refs():
    # 只检查运行时内容面；docs/ 为开发溯源档案（按需求保留原始路径记录），tests/ 为测试自身
    bad = []
    targets = [ROOT / "SKILL.md", ROOT / "test-prompts.json"]
    for sub in ("references", "scripts"):
        targets += [p for p in (ROOT / sub).rglob("*") if p.is_file()]
    for p in targets:
        if ".git" in p.parts:
            continue
        if p.name == "SOURCES.json":
            continue  # 台账的职责就是记录上游原始路径，属合法外部记录
        if p.suffix.lower() not in {".md", ".json", ".py", ".txt"}:
            continue
        text = p.read_text(encoding="utf-8", errors="ignore")
        for pat in ("../../", "D:\\BaiduSyncdisk", ".workbuddy/skills"):
            if pat in text:
                bad.append(f"{p.relative_to(ROOT)} 含外部引用 {pat}")
    assert not bad, "\n".join(bad)


def test_sources_complete():
    data = json.loads((ROOT / "references/SOURCES.json").read_text(encoding="utf-8"))
    ids = {s["id"] for s in data["sources"]}
    expect = {"audit-report-checker", "tianchuan-perspective", "chen-yiwei-perspective",
              "writing", "humanizer-zh", "human-writing", "officecli-huaxin-format"}
    assert ids == expect, f"来源台账缺口: {expect - ids}"
    for s in data["sources"]:
        assert s.get("license"), f"{s['id']} 缺许可字段"
        assert s.get("synced_at"), f"{s['id']} 缺同步日期"


def test_notice_covers_third_party():
    notice = (ROOT / "NOTICE").read_text(encoding="utf-8")
    for name in ("audit-report-checker", "tianchuan-perspective", "chen-yiwei-perspective",
                 "writing", "humanizer-zh", "human-writing", "officecli-huaxin-format"):
        assert name in notice, f"NOTICE 缺 {name}"


def test_licenses_present():
    lic = ROOT / "references/licenses"
    for f in ("MIT-tianchuan-perspective.txt", "MIT-chen-yiwei-perspective.txt",
              "MIT-writing.txt", "MIT-humanizer-zh.txt", "MIT-human-writing.txt"):
        assert (lic / f).exists(), f"缺许可全文 {f}"
    assert (ROOT / "LICENSE").exists(), "缺主 LICENSE"


def test_pe_excluded():
    for p in (ROOT / "references").rglob("*"):
        assert "private-equity" not in p.name.lower(), f"PE 内容残留: {p}"
    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    assert "该视角未整合" in skill, "SKILL.md 缺 PE 未整合标注"
