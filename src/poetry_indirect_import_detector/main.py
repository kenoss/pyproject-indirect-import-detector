import ast
import sys
from pathlib import Path
from typing import List

from .detector import _Detector, _IllegalImportDetected, _read_file
from .pyproject import _PyProject
from .result import Err, Ok, Result
from .util import _flatten, _list_all_python_files


def _process_file(
    module_to_proj: dict[str, str], path: Path  # type: ignore  # reason: dict
) -> Result[List[_IllegalImportDetected], Exception]:
    s = _read_file(path)
    tree = ast.parse(s)
    s_ = s.split("\n")
    detector = _Detector(module_to_proj, path, s_, tree)
    return Ok(detector.detect())


def _detect(pyproject: _PyProject, dev: bool) -> Result[List[_IllegalImportDetected], Exception]:
    module_to_proj_ = pyproject.load_module_to_proj(dev)
    if module_to_proj_.is_err():
        return Err(module_to_proj_.unwrap_err())
    module_to_proj = module_to_proj_.unwrap()

    paths = pyproject.target_dirs(dev)
    paths = _flatten([_list_all_python_files(path) for path in paths])

    results = [_process_file(module_to_proj, path) for path in paths]
    return _merge_results(results)


def _merge_results(  # type: ignore  # Missing return statement ...why?
    results: List[Result[List[_IllegalImportDetected], Exception]]
) -> Result[List[_IllegalImportDetected], Exception]:
    if all([result.is_ok() for result in results]):
        xss = [result.unwrap() for result in results]
        xs = _flatten(xss)
        return Ok(xs)
    else:
        for result in results:
            if result.is_err():
                return result


def _main() -> None:
    pyproject_ = _PyProject.load()
    if pyproject_.is_err():
        raise pyproject_.unwrap_err()
    pyproject = pyproject_.unwrap()

    res_ = _detect(pyproject, False)
    res_dev = _detect(pyproject, True)
    res = _merge_results([res_, res_dev])

    if res.is_err():
        raise res.unwrap_err()
    else:
        xs = res.unwrap()
        if len(xs) == 0:
            print("OK")
        else:
            for x in xs:
                print(x)
            sys.exit(1)
