"""Fail if any commands/*.py defines anything other than exactly one command."""

import ast
import sys
from pathlib import Path


def count_commands(path: Path) -> int:
    """Count the public top-level functions in a command module.

    Args:
        path: A module in the ``commands`` package.

    Returns:
        The number of public (not underscore-prefixed) top-level functions.
    """
    tree = ast.parse(path.read_text(encoding="utf-8"))
    return sum(
        isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef) and not node.name.startswith("_")
        for node in tree.body
    )


def main() -> int:
    """Check every command module and report the ones that break the rule.

    Returns:
        The process exit code: 0 when every module defines exactly one command.
    """
    pkg_commands = next(Path("src").glob("*/commands"))
    fail = False
    for path in sorted(pkg_commands.glob("*.py")):
        if path.name == "__init__.py":
            continue
        n = count_commands(path)
        if n != 1:
            print(f"{path}: defines {n} public functions, expected 1 command")
            fail = True
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
