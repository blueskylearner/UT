
from validators import is_valid_email, non_empty

def test_non_empty():
    assert non_empty("x")
    assert not non_empty("   ")
    assert not non_empty(None)

def test_is_valid_email():
    assert is_valid_email("teacher@unitedteaching.org")
    assert not is_valid_email("teacher@")
    assert not is_valid_email("foo")
