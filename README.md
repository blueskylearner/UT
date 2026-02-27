# United Teaching Staff Knowledge Quiz 🧠🎓 (Tkinter)

A Python/Tkinter desktop quiz for **induction** and **CPD** at United Teaching (UT) to reinforce critical organisational knowledge **with a focus on safeguarding** 🛡️.  
The app evidences professional software practice: **GUI**, **persistence**, **OOP**, **validation**, **tests**, and **CI**.

**Python version tested:** 3.11 (compatible with 3.9+) 🐍

---

## 1️⃣ Introduction 📘

United Teaching supports teacher training and ongoing professional development across a network of schools. New joiners and staff moving roles must quickly internalise key organisational knowledge—especially safeguarding duties (e.g., how to record a concern, who the DSL is, when to call 999, information sharing, child‑on‑child abuse guidance).  
A short, interactive quiz turns policy reading into an **active recall** experience 🧠, surfaces misconceptions early, and produces a minimal **audit trail** of engagement for the Digital Lead ✅.

This MVP is an offline Tkinter app. Staff enter a work email or initials, complete a short mixed‑format quiz (MCQ and short‑answer), receive immediate feedback, and results are stored locally to CSV using pseudonymisation 🔒. Logic is separated from UI so it’s **unit‑testable**. A light Admin view allows export/housekeeping 🧹.

---

## 2️⃣ Design 🎨

### 📷 Wireframe Overview
<img src=wireframe.png" alt="Wireframe" width="100">
**Figure 1 — Early wireframe illustrating user flow and screen structure.**
## Figure 1 presents the wireframe developed during the early design stage of the quiz application. The purpose of the wireframe was to conceptualise the intended user journey, from initial identification through to question completion and final confirmation. Each screen is depicted as a white interaction card placed within a light‑grey container, providing a clear visual boundary and supporting a consistent, structured interface. The inclusion of arrows between screens illustrates the intended flow of navigation and user progression through the application.
The wireframe was produced prior to implementation and served as a planning tool for determining screen layout, information hierarchy, and input requirements. It identifies the placement of key interface components—such as text fields, radio buttons, navigation controls, and instructional text—and demonstrates how these elements operate together to support user interaction. In particular, the wireframe maps the validation sequence (e.g., entering a name before beginning the quiz), the backward‑and‑forward navigation during question answering, and the transition to the results screen once all responses have been submitted.
Although the wireframe does not reflect final typography, colour palette, or stylistic refinements, it establishes the core structural and functional characteristics of the application. Its primary aim is not aesthetic detail but the articulation of **workflow**, **usability**, and **logical sequencing**. By outlining each screen in a simplified, low‑fidelity form, the wireframe ensures that design decisions focus on clarity, accessibility, and effective information flow.
From an interaction‑design perspective, the wireframe also contributes to early identification of potential usability considerations. The separation of screens encourages cognitive simplicity, while the uniform card layout supports predictable navigation. Controls such as **Back**, **Next**, and **Exit** are positioned consistently across screens, reducing user load and ensuring straightforward task completion. The use of input fields and selection components early on also reinforces data‑entry expectations and maintains coherence throughout the quiz experience.
Overall, the wireframe acts as a blueprint for the eventual Tkinter GUI. It ensures that the implemented interface is aligned with the intended pedagogical purpose of the quiz—namely, guiding the user through a structured, linear set of questions, validating input appropriately, and presenting a clear conclusion to the activity. By focusing on user interaction, screen sequence, and layout clarity, the wireframe underpins the development of a coherent and intuitive application.

### 🧭 User roles & journey
- **Staff:** Launch → identify (email/initials) → take quiz → view score & topic hints → retry.
- **Admin:** Open Admin (Ctrl+Shift+A) → export `attempts.csv` → rotate hashing salt.

### ⚙️ Functional requirements
- Tkinter GUI for input, quiz navigation and export.
- Persistent storage of attempts in CSV; question bank in CSV.
- OOP design separating models, engine, storage.
- Docstrings for maintainability.
- Input validation & exception handling.
- Testable logic with unit tests.

### 📐 Non‑functional requirements
- **Usability & accessibility**: keyboard navigation, sensible focus, scalable fonts ♿
- **Reliability**: atomic writes, defensive error handling 🛡️
- **Privacy/Security**: minimal PII; one‑way hashing of identifiers with a salt 🔐
- **Performance/Portability**: fast startup on school laptops; Python 3.9+; PyInstaller packaging for Windows ⚡

