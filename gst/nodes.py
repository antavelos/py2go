import ast
import enum
from dataclasses import dataclass
from typing import Protocol


class GoType(enum.Enum):
    STRING = 'string'
    INT = 'int'
    FLOAT = 'float'
    SLICE = 'slice'
    MAP = 'map'
    BOOL = 'bool'
    ANY = 'any'
    NIL = 'nil'


PY2GO_TYPES = {
    str: GoType.STRING,
    int: GoType.INT,
    float: GoType.FLOAT,
    bool: GoType.BOOL,
    list: GoType.SLICE,
    tuple: GoType.SLICE,
    dict: GoType.MAP,
    None: GoType.NIL
}


class Node(Protocol):
    def to_go(self) -> str: ...


def _infer_list_type(lst: list[any]) -> GoType:
    type_set = {type(item) for item in lst}

    if len(type_set) == 1:
        return PY2GO_TYPES.get(type_set.pop())

    return GoType.ANY


def py_value_to_go(value: any) -> str:
    match value:
        case bool():
            return 'true' if value else 'false'
        case str():
            return f'"{value}"'
        case list() | tuple():
            list_type = _infer_list_type(value)
            value_str = ", ".join([py_value_to_go(item) for item in value])

            return f"[]{list_type.value}{{{value_str}}}"
        case dict():
            key_type = _infer_list_type(list(value.keys()))
            value_type = _infer_list_type(list(value.values()))

            def dict_pair_str(key: any, value: any) -> str:
                return f'{py_value_to_go(key)}: {py_value_to_go(value)}'

            def value_str(value: dict) -> str:
                return f'{{{", ".join([dict_pair_str(key, val) for key, val in value.items()])}}}'

            return f"map[{key_type.value}]{value_type.value}{value_str(value)}"

    return f"{value}"


def get_elt_value(elt: ast.Constant | ast.List | ast.Tuple) -> any:
    if hasattr(elt, 'elts'):
        return [get_elt_value(e) for e in getattr(elt, 'elts')]

    return elt.value


def py_value_from_assign_value(assign_value) -> any:
    if isinstance(assign_value, (ast.List, ast.Tuple)):
        return [get_elt_value(elt) for elt in assign_value.elts]

    if isinstance(assign_value, ast.Dict):
        keys = [key.value for key in assign_value.keys]
        values = [py_value_from_assign_value(value) for value in assign_value.values]
        return {key: value for key, value in zip(keys, values)}

    return assign_value.value


@dataclass
class PyVariable:
    name: str
    value: any


class AssignNode:
    def __init__(self, py_variables: list[PyVariable]):
        self.py_variables = py_variables

    @classmethod
    def from_ast_assign(cls, assign: ast.Assign):
        variables = [
            PyVariable(name=target.id, value=py_value_from_assign_value(assign.value))
            for target in assign.targets
        ]
        return cls(variables)

    @classmethod
    def from_ast_ann_assign(cls, assign: ast.AnnAssign):
        var = PyVariable(name=assign.target.id, value=py_value_from_assign_value(assign.value))
        return cls([var])

    def to_go(self) -> str:
        return "\n".join(f"{var.name} := {py_value_to_go(var.value)}" for var in self.py_variables)


class CompareOp(enum.Enum):
    EQ = 'eq'
    NE = 'ne'
    GT = 'gt'
    GE = 'ge'
    LT = 'lt'
    LE = 'le'


class GoBoolOp(enum.Enum):
    AND = '&&'
    OR = '||'


@dataclass
class Compare:
    left: any
    right: any
    op: CompareOp


class BoolCondition:
    left: any
    right: any


class IfNode:
    def __init__(self, comparisons: list[Compare], body: list[Node]):
        self.comparisons = comparisons
        self.body = body

    def to_go(self) -> str:
        return f"""if """


def go_compare_op_from_ast_compare_op(op: ast.Gt | ast.GtE | ast.Eq | ast.NotEq | ast.Lt | ast.LtE) -> str:
    mapper = {
        ast.Gt: ">",
        ast.GtE: ">=",
        ast.Lt: "<",
        ast.LtE: "<=",
        ast.Eq: "==",
        ast.NotEq: "!="
    }
    return mapper.get(type(op))


def py_value_from_ast_name_or_constant(var: ast.Name | ast.Constant) -> any:
    if isinstance(var, ast.Name):
        return var.id

    if isinstance(var, ast.Constant):
        return py_value_from_assign_value(var)


def ast_compare_to_go(compare: ast.Compare) -> str:
    left = py_value_from_ast_name_or_constant(compare.left)
    right = py_value_from_ast_name_or_constant(compare.comparators[0])
    op = go_compare_op_from_ast_compare_op(compare.ops[0])

    return f"{left} {op} {right}"


def ast_unary_op_to_go(unary: ast.UnaryOp) -> str:
    mapper = {
        ast.Not: "!",
        ast.UAdd: "+",
        ast.USub: "-"
    }
    op = mapper.get(type(unary.op))
    operand = py_value_from_ast_name_or_constant(unary.operand)

    return f"{op}{operand}"


def ast_name_to_go(name: ast.Name) -> str:
    return name.id


def ast_constant_to_go(const: ast.Constant) -> str:
    return const.value


def ast_bool_op_to_go(bool_op: ast.BoolOp) -> str:
    operator_mapper = {
        ast.Or: "||",
        ast.And: "&&"
    }

    operand_mapper = {
        ast.Name: ast_name_to_go,
        ast.Constant: ast_constant_to_go,
        ast.UnaryOp: ast_unary_op_to_go,
        ast.Compare: ast_compare_to_go,
        ast.BoolOp: ast_bool_op_to_go
    }

    left = operand_mapper.get(type(bool_op.values[0]))(bool_op.values[0])
    right = operand_mapper.get(type(bool_op.values[1]))(bool_op.values[1])
    operator = operator_mapper.get(type(bool_op.op))

    return f"({left} {operator} {right})"


def trim_brackets(expr: str) -> str:
    length = len(expr)
    brackets_to_remove = 0

    for i in range(int(length / 2)):
        if expr[i] != "(" or expr[length - 1 - i] != ")":
            break

        brackets_to_remove += 1

    return expr[brackets_to_remove:length - brackets_to_remove]


def ast_if_to_go(if_cond: ast.If):
    condition_mapper = {
        ast.Compare: ast_compare_to_go,
        ast.BoolOp: ast_bool_op_to_go
    }

    condition = condition_mapper[type(if_cond.test)](if_cond.test)

    return f"if ({trim_brackets(condition)}) {{}}"