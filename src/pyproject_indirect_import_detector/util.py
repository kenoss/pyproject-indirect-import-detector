import os
from pathlib import Path
from typing import Any, List, TypeVar

T = TypeVar("T")


def _flatten(xss: List[List[T]]) -> List[T]:
    # fmt: off
    return [x
            for xs in xss
            for x in xs]


def _walk(path: Path) -> List[Path]:
    # fmt: off
    return [Path(d) / f
            for (d, _, fs) in os.walk(path)
            for f in fs]


def _list_all_python_files(path: Path) -> List[Path]:
    # fmt: off
    return [path
            for path in _walk(path)
            if path.name.endswith(".py")]


def _dict_rec_get(d: dict[Any, Any], path: List[Any], default: Any) -> Any:  # type: ignore  # reason: dict
    """
    Get an element of path from dict.

    >>> d = {'a': 'a', 'b': {'c': 'bc', 'd': {'e': 'bde'}}}

    Simple get:

    >>> _dict_rec_get(d, ['a'], None)
    'a'

    Returns default if key does not exist:

    >>> _dict_rec_get(d, ['c'], None) is None
    True
    >>> _dict_rec_get(d, ['c'], 0)
    0

    Get recursive:

    >>> _dict_rec_get(d, ['b', 'c'], None)
    'bc'
    >>> _dict_rec_get(d, ['b', 'd'], None)
    {'e': 'bde'}
    >>> _dict_rec_get(d, ['b', 'd', 'e'], None)
    'bde'
    >>> _dict_rec_get(d, ['b', 'nopath'], None) is None
    True
    """

    assert isinstance(path, list)

    while len(path) != 0:
        p = path[0]
        path = path[1:]
        if isinstance(d, dict) and (p in d):  # type: ignore
            d = d[p]
        else:
            return default

    return d
