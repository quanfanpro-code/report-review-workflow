"""README 可读性校验：通俗文档的最低门槛。"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"


def test_readme_exists():
    assert README.exists(), "缺 README.md"


def test_readme_has_emoji():
    text = README.read_text(encoding="utf-8")
    emoji = re.findall(r"[\U0001F300-\U0001FAFF☀-➿]", text)
    assert len(emoji) >= 5, f"README emoji 少于 5 个，仅 {len(emoji)} 个"


def test_readme_no_code_fence():
    text = README.read_text(encoding="utf-8")
    assert "```" not in text, "README 含代码围栏，违反零代码要求"


def test_readme_four_sections():
    text = README.read_text(encoding="utf-8")
    for title in ("使用方式", "运行逻辑", "输入要求", "输出内容"):
        assert title in text, f"README 缺小节：{title}"
