def trim_brackets(expr: str) -> str:
    length = len(expr)
    brackets_to_remove = 0

    for i in range(int(length / 2)):
        if expr[i] != "(" or expr[length - 1 - i] != ")":
            break

        brackets_to_remove += 1

    return expr[brackets_to_remove:length - brackets_to_remove]
