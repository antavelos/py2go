
import ast

from gst.nodes import AssignNode


def read_code():
    with open('sample.py', 'r') as f:
        return f.read()


def print_tree(tree: ast.AST):
    print(ast.dump(tree, indent=4))


if __name__ == '__main__':
    code = read_code()
    tree = ast.parse(code)
    # print_tree(tree)

    for item in tree.body:
        if isinstance(item, ast.Assign):
            node = AssignNode.from_assign(item)
            node.to_go()

        if isinstance(item, ast.AnnAssign):
            node = AssignNode.from_ann_assign(item)
            node.to_go()
