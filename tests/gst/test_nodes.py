import ast

import pytest

from gst.nodes import AssignNode, py_value_to_go


@pytest.mark.parametrize('py_value, expected_go_value', [
    (True, 'true'),
    (False, 'false'),
    ("test", '"test"'),
    (1, '1'),
    (1.1, '1.1'),
    ([1, 2, 3], '[]int{1,2,3}'),
    ((1, 2, 3), '[]int{1,2,3}'),
    ([1, 2, "3"], '[]any{1,2,"3"}'),
    ((1, 2, "3"), '[]any{1,2,"3"}'),
    ([1, 2, [3, 4]], '[]any{1,2,[]int{3,4}}'),
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
])
def test_assign_node(python_assign, expected_go_assignment):
    tree = ast.parse(python_assign)
    node = AssignNode.from_assign(assign=tree.body[0])
    assert node.to_go() == expected_go_assignment
