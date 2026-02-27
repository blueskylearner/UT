import os
from datetime import datetime, UTC
from storage import ResultStore
from models import Result


def test_save_and_file_creation(tmp_path):
    store = ResultStore(os.path.join(tmp_path, "attempts.csv"))
    r = Result("abc", datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z"), 7, 10, {"q1": True})
    store.save(r)
    assert os.path.exists(os.path.join(tmp_path, "attempts.csv"))