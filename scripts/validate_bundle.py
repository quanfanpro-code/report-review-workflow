"""一键完整性校验：转发到 tests/test_bundle.py 的断言并汇总结果。"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    r = subprocess.run([sys.executable, "-m", "pytest",
                        str(ROOT / "tests/test_bundle.py"), "-v"], cwd=ROOT)
    return r.returncode


if __name__ == "__main__":
    sys.exit(main())
