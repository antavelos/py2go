import ast
import enum
from dataclasses import dataclass
from typing import Protocol


class GoType(enum.Enum):
    INT = 'int'
    FLOAT = 'float'
    SLICE = 'slice'
    MAP = 'map'
    BOOL = 'bool'
    INTERFACE = 'interface'
    NIL = 'nil'


PY2GO_TYPES = {
    int: GoType.INT,
    float: GoType.FLOAT,
    bool: GoType.BOOL,
    list: GoType.SLICE,
    tuple: GoType.SLICE,
    dict: GoType.MAP,
    None: GoType.NIL
}


class Node(Protocol):
    def to_go(self): ...


@dataclass
class PyValue:
    value: any

    @staticmethod
    def _infer_list_type(lst: list[any]) -> GoType:
        type_set = {type(item) for item in lst}

        if len(type_set) == 1:
            return PY2GO_TYPES.get(type_set.pop())

        return GoType.INTERFACE

    def to_go(self):

        match self.value:
            case bool():
                return 'true' if self.value else 'false'
            case str():
                return f'"{self.value}"'
            case list() | tuple():
                list_type = self._infer_list_type(self.value)
                list_str = ",".join([PyValue(item).to_go() for item in self.value])
                return f"[]{list_type.value}{{{list_str}}}"

        return f"{self.value}"


@dataclass
class PyVariable:
    name: str
    value: PyValue


class AssignNode(Node):
    def __init__(self, variables: list[PyVariable]):
        self.variables = variables

    @classmethod
    def from_assign(cls, assign: ast.Assign):
        def get_elt_value(elt: ast.Constant | ast.List | ast.Tuple) -> any:
            if hasattr(elt, 'elts'):
                return [get_elt_value(e) for e in getattr(elt, 'elts')]

            return elt.value

        def py_value_from_assign(assign: ast.Assign) -> PyValue:
            if isinstance(assign.value, (ast.List, ast.Tuple)):
                return PyValue([get_elt_value(elt) for elt in assign.value.elts])

            return PyValue(assign.value.value)

        variables = [
            PyVariable(name=target.id, value=py_value_from_assign(assign))
            for target in assign.targets
        ]
        return cls(variables)

    @classmethod
    def from_ann_assign(cls, assign: ast.AnnAssign):
        var = PyVariable(name=assign.target.id, value=PyValue(assign.value.value))
        return cls([var])

    def to_go(self):
        return "\n".join(f"{var.name} := {var.value.to_go()}" for var in self.variables)