# `pyproject-indirect-import-detector`: Indirect import detector

[![PyPI](https://img.shields.io/pypi/v/pyproject-indirect-import-detector.svg)](https://pypi.org/project/pyproject-indirect-import-detector)
[![Project License](https://img.shields.io/pypi/l/pyproject-indirect-import-detector.svg)](https://pypi.org/project/pyproject-indirect-import-detector)
[![Supported Python versions](https://img.shields.io/badge/python-3.9-1081c2.svg)](https://pypi.org/project/nitpick/)
[![CircleCI](https://circleci.com/gh/kenoss/pyproject-indirect-import-detector.svg?style=svg)](https://app.circleci.com/pipelines/github/kenoss/pyproject-indirect-import-detector)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## Motivation

Indirect import is bad.

- The biggest reason is requirements are not protected by [semantic versioning](https://semver.org/).
- [Tests cannot check import-problem correctly](tests/integration_test/case/ng_test_cannot_check_import_problem).
- Virtual environment is not strictly synced with `pyproject.toml` nor `poetry.lock` by `poetry`, so far.  It is possible that you delete a dependency but it still remains in the virtual environment.  This means, tests can accidentally pass.
- FYI, indirect import is not allowed in rust/cargo.

## Limitation

Currently, this tool only suuport `pyproject.toml` using `poetry`.
[PEP 631](https://www.python.org/dev/peps/pep-0631/) support is planed if python community agree this motivation and use this tool.

## How to use

### Install

```
poetry add --dev pyproject-indirect-import-detector
```

Note that this tool is intended to use in the virtual environment created by `poetry install`.  See also: [Why only works in venv?](#why-only-works-in-venv)

### Usage

```
poetry run pyproject-indirect-import-detector -v
```

See also [CI config](.circleci/config.yml), especially the job `check-indirect-import`.

### Configuration

You can configure by `pyproject.toml` as the following:

```
[tool.pyproject-indirect-import-detector]
exclude_modules = [
    "dataclasses",           # If you use compat trick like https://github.com/PyCQA/isort/blob/5.8.0/isort/_future/__init__.py#L3-L7 .
    "tests",                 # If your test suite make `tests` module importable and use it like https://github.com/andreoliwa/nitpick/blob/v0.26.0/tests/test_json.py#L6 .
    "dummy_module_for_test", # If you use dummy modules in tests like https://github.com/PyCQA/isort/blob/5.8.0/tests/unit/example_crlf_file.py#L1-L2 .
]
```

## FAQ

### It failes with not reasonable errors.

Report an issue and let me know your case.
The core logic is not yet well-tested with real packages.
We need edge cases.

### Why only works in venv?

This tool makes a correspondence from [package names to module names](src/pyproject_indirect_import_detector/domain.py).
This use [`importlib`](https://docs.python.org/3/library/importlib.html) and requires an environment that has all packages installed.
This tool is designed to be used in CI.  So, runnable under `poetry run` is enough.

### Why installable with `python >= 3.6` and runnable only in `python >= 3.9`?

See the comment in [pyproject.toml](./pyproject.toml).
I tried to make it runnable in old pythons, but the cost is high.
This tool is designed to be used in CI.  So, this restriction is reasonable.

## How to develop

### How to release

1. Bump version, PR and merge.
2. `git tag <version>` then `git push origin <version>`.
3. CI will pubish the package to PyPI: https://pypi.org/project/pyproject-indirect-import-detector/
