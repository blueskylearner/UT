
import csv
from typing import List, Tuple, Dict
from models import Question

class QuizEngine:
    """Core quiz logic: state, navigation, scoring."""
    def __init__(self, questions: List[Question]) -> None:
        self._questions = questions
        self._index = 0
        self._answers: Dict[str, str] = {}

    @staticmethod
    def load_from_csv(path: str) -> List[Question]:
        """Load a question bank from CSV (id,prompt,options|;|,answer,topic)."""
        out: List[Question] = []
        with open(path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                opts = [o.strip() for o in row["options"].split("|;|")] if row["options"] else []
                out.append(Question(row["id"], row["prompt"], opts, row["answer"], row["topic"]))
        return out

    def current(self) -> Question:
        return self._questions[self._index]

    def submit(self, answer: str) -> None:
        self._answers[self.current().id] = answer

    def next(self) -> bool:
        if self._index < len(self._questions) - 1:
            self._index += 1
            return True
        return False

    def prev(self) -> bool:
        if self._index > 0:
            self._index -= 1
            return True
        return False

    def score(self) -> Tuple[int, Dict[str, bool]]:
        correct = {q.id: (self._answers.get(q.id, "").strip().lower() == q.answer.strip().lower())
                   for q in self._questions}
        return sum(correct.values()), correct

    def reset(self) -> None:
        self._index = 0
        self._answers.clear()
