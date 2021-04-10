from pathlib import Path

import toml
from poetry_indirect_import_detector.exception import InvalidPyProjectError
from poetry_indirect_import_detector.pyproject import _parse_minimal_python_verison, _PyProject
from poetry_indirect_import_detector.result import Err, Ok, Result


def test_parse_minimal_python_version() -> None:
    assert _parse_minimal_python_verison("^3.9").unwrap() == "3.9"
    assert _parse_minimal_python_verison("^3.9.1").unwrap() == "3.9"
    assert _parse_minimal_python_verison("~3.9").unwrap() == "3.9"
    assert _parse_minimal_python_verison("~3.9.1").unwrap() == "3.9"
    assert _parse_minimal_python_verison("3.*").unwrap() == "3.0"
    assert _parse_minimal_python_verison("3.9.*").unwrap() == "3.9"

    assert _parse_minimal_python_verison("*").is_err()
    assert _parse_minimal_python_verison(">= 3.9").is_err()


class PyProject(_PyProject):
    @classmethod
    def test_load(cls, s: str) -> Result["PyProject", InvalidPyProjectError]:
        t = toml.loads(s)
        this = cls(t)
        res = this._init_validate()
        if res.is_err():
            return Err(res.unwrap_err())
        return Ok(this)


def dummy_toml(s: str) -> str:
    return (
        """
        [build-system]
        requires = ["poetry-core>=1.0.0"]
        build-backend = "poetry.core.masonry.api"

        """
        + s
    )


def test_pyproject() -> None:
    # Base.
    s = dummy_toml(
        """
        [tool.poetry]
        name = "foo"

        [tool.poetry.dependencies]
        python = "^3.9"
        """
    )
    pyproject = PyProject.test_load(s).unwrap()
    assert pyproject.base_python_version().unwrap() == "3.9"
    assert pyproject.dependencies(False) == []
    assert pyproject.dependencies(True) == []
    assert pyproject._target_dirs(False) == [Path("foo")]
    assert pyproject._target_dirs(True) == [Path("tests")]

    # "tool/poetry/name" missing.
    s = dummy_toml(
        """
        [tool.poetry]

        [tool.poetry.dependencies]
        python = "^3.9"
        """
    )
    assert PyProject.test_load(s).is_err()

    # "tool/poetry/dependencies" missing.
    s = dummy_toml(
        """
        [tool.poetry]
        name = "foo"
        """
    )
    assert PyProject.test_load(s).is_err()

    # "tool/poetry/dependencies/python" missing.
    s = dummy_toml(
        """
        [tool.poetry]
        name = "foo"

        [tool.poetry.dependencies]
        result = "^0.6.0"
        """
    )
    assert PyProject.test_load(s).is_err()

    # "tool/poetry/dependencies/python" invalid.
    s = dummy_toml(
        """
        [tool.poetry]
        name = "foo"

        [tool.poetry.dependencies]
        python = "*"
        """
    )
    assert PyProject.test_load(s).is_err()

    # `target_dirs()` for `src/<module_name>` case.
    s = dummy_toml(
        """
        [tool.poetry]
        name = "foo"
        packages = [
            {include = "bar", from = "src"},
            {include = "baz", from = "src"},
            {include = "no_from"},
            {from = "no_include"},
            "not_dict",
        ]

        [tool.poetry.dependencies]
        python = "^3.9"
        """
    )
    pyproject = PyProject.test_load(s).unwrap()
    assert pyproject._target_dirs(False) == [Path("src/bar"), Path("src/baz")]
    assert pyproject._target_dirs(True) == [Path("tests")]

    # Dependencies.
    s = dummy_toml(
        """
        [tool.poetry]
        name = "foo"

        [tool.poetry.dependencies]
        python = "^3.9"

        result = "^0.6.0"
        stdlib-list = "^0.8.0"
        toml = "^0.10.2"

        [tool.poetry.dev-dependencies]
        pysen = {version = "^0.9.1", extras = ["lint"]}
        pytest = "^5.2"
        """
    )
    pyproject = PyProject.test_load(s).unwrap()
    assert pyproject.dependencies(False) == ["result", "stdlib-list", "toml"]
    assert pyproject.dependencies(True) == ["pysen", "pytest", "result", "stdlib-list", "toml"]
