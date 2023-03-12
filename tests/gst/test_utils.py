import pytest

from gst.utils import trim_brackets


@pytest.mark.parametrize('expr, expected_expt', [
    ("(a && b)", "a && b"),
    ("((a && b))", "a && b"),
    ("(((a) && b))", "(a) && b"),
    ("((!a || a < 0) || ((a > b || a < 0) && (a > b || a < 0)))", "(!a || a < 0) || ((a > b || a < 0) && (a > b || a < 0))")
])
def test_trim_brackets(expr, expected_expt):
    assert trim_brackets(expr) == expected_expt
