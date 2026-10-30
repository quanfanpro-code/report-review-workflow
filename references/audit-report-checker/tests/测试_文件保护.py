from pathlib import Path
import pytest
import apply_manifest
from 复核契约 import save_json

def test_取数输出不能覆盖原件(验证目录):
    source=验证目录/"原件.docx";source.write_bytes(b"original")
    manifest=验证目录/"manifest.json"
    save_json(manifest,{"files":{"原件.docx":{"loader":"docx"}},"statements_map":{}})
    with pytest.raises(SystemExit):
        apply_manifest.main([str(manifest),"-o",str(source)])
    assert source.read_bytes()==b"original"
