
import os
from datetime import datetime
from storage import ResultStore
from models import Result

def test_save_and_file_creation(tmp_path):
    store = ResultStore(tmp_path/"attempts.csv")
    r = Result("abc", datetime.utcnow().isoformat(), 7, 10, {"q1": True})
    store.save(r)
    assert os.path.exists(tmp_path/"attempts.csv")
