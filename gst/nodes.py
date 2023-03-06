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


@dataclass
class PyVariable:
    name: str
    value: any


class AssignNode(Node):
    def __init__(self, variables: list[PyVariable]):
        self.variables = variables

    @classmethod
    def from_assign(cls, assign: ast.Assign):
        def get_elt_value(elt: ast.Constant | ast.List | ast.Tuple) -> any:
            if hasattr(elt, 'elts'):
                return [get_elt_value(e) for e in getattr(elt, 'elts')]

            return elt.value

        def py_value_from_assign(assign: ast.Assign) -> any:
            if isinstance(assign.value, (ast.List, ast.Tuple)):
                return [get_elt_value(elt) for elt in assign.value.elts]

            if isinstance(assign.value, ast.Dict):
                keys = [key.value for key in assign.value.keys]
                values = [value.value for value in assign.value.values]
                return {key: value for key, value in zip(keys, values)}

            return assign.value.value

        variables = [
            PyVariable(name=target.id, value=py_value_from_assign(assign))
            for target in assign.targets
        ]
        return cls(variables)

    @classmethod
    def from_ann_assign(cls, assign: ast.AnnAssign):
        var = PyVariable(name=assign.target.id, value=assign.value.value)
        return cls([var])

    def to_go(self) -> str:
        return "\n".join(f"{var.name} := {py_value_to_go(var.value)}" for var in self.variables)