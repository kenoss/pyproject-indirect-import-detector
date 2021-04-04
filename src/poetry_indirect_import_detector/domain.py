from importlib.metadata import Distribution
from typing import List

from stdlib_list import stdlib_list

from .exception import InvalidPythonVersionError
from .result import Err, Ok, Result


# TODO: top_level.txt is not ensured
def _get_modules(project_name: str) -> List[str]:
    dist = Distribution.from_name(project_name)
    modules = dist.read_text("top_level.txt")
    assert modules is not None
    return modules.rstrip().split("\n")


def _load_proj_to_modules(
    self_project_name: str,
    project_names: List[str],
    python_version: str,
) -> Result[dict[str, List[str]], InvalidPythonVersionError]:  # type: ignore  # reason: dict
    try:
        modules_std = stdlib_list(python_version)
    except ValueError as err:
        msg = f"`stdlib-list` does not support {python_version}"
        return Err(err).wrap_err(InvalidPythonVersionError(msg))

    proj_to_modules_std = {"std": modules_std}
    proj_to_modules_dep = dict((proj, _get_modules(proj)) for proj in project_names)
    proj_to_modules_self = {self_project_name: [self_project_name]}
    proj_to_modules = {**proj_to_modules_std, **proj_to_modules_dep, **proj_to_modules_self}
    return Ok(proj_to_modules)
