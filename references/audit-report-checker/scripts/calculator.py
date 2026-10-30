"""确定性财务金额计算；语义及取数由当前agent负责。"""
import argparse
import ast
import json
import re
import unicodedata
from decimal import Decimal, InvalidOperation, getcontext

getcontext().prec = 60
UNITS = {"": Decimal(1), "元": Decimal(1), "千": Decimal(1000), "千元": Decimal(1000), "万": Decimal(10000), "万元": Decimal(10000), "百万": Decimal(1000000), "百万元": Decimal(1000000)}

def parse_number(value):
    if value is None or isinstance(value, bool):
        raise ValueError("缺少金额或金额类型无效")
    if isinstance(value, (int, float, Decimal)):
        try:
            number = Decimal(str(value))
        except InvalidOperation as exc:
            raise ValueError("金额无效") from exc
        if not number.is_finite():
            raise ValueError("金额必须为有限数")
        return number
    if not isinstance(value, str):
        raise ValueError("金额类型无效")
    s = unicodedata.normalize("NFKC", value).strip().replace("−", "-")
    s = re.sub(r"^(?:人民币|￥|¥)\s*", "", s)
    s = re.sub(r" +(?=(?:百万元|万元|千元|百万|万|千|元)\)?$)","",s)
    if re.search(r"\s",s):
        if not re.fullmatch(r"\(?[+-]?\d{1,3}(?: \d{3})+(?:[.,]\d+)?(?:百万元|万元|千元|百万|万|千|元)?\)?",s):raise ValueError("金额分隔存在歧义")
        s=s.replace(" ","")
    if not s:
        raise ValueError("缺少金额")
    negative = s.startswith("(") and s.endswith(")")
    if negative:
        s = s[1:-1]
        if s.startswith(("-", "+")):
            raise ValueError("金额符号重复")
    match = re.fullmatch(r"([+-]?[\d.,]+)(百万元|万元|千元|百万|万|千|元)?", s)
    if not match:
        raise ValueError("无法解析完整金额：" + value)
    digits, unit = match.groups()
    if "," in digits and (digits.rfind(",") > digits.rfind(".") and "." in digits or ("." not in digits and digits.count(",") == 1 and len(digits.rsplit(",", 1)[1]) != 3)):
        if not re.fullmatch(r"[+-]?(?:\d+|\d{1,3}(?:\.\d{3})+),\d+", digits):
            raise ValueError("金额分隔符无效：" + value)
        digits = digits.replace(".", "").replace(",", ".")
    elif not re.fullmatch(r"[+-]?(?:\d+|\d{1,3}(?:,\d{3})+)(?:\.\d+)?", digits):
        raise ValueError("金额分隔符无效：" + value)
    else:
        digits = digits.replace(",", "")
    try:
        result = Decimal(digits) * UNITS[unit or ""]
    except InvalidOperation as exc:
        raise ValueError("金额无效：" + value) from exc
    return -result if negative else result

def amount_in_unit(value,unit):
    if unit not in UNITS:raise ValueError("金额单位未确认")
    raw=re.sub(r"\s+","",unicodedata.normalize("NFKC",str(value)))
    suffix=re.search(r"(百万元|万元|千元|百万|元|万|千)\)?$",raw)
    if suffix and UNITS[suffix.group(1)]!=UNITS[unit]:raise ValueError("内嵌金额单位与声明单位冲突")
    return parse_number(value)*(1 if suffix else UNITS[unit])

def sum_numbers(text):
    if not isinstance(text, str) or not text.strip():
        raise ValueError("缺少求和金额")
    tokens = re.findall(r"\([^)]*\)|（[^）]*）|\S+", text)
    return sum((parse_number(t) for t in tokens), Decimal(0))

def evaluate_expression(expr, values=None):
    if not isinstance(expr, str) or len(expr) > 10000:
        raise ValueError("表达式无效或过长")
    values = values or {}
    try:
        tree = ast.parse(expr, mode="eval")
        if sum(1 for _ in ast.walk(tree)) > 500:
            raise ValueError("表达式过于复杂")
        def evaluate(node):
            if isinstance(node, ast.Expression):
                return evaluate(node.body)
            if isinstance(node, ast.Constant) and type(node.value) in (int, float):
                return parse_number(ast.get_source_segment(expr, node))
            if isinstance(node, ast.Name) and node.id in values:
                return parse_number(values[node.id])
            if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
                v = evaluate(node.operand)
                return -v if isinstance(node.op, ast.USub) else v
            if isinstance(node, ast.BinOp):
                left, right = evaluate(node.left), evaluate(node.right)
                if isinstance(node.op, ast.Add): return left + right
                if isinstance(node.op, ast.Sub): return left - right
                if isinstance(node.op, ast.Mult): return left * right
                if isinstance(node.op, ast.Div): return left / right
            raise ValueError("表达式含不支持的操作")
        result = evaluate(tree)
        if not result.is_finite():
            raise ValueError("计算结果无效")
        return result
    except (SyntaxError, ArithmeticError, RecursionError) as exc:
        raise ValueError("表达式计算失败：" + str(exc)) from exc

def check_equal(value1, value2, tolerance=Decimal("0.01")):
    tol = parse_number(tolerance)
    if tol < 0:
        raise ValueError("容差不能为负数")
    try:
        a, b = parse_number(value1), parse_number(value2)
    except ValueError as exc:
        return {"match": False, "diff": None, "error": str(exc), "value1_parsed": None, "value2_parsed": None}
    difference = abs(a - b)
    return {"match": difference <= tol, "diff": difference, "value1_parsed": a, "value2_parsed": b}

def reconcile(beginning, increase, decrease, ending, tolerance=Decimal("0.01")):
    try:
        a, b, c, d = [parse_number(v) for v in (beginning, increase, decrease, ending)]
    except ValueError as exc:
        return {"match": False, "diff": None, "error": str(exc), "calculated_ending": None, "actual_ending": None}
    expected = a + b - c
    result = check_equal(expected, d, tolerance)
    return {"match": result["match"], "diff": result["diff"], "calculated_ending": expected, "actual_ending": d}

def main():
    parser = argparse.ArgumentParser(description="本地财务金额验算")
    parser.add_argument("-f", "--format", choices=["text", "json"], default="text")
    sub = parser.add_subparsers(dest="command", required=True)
    for name, fields in [("sum", ["numbers"]), ("expr", ["expression"]), ("check", ["value1", "value2"]), ("reconcile", ["beginning", "increase", "decrease", "ending"])]:
        p = sub.add_parser(name)
        p._negative_number_matcher = re.compile(r"^-\d[\d,.]*$")
        for field in fields: p.add_argument(field)
        if name in ("check", "reconcile"): p.add_argument("-t", "--tolerance", default="0.01")
    args = parser.parse_args()
    try:
        if args.command == "sum": result = {"total": sum_numbers(args.numbers)}
        elif args.command == "expr": result = {"result": evaluate_expression(args.expression)}
        elif args.command == "check": result = check_equal(args.value1, args.value2, args.tolerance)
        else: result = reconcile(args.beginning, args.increase, args.decrease, args.ending, args.tolerance)
        print(json.dumps(result, ensure_ascii=False, default=lambda v: format(v, "f")) if args.format == "json" else str(result))
        return 1 if result.get("error") else 0
    except ValueError as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
