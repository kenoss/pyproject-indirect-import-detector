import argparse
import ast
import sys
from pathlib import Path
from typing import List, Optional, Tuple

from termcolor import colored

from .detector import _Detector, _IllegalImportDetected, _read_file
from .pyproject import _PyProject
from .result import Err, Ok, Result
from .util import _flatten, _list_all_python_files


def _process_file(
    module_to_proj: dict[str, str], path: Path  # type: ignore  # reason: dict
) -> Result[Tuple[Path, List[_IllegalImportDetected]], Exception]:
    s = _read_file(path)
    tree = ast.parse(s)
    s_ = s.split("\n")
    detector = _Detector(module_to_proj, path, s_, tree)
    return Ok((path, detector.detect()))


def _detect(pyproject: _PyProject, dev: bool) -> Result[List[Tuple[Path, List[_IllegalImportDetected]]], Exception]:
    module_to_proj_ = pyproject.load_module_to_proj(dev)
    if module_to_proj_.is_err():
        return Err(module_to_proj_.unwrap_err())
    module_to_proj = module_to_proj_.unwrap()

    paths = pyproject.target_dirs(dev)
    paths = _flatten([_list_all_python_files(path) for path in paths])
    paths.sort()

    ret = []
    for path in paths:
        x = _process_file(module_to_proj, path)
        if x.is_ok():
            ret.append(x.unwrap())
        else:
            return Err(x.unwrap_err())
    return Ok(ret)


def _main_aux(args: argparse.Namespace, root: Path) -> None:
    pyproject_ = _PyProject.load(root)
    if pyproject_.is_err():
        raise pyproject_.unwrap_err()
    pyproject = pyproject_.unwrap()

    res = _detect(pyproject, False)
    res_dev = _detect(pyproject, True)
    if res.is_err():
        raise res.unwrap_err()
    elif res_dev.is_err():
        raise res_dev.unwrap_err()
    else:
        xs = _flatten([res.unwrap(), res_dev.unwrap()])
        ok = all([len(es) == 0 for (_, es) in xs])
        ok_or_ng = colored("OK", "green") if ok else colored("NG", "red")
        print(f"Checking {len(xs)} files... {ok_or_ng}")
        print("")

        for (path, es) in xs:
            if len(es) == 0:
                if args.v:
                    print(f"{colored('[OK]', 'green')} {path}")
            else:
                if args.v:
                    print(f"{colored('[NG]', 'red')} {path}")
                    print("")

                for e in es:
                    print(e)

        if not ok:
            sys.exit(1)


def _main(root: Optional[Path] = None) -> None:
    parser = argparse.ArgumentParser(description="Detect indirect import")
    parser.add_argument("-v", type=bool, nargs="?", const=True, default=False, help="Make output verbose.")
    args = parser.parse_args()

    if root is None:
        root = Path()

    _main_aux(args, root)
