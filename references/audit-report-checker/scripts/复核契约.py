"""本地复核的状态、证据及可恢复写入约定。"""
import hashlib
import json
import os
import shutil
import uuid
from datetime import date, datetime, time
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKUP_ROOT = Path.home() / "BackUp"
STATUSES = ("通过", "确认错误", "待核实", "未执行", "不适用", "已排除误报")

def fingerprint(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def stable_id(value):
    text = json.dumps(value, ensure_ascii=False, sort_keys=True, default=_decimal)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:24]

def _decimal(value):
    if isinstance(value, Decimal) and value.is_finite():
        return format(value, "f")
    if isinstance(value, (datetime, date, time)):
        return value.isoformat()
    raise TypeError("不支持的JSON值：" + type(value).__name__)

def backup_existing(path):
    path = Path(path).resolve()
    if not path.exists():
        return None
    relative = path.relative_to(ROOT) if path.is_relative_to(ROOT) else Path(path.name)
    folder = BACKUP_ROOT / ("audit-report-checker_" + datetime.now().strftime("%Y%m%d_%H%M%S_%f") + "_" + uuid.uuid4().hex[:6])
    target = folder / relative
    target.parent.mkdir(parents=True)
    shutil.copy2(path, target)
    if fingerprint(path) != fingerprint(target):
        raise OSError("备份校验失败：" + str(path))
    return target

def save_text(path, text):
    path = Path(path)
    if "\ufffd" in text:
        raise ValueError("输出含替换字符，请核对原始文字")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary=path.with_name("."+path.name+".未完成_"+uuid.uuid4().hex+".tmp")
    with temporary.open("x", encoding="utf-8-sig", newline="\n") as f:
        f.write(text)
        f.flush()
        os.fsync(f.fileno())
    if temporary.read_text(encoding="utf-8-sig") != text:
        raise OSError("写入回读不一致：" + str(path))
    backup_existing(path)
    os.replace(temporary,path)

def guard_outputs(directory,*outputs,allow_names=()):
    directory=Path(directory).resolve()
    names=("report.md","extracted_tables.json","files_index.json","manifest.json","statements.json","note_map.json","relations.json","annotations.json","复核进度.json")
    protected={directory/name for name in names if name not in allow_names}
    extracted=directory/"extracted_tables.json"
    if extracted.exists():
        protected.update(Path(f["path"]).resolve() for f in load_json(extracted).get("files",[]) if f.get("path"))
    if any(Path(p).resolve() in protected for p in outputs):raise ValueError("输出不能覆盖原件、输入或进度")

def verify_sources(data):
    for source in data.get("meta",{}).get("source_files",[]):
        path=Path(source["path"])
        if not path.is_file() or not source.get("sha256") or fingerprint(path)!=source["sha256"]:
            raise ValueError("原始来源变化或缺失，旧结论已失效："+str(path))

def save_json(path, data):
    save_text(path, json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False, default=_decimal) + "\n")

def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"), parse_float=Decimal)

def review_valid(item):
    review = item.get("review")
    if not isinstance(review, dict):
        return False
    return bool(review.get("agent") and review.get("basis") and review.get("source_fingerprint")
                and isinstance(review.get("source_refs"), list) and review["source_refs"]
                and review.get("check_id") == item.get("check_id")
                and review.get("conclusion") == item.get("status"))

def normalize_result(item):
    item = dict(item)
    item.setdefault("check_id", stable_id({k: item.get(k) for k in ("check_type", "rule_name", "source_location", "target_location", "source_file", "context", "period")}))
    item.setdefault("calculation", {"match": item.get("passed"), "expected": item.get("expected"), "actual": item.get("actual"), "difference": item.get("difference")})
    if item.get("status") not in STATUSES or not review_valid(item):
        item["status"] = "未执行"
    if item["status"] == "通过" and item["calculation"].get("match") is False:
        raise ValueError("计算不一致不能标通过")
    if item["status"] == "通过" and item.get("expected") is not None and item.get("actual") is not None:
        from calculator import check_equal
        calc = check_equal(item["expected"], item["actual"], item["calculation"].get("tolerance", "0.01"))
        if not calc["match"]:
            raise ValueError("实际计算存在差异，不能标通过")
    item["passed"] = item["status"] == "通过"
    item["severity"] = {"确认错误": "error", "待核实": "warning", "未执行": "warning"}.get(item["status"], "info")
    return item

def validate_report(data):
    if not isinstance(data, dict) or not isinstance(data.get("results", []), list):
        raise ValueError("结果格式无效")
    ids = data.get("coverage", {}).get("expected_ids", [])
    if not isinstance(ids, list) or len(ids) != len(set(ids)):
        raise ValueError("覆盖清单无效或重复")
    results = [normalize_result(r) for r in data.get("results", [])]
    actual = [r["check_id"] for r in results]
    if len(actual) != len(set(actual)):
        raise ValueError("检查对象重复")
    missing = set(ids) - set(actual)
    counts = {s: sum(r["status"] == s for r in results) for s in STATUSES}
    counts["未执行"] += len(missing)
    counts["应检"] = len(ids)
    counts["已记录"] = len(results)
    counts["缺少记录"] = len(missing)
    complete = bool(ids) and set(actual) == set(ids) and counts["未执行"] == 0
    counts["完整"] = complete
    if data.get("meta", {}).get("stage") == "final" and not complete:
        raise ValueError("复核未完成：覆盖、来源或终审证据不足")
    data["results"] = results
    return counts
