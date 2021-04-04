import logging as _logging

# noqa idiom
if True:
    logger = _logging.getLogger(__name__)
    handler = _logging.StreamHandler()
    _level = _logging.WARNING
    handler.setLevel(_level)
    logger.setLevel(_level)
    logger.addHandler(handler)
    logger.propagate = False


from pathlib import Path
from typing import Any, List, MutableMapping, cast

import toml

from .domain import _load_proj_to_modules
from .exception import InvalidPyProjectError, InvalidPythonVersionError
from .result import Err, Ok, Result
from .util import _dict_rec_get


class _PyProject:
    _t: dict[str, Any]  # type: ignore  # reason: dict

    def __init__(self, t: MutableMapping[str, Any]) -> None:
        self._t = cast(dict[str, Any], t)  # type: ignore  # reason: dict

    def _init_validate(self) -> Result[None, InvalidPyProjectError]:
        if _dict_rec_get(self._t, ["tool", "poetry", "name"], None) is None:
            return Err(InvalidPyProjectError('path "tool/poetry/name" must not be empty'))

        res = self.base_python_version()
        if res.is_err():
            return Err(res.unwrap_err())

        return Ok(None)

    @classmethod
    def load(cls) -> Result["_PyProject", InvalidPyProjectError]:
        t = toml.load(open("pyproject.toml"))
        this = cls(t)
        res = this._init_validate()
        if res.is_err():
            return Err(res.unwrap_err())
        return Ok(this)

    def _project_name(self) -> str:
        ret = self._t["tool"]["poetry"]["name"]
        assert type(ret) is str
        return cast(str, ret)

    def base_python_version(self) -> Result[str, InvalidPythonVersionError]:
        python_version_constraint = _dict_rec_get(self._t, ["tool", "poetry", "dependencies", "python"], None)
        if python_version_constraint is None:
            return Err(InvalidPythonVersionError("must not be empty."))
        return _parse_minimal_python_verison(python_version_constraint)

    def _dependencies(self) -> List[str]:
        deps = _dict_rec_get(self._t, ["tool", "poetry", "dependencies"], None)
        if deps is None:
            return []
        else:
            return list(deps.keys())

    def _dev_dependencies(self) -> List[str]:
        deps = _dict_rec_get(self._t, ["tool", "poetry", "dev-dependencies"], None)
        if deps is None:
            return []
        else:
            return list(deps.keys())

    def dependencies(self, include_dev: bool) -> List[str]:
        xs = self._dependencies()
        if include_dev:
            xs += self._dev_dependencies()

        xs = list(set(xs))
        xs.remove("python")
        xs.sort()
        return xs

    def load_module_to_proj(self, dev: bool) -> Result[dict[str, str], Exception]:  # type: ignore  # reason: dict
        python_version_ = self.base_python_version()
        if python_version_.is_err():
            return Err(python_version_.unwrap_err())
        python_version = python_version_.unwrap()

        proj_to_modules_ = _load_proj_to_modules(self._project_name(), self.dependencies(dev), python_version)
        if proj_to_modules_.is_err():
            return Err(proj_to_modules_.unwrap_err())
        proj_to_modules = proj_to_modules_.unwrap()
        logger.debug(f"proj_to_modules = {proj_to_modules}")

        # fmt: off
        module_to_proj = dict((m, p)
                              for (p, ms) in proj_to_modules.items()
                              for m in ms)
        logger.debug(f"module_to_proj = {module_to_proj}")
        return Ok(module_to_proj)

    # Separate method for test.
    def _target_dirs(self, dev: bool) -> List[Path]:
        if dev:
            # TODO: Should we make it configurable?
            paths_ = ["tests"]
            paths = [Path(path) for path in paths_]
        else:
            packages_ = _dict_rec_get(self._t, ["tool", "poetry", "packages"], None)
            if packages_ is None:
                # Case: Module is `<package_name>`

                paths = [Path(self._project_name())]
            else:
                # Case: Modules are `src/<module>`

                # FIXME
                paths = [Path(x["from"]) / x["include"] for x in packages_]

        # FIXME
        assert len(paths) > 0
        return paths

    def target_dirs(self, dev: bool) -> List[Path]:
        return [path for path in self._target_dirs(dev) if path.exists()]


def _parse_minimal_python_verison(spec: str) -> Result[str, InvalidPythonVersionError]:
    def normalize(version: str) -> str:
        version_ = version.split(".")[:2]
        if len(version_) == 0:
            raise RuntimeError("unreachable")
        elif len(version_) == 1:
            return version_[0] + ".0"
        else:
            return version_[0] + "." + version_[1]

    if spec.startswith("^"):
        return Ok(normalize(spec[1:]))
    elif spec.startswith("~"):
        return Ok(normalize(spec[1:]))
    elif spec.endswith(".*"):
        return Ok(normalize(spec[:-2]))
    elif spec == "*":
        return Err(
            InvalidPythonVersionError(
                'this tool cannot treat well python version constraint "*".\n' 'Specify more concrete, e.g. "^3.9".'
            )
        )
    else:
        return Err(InvalidPythonVersionError(f"cannot understand: {spec}"))