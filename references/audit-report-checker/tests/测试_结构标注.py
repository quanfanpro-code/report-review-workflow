import pytest
import run_check as checks

@pytest.mark.parametrize("headers,row", [(["项目","期初余额","本期增加","本期减少","期末余额"],["薪酬","100","20","10","999"]),(["项目","原价","累计折旧","减值准备","账面价值"],["设备","100","20","10","999"])])
def test_横加不能因列名冲突而漏检(headers,row):
    result=checks.code_horizontal_check({"id":1,"headers":headers,"rows":[row]})
    assert result and result[0]["calculation"]["match"] is False

def test_零合计仍验算():
    result=checks.code_vertical_check({"id":1,"headers":["项目","金额"],"rows":[["甲","1"],["合计","0.00"]]})
    assert result and result[0]["calculation"]["match"] is False

def test_小计只用自己的明细():
    table={"id":1,"headers":["项目","金额"],"rows":[["甲","2"],["小计甲","2"],["乙","3"],["小计乙","3"]]}
    ann={"vertical":[{"target_row":1,"col":1,"operands":[{"row":0,"op":"+"}]},{"target_row":3,"col":1,"operands":[{"row":2,"op":"+"}]}]}
    result=checks.execute_annotations(table,ann)
    assert len(result)==2 and all(r["calculation"]["match"] for r in result)

@pytest.mark.parametrize("bad",[-1,10,"1",True])
def test_索引必须合法(bad):
    with pytest.raises(ValueError,match="索引"):
        checks.execute_annotations({"id":1,"headers":["项目","金额"],"rows":[["甲","1"]]}, {"vertical":[{"target_row":bad,"col":1,"operands":[{"row":0,"op":"+"}]}]})

def test_横加只执行声明行():
    table={"id":1,"headers":["项目","原值","准备","净值"],"rows":[["甲","100","10","90"],["注释","文本","文本","文本"]]}
    ann={"horizontal":[{"rows":[0],"operands":[{"col":1,"op":"+"},{"col":2,"op":"-"}],"result_col":3}]}
    result=checks.execute_annotations(table,ann)
    assert len(result)==1 and result[0]["calculation"]["match"] is True

def test_重复金额引用不得重复加():
    with pytest.raises(ValueError,match="重复"):
        checks.execute_annotations({"id":1,"rows":[["甲","1"],["合计","2"]]}, {"vertical":[{"target_row":1,"col":1,"operands":[{"row":0,"op":"+"},{"row":0,"op":"+"}]}]})

def test_百分比不能冒充金额():
    with pytest.raises(ValueError,match="比例|百分比"):
        checks.execute_annotations({"id":1,"headers":["项目","金额","占比%","合计"],"rows":[["甲","90","10","100"]]}, {"horizontal":[{"rows":[0],"operands":[{"col":1,"op":"+"},{"col":2,"op":"+"}],"result_col":3}]})

def test_收入附注不能被当四表跳过():
    table={"id":0,"name":"营业收入附注","headers":["项目","金额"],"rows":[["主营业务收入","100"],["营业收入合计","99"]]}
    assert checks.code_vertical_check(table)

def test_净值横加不能跨期混算():
    table={"id":1,"headers":["项目","期末账面余额","期初坏账准备","期末账面价值"],"rows":[["甲","100","10","90"]]}
    ann={"horizontal":[{"rows":[0],"operands":[{"col":1,"op":"+"},{"col":2,"op":"-"}],"result_col":3}]}
    with pytest.raises(ValueError,match="期间|时点"):
        checks.execute_annotations(table,ann)
def test_万元表注统一元后验算():
    import run_check as run
    table={"id":0,"unit":"万元","rows":[["甲","1"],["乙","2"],["合计","3.001"]]}
    result=run.execute_annotations(table,{"vertical":[{"target_row":2,"col":1,"operands":[{"row":0,"op":"+"},{"row":1,"op":"+"}]}]})[0]
    assert result["calculation"]["match"] is False and result["difference"]==10

