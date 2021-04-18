import os
import subprocess
from pathlib import Path
from typing import Tuple

CASES_DIR = Path(__file__).parent / "case"
CASES = list(CASES_DIR.iterdir())


def run(root: Path) -> Tuple[bool, str]:
    os.chdir(root)
    command = ["python", "-m", "poetry_indirect_import_detector"]
    p = subprocess.run(
        command,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )

    return (p.returncode == 0, p.stdout)


def test_output_self() -> None:
    root = Path()
    ok, _ = run(root)
    assert ok


def aux(root: Path) -> None:
    ok, err = run(root)
    if root.name.startswith("ok_"):
        assert ok
    elif root.name.startswith("ng_"):
        error_path = root / "error.txt"
        with open(error_path, "r") as f:
            error_output = f.read()

        assert not ok
        assert err == error_output
    else:
        raise RuntimeError("unreachable")


def test_output() -> None:
    for case_root in CASES:
        aux(case_root)


def gen(root: Path) -> None:
    error_path = root / "error.txt"

    ok, err = run(root)
    if not ok:
        with open(error_path, "w") as f:
            f.write(err)


def generate_error_txts() -> None:
    print(f"Generating {CASES_DIR}/*/error.txt ...")

    for case_root in CASES:
        gen(case_root)

    print(f"Generating {CASES_DIR}/*/error.txt ... done")


if __name__ == "__main__":
    generate_error_txts()