### 🛠️ Tech stack
- **Language:** Python 3.11
- **GUI:** Tkinter (stdlib)
- **Data:** CSV (questions, attempts)
- **Tests:** `pytest` (+ coverage)
- **CI:** GitHub Actions (3.9–3.12)
- **Packaging:** PyInstaller (optional)

### 🗂️ Code structure & Desgin 

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



### 🧱 Class design (overview)
- **Question:** immutable question object (id, prompt, options, answer, topic)
- **QuizEngine:** navigation + scoring; loads CSV question bank
- **Result:** attempt result (user_hash, timestamp, score, total, per‑item correctness)
- **ResultStore:** atomic CSV append & simple JSON serialisation of detail
- **validators:** pure functions `is_valid_email`, `non_empty`

---

## 3️⃣ Development 🛠️

### Key modules (excerpts)

**`models.py`** 🧩
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

    engine.py 🔁
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
        correct = {
            q.id: (self._answers.get(q.id, '').strip().lower()
                   == q.answer.strip().lower())
            for q in self._questions
        }
        return sum(correct.values()), correct

        validators.py 🔍
        import re
_EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[\w.-]+\.[A-Za-z]{2,}$")

def is_valid_email(s: str) -> bool: return bool(_EMAIL_RE.match(s or ''))

def non_empty(s: str) -> bool: return bool((s or '').strip())

storage.py 💾
import csv, os, tempfile, hashlib, json

def hash_identifier(raw: str, salt: str) -> str:
    h = hashlib.sha256()
    h.update((salt + '|' + (raw or '')).encode('utf-8'))
    return h.hexdigest()

class ResultStore:
    def save(self, r: Result) -> None:
        # atomic append via temp file + replace
        ...
        app.py organises three frames: WelcomeFrame (identity + consent), QuizFrame (items with Next/Back) and ResultFrame (score + per‑item ticks ✅).
A simple Admin action (menu or Ctrl+Shift+A) points admins to the storage location and is the hook for future exports.
Question content
The starter questions.csv focuses on safeguarding essentials (DSL identity, CPOMS recording, immediate referral for significant harm, FGM duty to report, 10‑day CME threshold, Prevent emergency action, information‑sharing basis under DPA 2018, zero‑tolerance approach to child‑on‑child abuse, robust record keeping, LADO role, etc.).
Please review against your latest policy before deployment. 🛡️

4️⃣ Testing 🧪

Strategy

Unit tests: deterministic logic in validators, scoring and storage append ✔️
Integration tests: minimal end‑to‑end path via QuizEngine with a tiny fixture set 🔗
Manual tests: GUI flows (validation dialogs, navigation, state persistence) 🖱️
CI: GitHub Actions matrix (3.9–3.12) executes pytest on push/PR 🔄

Sample results
$ pytest -q
3 passed in 0.30s
Add screenshots of passing tests to docs/ui/ if required by your submission pack. 📷
5️⃣ Documentation 📚
👥 User (staff)

Launch the app → enter work email (or initials) → tick consent → Start.
Answer questions (radio buttons or short text). Use Tab/Shift+Tab for keyboard nav ⌨️.
View score and feedback; optionally Retry 🔁.

🗂️ Admin (Digital Lead)

Open Admin (Ctrl+Shift+A) to see storage location (./data/attempts.csv).
Export or analyse in your BI tool of choice; rotate the hashing salt before a new cycle 🔑.
👨‍💻 Developer
git clone <your-repo>
cd ut-quiz
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python app.py
pytest -q
CI file: .github/workflows/ci.yml (Actions → Tests on PRs and pushes) 🔄.
Packaging (optional):
pyinstaller --name "UT-Quiz" --onefile app.py
📦
6️⃣ Evaluation ⭐
Went well 🚀
Clean separation of logic/UI for testability
Privacy‑aware storage
Fast, offline operation
CI from day one
Could be improved 🔧
In‑app question editor
Richer analytics dashboard
SQLite for stronger integrity at scale
Accessibility enhancements (screen‑reader roles, contrast themes)
Secure admin secret management
Roadmap 🗺️
Versioned question banks per term
OneDrive/SharePoint export
Power BI template
Internationalisation
Extended admin controls
