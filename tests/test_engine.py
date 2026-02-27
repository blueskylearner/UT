
from models import Question
from engine import QuizEngine

def make_engine():
    qs = [
        Question("q1","What is DSL?",["Direct Safeguarding Lead","Designated Safeguarding Lead"],"Designated Safeguarding Lead","Safeguarding"),
        Question("q2","GDPR requires data to be ____.",["encrypted","public"],"encrypted","GDPR"),
    ]
    return QuizEngine(qs)

def test_scoring():
    e = make_engine()
    e.submit("Designated Safeguarding Lead")
    e.next()
    e.submit("encrypted")
    score, detail = e.score()
    assert score == 2
    assert detail["q1"] is True and detail["q2"] is True
