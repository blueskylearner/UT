
import csv, os, tempfile, hashlib, json
from models import Result

def hash_identifier(raw: str, salt: str) -> str:
    """One-way SHA-256 hash to pseudonymise user identifiers."""
    h = hashlib.sha256()
    h.update((salt + "|" + (raw or "")).encode("utf-8"))
    return h.hexdigest()

class ResultStore:
    def __init__(self, path: str) -> None:
        self.path = path
        self.fieldnames = ["timestamp_iso", "user_hash", "score", "total", "details_json"]

    def save(self, r: Result) -> None:
        """Append a row to CSV atomically; create file with header if missing."""
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        row = {
            "timestamp_iso": r.timestamp_iso,
            "user_hash": r.user_hash,
            "score": r.score,
            "total": r.total,
            "details_json": json.dumps(r.details, ensure_ascii=False),
        }
        mode = "a" if os.path.exists(self.path) else "w"
        with tempfile.NamedTemporaryFile("w", delete=False, encoding="utf-8", newline="") as tmp:
            writer = csv.DictWriter(tmp, fieldnames=self.fieldnames)
            if mode == "w":
                writer.writeheader()
            writer.writerow(row)
            tmp_name = tmp.name
        os.replace(tmp_name, self.path)
