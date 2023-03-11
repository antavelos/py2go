import pytest

from gst.utils import trim_brackets


@pytest.mark.parametrize('expr, expected_expt', [
    ("(a && b)", "a && b"),
    ("((a && b))", "a && b"),
    ("(((a) && b))", "(a) && b"),
])
def test_trim_brackets(expr, expected_expt):
    assert trim_brackets(expr) == expected_expt
