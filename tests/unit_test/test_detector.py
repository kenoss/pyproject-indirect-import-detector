import ast
from pathlib import Path
from typing import List

from pyproject_indirect_import_detector.detector import _Detector, _IllegalImportDetected


def aux_detect(s: str, module_to_proj=None) -> List[_IllegalImportDetected]:
    module_to_proj_ = {} if module_to_proj is None else module_to_proj
    path = Path()
    tree = ast.parse(s)
    s_ = s.split("\n")
    detector = _Detector(module_to_proj_, path, s_, tree)
    return detector.detect()


def test_get_source() -> None:
    def aux(original, line, module):
        res = aux_detect(original)
        assert len(res) == 1
        err = res[0]
        assert err._line == line
        assert err._module == module

    aux(
        ("from \\\n" "    module \\\n" "    import name # comment"),
        "from      module      import name",
        "module",
    )
    aux(
        ("def f():\\\n" "    from module  import x, y # comment"),
        "from module  import x, y",
        "module",
    )


def test_detector_from_import() -> None:
    # Detect if not in known list.
    s = "from module import name"
    res = aux_detect(s)
    assert len(res) == 1
    assert res[0]._module == "module"

    s = "from module.x import name"
    res = aux_detect(s)
    assert len(res) == 1
    assert res[0]._module == "module"

    # Do not detect if in known list.
    s = "from module import name"
    res = aux_detect(s, {"module": "module"})
    assert len(res) == 0

    s = "from module.x import name"
    res = aux_detect(s, {"module": "module"})
    assert len(res) == 0

    # Do not detect if module starts with `.`.
    s = "from . import name"
    res = aux_detect(s)
    assert len(res) == 0

    s = "from .module import name"
    res = aux_detect(s)
    assert len(res) == 0

    s = "from .module.x import name"
    res = aux_detect(s)
    assert len(res) == 0


def test_detector_import() -> None:
    # Detect if not in known list.
    s = "import m, n"
    res = aux_detect(s)
    assert len(res) == 2
    assert res[0]._module == "m"
    assert res[1]._module == "n"

    s = "import m.x, n.y"
    res = aux_detect(s)
    assert len(res) == 2
    assert res[0]._module == "m"
    assert res[1]._module == "n"

    s = "import m as x, n as y"
    res = aux_detect(s)
    assert len(res) == 2
    assert res[0]._module == "m"
    assert res[1]._module == "n"

    # Do not detect if in known list.
    s = "import m, n"
    res = aux_detect(s, {"m": "m"})
    assert len(res) == 1
    assert res[0]._module == "n"
