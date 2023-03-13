
import ast

from gst.nodes import ast_if_to_go


def read_code():
    with open('sample.py', 'r') as f:
        return f.read()


def print_tree(tree: ast.AST):
    print(ast.dump(tree, indent=4))


if __name__ == '__main__':
    code = read_code()
    tree = ast.parse(code)
    # print_tree(tree)
    print(ast_if_to_go(tree.body[2]))

