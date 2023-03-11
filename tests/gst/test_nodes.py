import ast

import pytest

from gst.nodes import py_value_to_go, ast_bool_op_to_go, ast_if_to_go, ast_assign_to_go, ast_ann_assign_to_go


@pytest.mark.parametrize('py_value, expected_go_value', [
    (True, 'true'),
    (False, 'false'),
    ("test", '"test"'),
    (1, '1'),
    (1.1, '1.1'),
    ([1, 2, 3], '[]int{1, 2, 3}'),
    ((1, 2, 3), '[]int{1, 2, 3}'),
    ([1, 2, "3"], '[]any{1, 2, "3"}'),
    ((1, 2, "3"), '[]any{1, 2, "3"}'),
    ([1, 2, [3, 4]], '[]any{1, 2, []int{3, 4}}'),
])
def test_value(py_value, expected_go_value):
    assert py_value_to_go(py_value) == expected_go_value


@pytest.mark.parametrize('python_assign, expected_go_assignment', [
    ('test = True', 'test := true'),
    ('test = False', 'test := false'),
    ('test = "test"', 'test := "test"'),
    ('test = 1', 'test := 1'),
    ('test = 1.1', 'test := 1.1'),
    ('test = [1, 2, 3]', 'test := []int{1, 2, 3}'),
    ('test = (1, 2, 3)', 'test := []int{1, 2, 3}'),
    ('test = [1, 2, "3"]', 'test := []any{1, 2, "3"}'),
    ('test = (1, 2, "3")', 'test := []any{1, 2, "3"}'),
    ('test = [1, 2, [3, 4]]', 'test := []any{1, 2, []int{3, 4}}'),
    ('test = {"key1": 1, "key2": 2}', 'test := map[string]int{"key1": 1, "key2": 2}'),
    ('test = {"key1": 1, "key2": "2"}', 'test := map[string]any{"key1": 1, "key2": "2"}'),
    ('test = {1: 1, "key2": "2"}', 'test := map[any]any{1: 1, "key2": "2"}'),
    ('test = {1: 1, "key2": ["2"]}', 'test := map[any]any{1: 1, "key2": []string{"2"}}'),
    ('test = {1: 1, "key2": ["2", 1]}', 'test := map[any]any{1: 1, "key2": []any{"2", 1}}'),
])
def test_assign_node(python_assign, expected_go_assignment):
    tree = ast.parse(python_assign)
    assert ast_assign_to_go(assign=tree.body[0]) == expected_go_assignment


@pytest.mark.parametrize('python_assign, expected_go_assignment', [
    ('test: bool = True', 'test := true'),
    ('test: bool = False', 'test := false'),
    ('test: int = "test"', 'test := "test"'),
    ('test: int = 1', 'test := 1'),
    ('test: float = 1.1', 'test := 1.1'),
    ('test: list = [1, 2, 3]', 'test := []int{1, 2, 3}'),
    ('test: tuple = (1, 2, 3)', 'test := []int{1, 2, 3}'),
    ('test: list = [1, 2, "3"]', 'test := []any{1, 2, "3"}'),
    ('test: list = (1, 2, "3")', 'test := []any{1, 2, "3"}'),
    ('test: list = [1, 2, [3, 4]]', 'test := []any{1, 2, []int{3, 4}}'),
    ('test: dict = {"key1": 1, "key2": 2}', 'test := map[string]int{"key1": 1, "key2": 2}'),
    ('test: dict = {"key1": 1, "key2": "2"}', 'test := map[string]any{"key1": 1, "key2": "2"}'),
    ('test: dict = {1: 1, "key2": "2"}', 'test := map[any]any{1: 1, "key2": "2"}'),
    ('test: dict = {1: 1, "key2": ["2"]}', 'test := map[any]any{1: 1, "key2": []string{"2"}}'),
    ('test: dict = {1: 1, "key2": ["2", 1]}', 'test := map[any]any{1: 1, "key2": []any{"2", 1}}'),
])
def test_ann_assign_node(python_assign, expected_go_assignment):
    tree = ast.parse(python_assign)
    assert ast_ann_assign_to_go(assign=tree.body[0]) == expected_go_assignment


@pytest.mark.parametrize('py_expression, expected_go_expression', [
    ("a or b", "(a || b)"),
    ("a > 1 or b", "(a > 1 || b)"),
    ("a > 1 or b and c", "(a > 1 || (b && c))"),
    ("a > 1 or b and c", "(a > 1 || (b && c))"),
    ("(not a or a < 0) or (a > b or a < 0) and (a > b or a < 0)", "((!a || a < 0) || ((a > b || a < 0) && (a > b || a < 0)))"),
])
def test_ast_bool_op_to_go(py_expression, expected_go_expression):
    tree = ast.parse(py_expression)
    bool_op = tree.body[0].value
    assert ast_bool_op_to_go(bool_op) == expected_go_expression


@pytest.mark.parametrize('py_if_cond, expected_go_if_cond', [
    ("""
if a > b:
    pass
    """,
     "if (a > b) {}"),
    ("""
if a > b and b > 0:
    pass
    """,
     "if (a > b && b > 0) {}"),

])
def test_ast_if_to_go(py_if_cond, expected_go_if_cond):
    tree = ast.parse(py_if_cond)
    if_node = tree.body[0]
    assert ast_if_to_go(if_node) == expected_go_if_cond