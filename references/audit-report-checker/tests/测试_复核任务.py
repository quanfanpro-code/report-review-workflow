import importlib
from pathlib import Path
import pytest
from 复核契约 import save_json,save_text

def prepare(path,large=False):
    path.mkdir(parents=True)
    tables=[{"id":i,"source_file":"报告.docx","headers":["项目","金额"],"rows":[["业务"+str(i),"100"],["合计","100"]]} for i in range(1000 if large else 2)]
    if large:tables.append({"id":1001,"source_file":"报告.docx","headers":["项目","金额"],"rows":[["大表明细"+str(i),str(i)] for i in range(3000)]})
    text="资料正文：核对期间、主体、金额与披露。"*(150*100 if large else 20)
    save_json(path/"extracted_tables.json",{"schema_version":2,"sources":["报告.docx"],"tables":tables,"segments":[{"id":0,"source_file":"报告.docx","text":text}],"pending":[]})
    save_text(path/"report.md",text)
    save_json(path/"relations.json",{"checks":[],"not_applicable_basis":"本测试只核对队列行为，不作跨表业务结论"})
    return path

def reply(state,batch,status="不适用"):
    objects={o["check_id"]:o for o in state["objects"]}
    return {"batch_id":batch["batch_id"],"source_fingerprint":state["source_fingerprint"],"results":[{"check_id":cid,"status":status,"description":"合成测试资料，已逐项检查其适用性","review":{"agent":"当前agent","check_id":cid,"source_fingerprint":state["source_fingerprint"],"conclusion":status,"basis":"测试样例不对应真实审计报告，已核对原文内容","source_refs":[{"check_id":cid,"quote":objects[cid]["material"][:30]}]}} for cid in batch["check_ids"]]}

def test_两档对象一致与大材料完整(验证目录,monkeypatch):
    task=importlib.import_module("复核任务")
    a=prepare(验证目录/"小档",True);b=prepare(验证目录/"大档",True)
    small=task.init_review(a,"128k","deep");large=task.init_review(b,"1m","deep")
    assert set(small["coverage"]["expected_ids"])==set(large["coverage"]["expected_ids"])
    assert len(task.next_batch(a)["material"])<=20000
    assert len(task.next_batch(b)["material"])<=80000
    assert any(o.get("table_id")==1001 for o in small["objects"])
    parts=sorted((o["span"] for o in small["objects"] if o.get("kind")=="text"))
    assert parts[0][0]==0
    assert all(left[1]>=right[0] for left,right in zip(parts,parts[1:]))
    assert parts[-1][1]==len(task.load_json(a/"extracted_tables.json")["segments"][0]["text"])
    raw=task.load_json(a/"extracted_tables.json")["tables"][-1]
    spans=sorted(o["row_range"] for o in small["objects"] if o.get("table_id")==1001)
    assert spans[0][0]==0 and spans[-1][1]==len(raw["rows"])
    assert all(left[1]==right[0] for left,right in zip(spans,spans[1:]))
    for state,folder,limit in ((small,a,20000),(large,b,80000)):
        monkeypatch.setattr(task,"_load",lambda directory:state)
        seen=[]
        while True:
            batch=task.next_batch(folder)
            if not batch["check_ids"]:break
            assert len(batch["material"])<=limit
            seen.extend(batch["check_ids"]);state["attempted_ids"].extend(batch["check_ids"])
        assert len(seen)==len(set(seen))==len(state["objects"])

def test_批次幂等续作且未完成不汇总(验证目录):
    task=importlib.import_module("复核任务");folder=prepare(验证目录/"输入")
    state=task.init_review(folder,"128k","standard")
    with pytest.raises(ValueError,match="未完成"):
        task.finalize_results(folder,验证目录/"结果.json")
    batch=task.next_batch(folder);answer=reply(state,batch)
    result=task.submit_batch(folder,answer)
    assert task.submit_batch(folder,answer)==result
    for _ in range(100):
        batch=task.next_batch(folder)
        if not batch["check_ids"]:break
        task.submit_batch(folder,reply(state,batch))
    coverage=task.audit_coverage(folder)
    assert coverage["未执行"]==0 and coverage["完整"]
    final=task.finalize_results(folder,验证目录/"结果.json")
    assert final["meta"]["stage"]=="final"

def test_来源变化拒绝旧结论(验证目录):
    task=importlib.import_module("复核任务");folder=prepare(验证目录/"输入")
    state=task.init_review(folder,"128k","deep");batch=task.next_batch(folder)
    save_text(folder/"report.md","已修改的原文")
    with pytest.raises(ValueError,match="变化|失效"):
        task.submit_batch(folder,reply(state,batch))

def test_虚构引文不能终审(验证目录):
    task=importlib.import_module("复核任务");folder=prepare(验证目录/"输入")
    state=task.init_review(folder,"128k","deep");batch=task.next_batch(folder);answer=reply(state,batch)
    answer["results"][0]["review"]["source_refs"][0]["quote"]="原文不存在的终审依据"
    with pytest.raises(ValueError,match="引文|原文"):
        task.submit_batch(folder,answer)

def test_文字终审不能掩盖计算不平(验证目录):
    task=importlib.import_module("复核任务");folder=prepare(验证目录/"输入")
    state=task.init_review(folder,"128k","deep");batch=task.next_batch(folder);answer=reply(state,batch)
    kinds={o["check_id"]:o["kind"] for o in state["objects"]}
    for r in answer["results"]:
        if kinds[r["check_id"]]=="table":
            r["status"]="通过";r["review"]["conclusion"]="通过"
            r["annotation"]={"vertical":[{"target_row":1,"col":1,"operands":[{"row":0,"op":"-"}]}]}
    with pytest.raises(ValueError,match="计算|结构|范围"):
        task.submit_batch(folder,answer)

def test_规则版本变化旧状态失效(验证目录,monkeypatch):
    task=importlib.import_module("复核任务");folder=prepare(验证目录/"输入")
    state=task.init_review(folder,"128k","deep");batch=task.next_batch(folder)
    monkeypatch.setattr(task,"POLICY_VERSION","规则已变化",raising=False)
    with pytest.raises(ValueError,match="变化|失效"):
        task.submit_batch(folder,reply(state,batch))
