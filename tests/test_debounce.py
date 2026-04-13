import pytest
import time
from src.infrastructure.repository import _write_json_debounced, _read_json, _flush_pending_writes, DATA_DIR
import os

def test_debounced_write():
    file_name = "test_debounce.json"
    path = os.path.join(DATA_DIR, file_name)
    if os.path.exists(path):
        os.remove(path)
        
    # Write 1 (should be immediate)
    _write_json_debounced(file_name, {"step": 1})
    data1 = _read_json(file_name)
    assert data1["step"] == 1
    
    # Write 2 (should be buffered because time < 0.5s)
    _write_json_debounced(file_name, {"step": 2})
    # _read_json calls flush internally, so it will actually flush it
    # Let's bypass _read_json to check if it's buffered
    import json
    with open(path, "r") as f:
        raw_data = json.load(f)
    assert raw_data["step"] == 1 # still 1 on disk!
    
    # Now use _read_json which flushes
    data2 = _read_json(file_name)
    assert data2["step"] == 2 # flushed!
    
    # Write 3
    _write_json_debounced(file_name, {"step": 3})
    # Wait > 0.5s
    time.sleep(0.6)
    _write_json_debounced(file_name, {"step": 4})
    # Because 0.6 > 0.5, Write 4 will trigger a flush of Write 4 (wait, write 4 triggers flush of what's in pending, which is write 4)
    with open(path, "r") as f:
        raw_data2 = json.load(f)
    assert raw_data2["step"] == 4
    
    if os.path.exists(path):
        os.remove(path)

