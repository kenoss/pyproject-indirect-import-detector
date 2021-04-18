from importlib.metadata import Distribution

from pyproject_indirect_import_detector.domain import _get_modules_by_files, _get_modules_by_toplevel_txt

PACKAGES = [
    "pysen",
    "pytest",
    "result",
    "stdlib-list",
    "toml",
]


def test_coherence_of_get_modules() -> None:
    for package in PACKAGES:
        dist = Distribution.from_name(package)
        lhs = _get_modules_by_toplevel_txt(dist)
        rhs = _get_modules_by_files(dist)
        if lhs is not None:
            assert set(lhs) == set(rhs)
