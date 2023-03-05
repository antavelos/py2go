import ast

import pytest

from gst.nodes import PyValue, AssignNode


@pytest.mark.parametrize('py_value, expected_go_value', [
    (True, 'true'),
    (False, 'false'),
    ("test", '"test"'),
    (1, '1'),
    (1.1, '1.1'),
    ([1, 2, 3], '[]int{1,2,3}'),
    ((1, 2, 3), '[]int{1,2,3}'),
    ([1, 2, "3"], '[]interface{1,2,"3"}'),
    ((1, 2, "3"), '[]interface{1,2,"3"}'),
    ([1, 2, [3, 4]], '[]interface{1,2,[]int{3,4}}'),
])
def test_value(py_value, expected_go_value):
    value = PyValue(py_value)
    assert value.to_go() == expected_go_value


@pytest.mark.parametrize('python_assign, expected_go_assignment', [
    ('test = True', 'test := true'),
    ('test = False', 'test := false'),
    ('test = "test"', 'test := "test"'),
    ('test = 1', 'test := 1'),
    ('test = 1.1', 'test := 1.1'),
    ('test = [1, 2, 3]', 'test := []int{1,2,3}'),
    ('test = (1, 2, 3)', 'test := []int{1,2,3}'),
    ('test = [1, 2, "3"]', 'test := []interface{1,2,"3"}'),
    ('test = (1, 2, "3")', 'test := []interface{1,2,"3"}'),
    ('test = [1, 2, [3, 4]]', 'test := []interface{1,2,[]int{3,4}}'),
])
def test_assign_node(python_assign, expected_go_assignment):
    tree = ast.parse(python_assign)
    node = AssignNode.from_assign(assign=tree.body[0])
    assert node.to_go() == expected_go_assignment
