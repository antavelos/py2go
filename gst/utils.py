def _is_mirror_brackets(expr: str) -> bool:
    brackets = [e for e in expr if e in ["(", ")"]]
    brackets_len = len(brackets)
    for i in range(int(brackets_len / 2)):
        if brackets[i] != "(" or brackets[brackets_len - 1 - i] != ")":
            return False

    return True


def trim_brackets(expr: str) -> str:
    length = len(expr)
    brackets_to_remove = 0

    for i in range(int(length / 2)):
        if expr[i] != "(" or expr[length - 1 - i] != ")":
            break

        brackets_to_remove += 1

    if not _is_mirror_brackets(expr):
        brackets_to_remove -= 1

    return expr[brackets_to_remove:length - brackets_to_remove]
