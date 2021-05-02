from importlib.metadata import Distribution
from typing import List, Optional

from stdlib_list import stdlib_list

from .exception import InvalidPythonVersionError
from .result import Err, Ok, Result


# We focus on wheel and make things are simple.
#
# Rationale:
# - Lots of packages contain `top_level.txt`, but the existance is not assured.
# - Lots of packages provide wheel.
# - The following logic should works well on wheel case because of PEP 427.
# - The author doesn't know the egg case that the following logic works well on.
#
# Let us know if there's a pathological case.
def _get_modules(project_name: str) -> List[str]:
    dist = Distribution.from_name(project_name)
    return _get_modules_by_toplevel_txt(dist) or _get_modules_by_files(dist)


def _get_modules_by_toplevel_txt(dist: Distribution) -> Optional[List[str]]:
    modules = dist.read_text("top_level.txt")
    if modules is None:
        return None
    else:
        return modules.rstrip().split("\n")


def _get_modules_by_files(dist: Distribution) -> List[str]:
    paths = dist.files
    # Safety:
    #   PEP 427 ensures that wheel must contain `RECORD` file.
    #   We do not care about egg-info case. (Are there any packages that violate below?)
    assert paths is not None
    IGNORE_SUFFIX_LIST = [
        ".dist-info",
        ".egg-info",
    ]
    # fmt: off
    return [dir_
            for dir_ in set(path.parts[0] for path in paths)
            # Note that there is a possibility that `dir_ == ".."` if the distribution includes entrypoints.
            if (dir_ != "..") and (not any([dir_.endswith(suffix) for suffix in IGNORE_SUFFIX_LIST]))]


def _load_proj_to_modules(
    self_project_name: str,
    self_module_names: List[str],
    project_names: List[str],
    python_version: str,
    exclude_modules: List[str],
) -> Result[dict[str, List[str]], InvalidPythonVersionError]:  # type: ignore  # reason: dict
    try:
        modules_std = stdlib_list(python_version)
    except ValueError as err:
        msg = f"`stdlib-list` does not support {python_version}"
        return Err(err).wrap_err(InvalidPythonVersionError(msg))

    proj_to_modules_std = {"<std>": modules_std}
    proj_to_modules_dep = dict((proj, _get_modules(proj)) for proj in project_names)
    proj_to_modules_self = {self_project_name: self_module_names}
    proj_to_modules_exclude = {"<exclude>": exclude_modules}
    proj_to_modules = {
        **proj_to_modules_std,
        **proj_to_modules_dep,
        **proj_to_modules_self,
        **proj_to_modules_exclude,
    }
    return Ok(proj_to_modules)
