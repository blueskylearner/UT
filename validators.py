
import re
_EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[\w.-]+\.[A-Za-z]{2,}$")

def is_valid_email(s: str) -> bool:
    """Return True if s looks like a valid email address; otherwise False."""
    return bool(_EMAIL_RE.match(s or ""))

def non_empty(s: str) -> bool:
    """Return True if s contains non-whitespace characters; otherwise False."""
    return bool((s or "").strip())
