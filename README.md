
# United Teaching Staff Knowledge Quiz (Tkinter)

> A Python/Tkinter desktop quiz for induction and CPD at United Teaching (UT) to reinforce critical organisational knowledge (with a focus on **safeguarding**). The app evidences professional software practice: GUI, persistence, OOP, validation, tests and CI.

**Python version tested:** 3.11 (compatible with 3.9+)

---

## 1) Introduction
United Teaching supports teacher training and ongoing professional development across a network of schools. New joiners and staff moving roles must quickly internalise key organisational knowledge—especially safeguarding duties (e.g., how to record a concern, who the DSL is, when to call 999, information sharing, child‑on‑child abuse guidance). A short, interactive quiz turns policy reading into an **active recall** experience, surfaces misconceptions early, and produces a minimal audit trail of engagement for the Digital Lead.

This MVP is an **offline Tkinter app**. Staff enter a work email or initials, complete a short mixed‑format quiz (MCQ and short‑answer), receive immediate feedback, and results are stored locally to CSV using pseudonymisation. Logic is separated from UI so it’s **unit‑testable**. A light **Admin** view allows export/housekeeping.

---

## 2) Design

### User roles & journey
- **Staff:** Launch → identify (email/initials) → take quiz → view score & topic hints → retry.
- **Admin:** Open Admin (Ctrl+Shift+A) → export `attempts.csv` → rotate hashing salt.

### Functional requirements
1. Tkinter GUI for input, quiz navigation and export.
2. Persistent storage of attempts in CSV; question bank in CSV.
3. OOP design separating models, engine, storage.
4. Docstrings for maintainability.
5. Input validation & exception handling.
6. Testable logic with unit tests.

### Non‑functional requirements
- **Usability & accessibility:** keyboard navigation, sensible focus, scalable fonts.
- **Reliability:** atomic writes, defensive error handling.
- **Privacy/Security:** minimal PII; one‑way hashing of identifiers with a salt.
- **Performance/Portability:** fast startup on school laptops; Python 3.9+; PyInstaller packaging for Windows.

### Tech stack
- **Language:** Python 3.11
- **GUI:** Tkinter (stdlib)
- **Data:** CSV (questions, attempts)
- **Tests:** pytest (+ coverage)
- **CI:** GitHub Actions (3.9–3.12)
- **Packaging:** PyInstaller (optional)

### Code structure
```
ut-quiz/
├─ app.py                  # Tkinter frames and routing
├─ engine.py               # QuizEngine (logic)
├─ models.py               # Data classes
├─ storage.py              # CSV persistence + hashing
├─ validators.py           # Pure validation functions
├─ data/
│  ├─ questions.csv        # Question bank (policy‑aligned)
│  └─ attempts.csv         # Created after first run
├─ tests/
│  ├─ test_engine.py
│  ├─ test_storage.py
│  └─ test_validators.py
└─ .github/workflows/ci.yml
```

### Class design (overview)
- `Question`: immutable question object (id, prompt, options, answer, topic)
- `QuizEngine`: navigation + scoring; loads CSV question bank
- `Result`: attempt result (user_hash, timestamp, score, total, per‑item correctness)
- `ResultStore`: atomic CSV append & simple JSON serialisation of detail
- `validators`: pure functions `is_valid_email`, `non_empty`

---

## 3) Development

### Key modules (excerpts)

`models.py`
```python
from dataclasses import dataclass
from typing import List, Dict

@dataclass(frozen=True)
class Question:
    """Immutable representation of a single quiz item."""
    id: str
    prompt: str
    options: List[str]  # empty list for short-answer
    answer: str
    topic: str

@dataclass
class Result:
    """A quiz attempt result."""
    user_hash: str
    timestamp_iso: str
    score: int
    total: int
    details: Dict[str, bool]  # question_id -> correctness
```

`engine.py`
```python
class QuizEngine:
    def __init__(self, questions: list[Question]) -> None:
        self._questions = questions
        self._index = 0
        self._answers: dict[str, str] = {}

    @staticmethod
    def load_from_csv(path: str) -> list[Question]:
        ...

    def current(self) -> Question: ...
    def submit(self, answer: str) -> None: ...
    def next(self) -> bool: ...
    def prev(self) -> bool: ...

    def score(self) -> tuple[int, dict[str, bool]]:
        correct = {q.id: (self._answers.get(q.id, '').strip().lower() == q.answer.strip().lower())
                   for q in self._questions}
        return sum(correct.values()), correct
```

`validators.py`
```python
import re
_EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[\w.-]+\.[A-Za-z]{2,}$")

def is_valid_email(s: str) -> bool: return bool(_EMAIL_RE.match(s or ''))

def non_empty(s: str) -> bool: return bool((s or '').strip())
```

`storage.py`
```python
import csv, os, tempfile, hashlib, json

def hash_identifier(raw: str, salt: str) -> str:
    h = hashlib.sha256(); h.update((salt + '|' + (raw or '')).encode('utf-8'))
    return h.hexdigest()

class ResultStore:
    def save(self, r: Result) -> None:
        # atomic append via temp file + replace
        ...
```

`app.py` organises three frames: `WelcomeFrame` (identity + consent), `QuizFrame` (items with Next/Back) and `ResultFrame` (score + per‑item ticks). A **simple Admin** action (menu or Ctrl+Shift+A) points admins to the storage location and is the hook for future exports.

### Question content
The starter `questions.csv` focuses on **safeguarding essentials** (DSL identity, CPOMS recording, immediate referral for significant harm, FGM duty to report, 10‑day CME threshold, Prevent emergency action, information‑sharing basis under DPA 2018, zero‑tolerance approach to child‑on‑child abuse, robust record keeping, LADO role, etc.). Please review against your latest policy before deployment.

---

## 4) Testing

### Strategy
- **Unit tests**: deterministic logic in validators, scoring and storage append.
- **Integration tests**: minimal end‑to‑end path via `QuizEngine` with a tiny fixture set.
- **Manual tests**: GUI flows (validation dialogs, navigation, state persistence).
- **CI**: GitHub Actions matrix (3.9–3.12) executes `pytest` on push/PR.

### Sample results
```
$ pytest -q
3 passed in 0.30s
```
Add screenshots of passing tests to `docs/ui/` if required by your submission pack.

---

## 5) Documentation

### User (staff)
1. Launch the app → enter **work email** (or initials) → tick consent → **Start**.
2. Answer questions (radio buttons or short text). Use **Tab/Shift+Tab** for keyboard nav.
3. View **score** and feedback; optionally **Retry**.

### Admin (Digital Lead)
- Open **Admin** (Ctrl+Shift+A) to see storage location (`./data/attempts.csv`).
- Export or analyse in your BI tool of choice; rotate the hashing salt before a new cycle.

### Developer
```bash
git clone <your-repo>
cd ut-quiz
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python app.py
pytest -q
```
CI file: `.github/workflows/ci.yml` (Actions → Tests on PRs and pushes).

Packaging (optional): `pyinstaller --name "UT-Quiz" --onefile app.py`

---

## 6) Evaluation
**Went well**: clean separation of logic/UI for testability; privacy‑aware storage; fast, offline operation; CI from day one.

**Could be improved**: in‑app question editor; richer analytics dashboard; SQLite for stronger integrity at scale; accessibility enhancements (screen‑reader roles, contrast themes); secure admin secret management.

**Roadmap**: versioned question banks per term; OneDrive/SharePoint export; Power BI template; internationalisation; extended admin controls.
