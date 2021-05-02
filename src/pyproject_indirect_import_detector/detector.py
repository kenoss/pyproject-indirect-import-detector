import logging as _logging

# noqa idiom
if True:
    logger = _logging.getLogger(__name__)
    logger.addHandler(_logging.NullHandler())


import ast
import re
import tokenize
from pathlib import Path
from typing import Any, List


def _read_file(path: Path) -> str:
    with tokenize.open(path) as stream:
        return stream.read()


class _IllegalImportDetected:
    _path: Path
    _lineno: int
    _line: str
    _module: str

    def __init__(self, path: Path, lineno: int, line: str, module: str) -> None:
        self._path = path
        self._lineno = lineno
        self._line = line
        self._module = module

    def __str__(self) -> str:
        return (
            "Error:\n"
            f"    {self._path}:{self._lineno}: {self._line}\n"
            f"    {self._module} is imported, but not in dependency.\n"
            ""
        )


class _Detector(ast.NodeVisitor):
    _module_to_dict: dict[str, str]  # type: ignore  # reason: dict
    _path: Path
    _source: List[str]
    _tree: Any
    _errs: List[_IllegalImportDetected]

    def __init__(self, module_to_proj: dict[str, str], path: Path, source: List[str], tree: Any) -> None:  # type: ignore  # reason: dict
        self._module_to_proj = module_to_proj
        self._path = path
        self._source = source
        self._tree = tree
        self._errs = []

    def detect(self) -> List[_IllegalImportDetected]:
        self.visit(self._tree)

        return self._errs

    def _validate(self, module: str, node: Any, line: str) -> None:
        logger.debug(f"module = {module}")

        m = module.split(".")[0]

        if module.startswith("."):
            pass
        elif m in self._module_to_proj:
            pass
        else:
            err = _IllegalImportDetected(self._path, node.lineno, line, m)
            self._errs.append(err)

    def visit_Import(self, node: Any) -> None:
        line = _get_source(self._source, node)
        for name in node.names:
            self._validate(name.name, node, line)

    def visit_ImportFrom(self, node: Any) -> None:
        # `ast.NodeVisitor` does not give information to distinguish "from .module import ..." and "from module import ...".
        # So we parse source code by ourselves.
        line = _get_source(self._source, node)
        p = re.compile("from +([^ ]+)")
        m = p.match(line)
        assert m is not None
        module = m.group(1)
        self._validate(module, node, line)


def _get_source(source: List[str], node: Any) -> str:
    lines = source[node.lineno - 1 : node.end_lineno]
    lines[-1] = lines[-1][: node.end_col_offset]
    lines[0] = lines[0][node.col_offset :]
    return " ".join([line.removesuffix("\\") for line in lines])  # type: ignore  # reason: removesuffix
