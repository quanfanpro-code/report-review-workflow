from decimal import Decimal
import pytest
from calculator import parse_number, sum_numbers, check_equal, reconcile, evaluate_expression

@pytest.mark.parametrize("text,want", [("100 -20", "80"), ("100 (20)", "80"), ("1万元 2万元", "30000"), ("-1,234.56 34.56", "-1200"), ("（２０） 100", "80")])
def test_求和保留符号单位(text, want):
    assert sum_numbers(text) == Decimal(want)

@pytest.mark.parametrize("text,want", [("1,234.56", "1234.56"), ("1.234,56", "1234.56"), ("（1，234.56）", "-1234.56"), ("1千元", "1000"), ("1百万元", "1000000"), ("１２３４．５６", "1234.56"), ("-1,234", "-1234")])
def test_金额格式(text, want):
    assert parse_number(text) == Decimal(want)

@pytest.mark.parametrize("text", ["附注12", "12O.50", "", None, True, "NaN", "Infinity", "1.2.3", "10%", "--1"])
def test_无效数据不冒充金额(text):
    with pytest.raises(ValueError):
        parse_number(text)

def test_大金额保留分():
    assert parse_number("9999999999999999.99") + Decimal("0.01") == Decimal("10000000000000000.00")

def test_精确容差():
    assert check_equal("1.00", "1.01")["match"] is True
    assert check_equal("1.00", "1.0100001")["match"] is False
    with pytest.raises(ValueError):
        check_equal("1", "1", -1)

def test_缺少变动金额不是零():
    result = reconcile("100", "", "10", "90")
    assert result["match"] is False and result.get("error")

def test_表达式变量与精度():
    assert evaluate_expression("a+b", {"a": Decimal("0.1"), "b": Decimal("0.2")}) == Decimal("0.3")
    with pytest.raises(ValueError):
        evaluate_expression("__import__('os')")

def test_求和非法余文不能忽略():
    with pytest.raises(ValueError):
        sum_numbers("100 待核实20")
def test_声明单位与内嵌单位只换算一次():
    from calculator import amount_in_unit
    assert amount_in_unit("1万元","万元")==10000
    assert amount_in_unit("（1万元）","万元")==-10000
    assert amount_in_unit("1","万元")==10000
    with pytest.raises(ValueError,match="单位"):
        amount_in_unit("1万元","元")

