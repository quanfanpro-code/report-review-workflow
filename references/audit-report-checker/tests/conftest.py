"""本机复核测试：产物保留，不访问外部模型。"""
import importlib
import socket
import sys
import uuid
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
RUN = ROOT / "docs" / "reviews" / ("验证运行_" + uuid.uuid4().hex[:12])
RUN.mkdir(parents=True)

@pytest.fixture
def 验证目录():
    path = RUN / uuid.uuid4().hex[:12]
    path.mkdir()
    return path

@pytest.fixture
def 技能根目录():
    return ROOT

@pytest.fixture(autouse=True)
def 禁止外部调用(monkeypatch):
    def denied(*args, **kwargs):
        raise AssertionError("测试禁止网络连接")
    monkeypatch.setattr(socket.socket, "connect", denied)
    original = Path.open
    def guarded(path, *args, **kwargs):
        if ".deepseek" in path.parts:
            raise AssertionError("测试禁止读取外部模型配置")
        return original(path, *args, **kwargs)
    monkeypatch.setattr(Path, "open", guarded)

@pytest.fixture
def 契约():
    return importlib.import_module("复核契约")
