import os
import subprocess
from pathlib import Path
from typing import Tuple

CASES_DIR = Path(__file__).parent / "case"
CASES = list(CASES_DIR.iterdir())


def run(root: Path, v: bool) -> Tuple[bool, str]:
    os.chdir(root)
    command = ["python", "-m", "poetry_indirect_import_detector"]
    if v:
        command.append("-v")
    p = subprocess.run(
        command,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )

    return (p.returncode == 0, p.stdout)


def test_output_self() -> None:
    root = Path()

    for v in [False, True]:
        ok, _ = run(root, v)
        assert ok


def aux(root: Path) -> None:
    for v in [False, True]:
        if v:
            output_path = root / "output-v.txt"
        else:
            output_path = root / "output.txt"

        with open(output_path, "r") as f:
            output_expect = f.read()

        ok, output_got = run(root, v)
        if root.name.startswith("ok_"):
            assert ok
        elif root.name.startswith("ng_"):
            assert not ok
            assert output_got == output_expect
        else:
            raise RuntimeError("unreachable")


def test_output() -> None:
    for case_root in CASES:
        aux(case_root)


def gen(root: Path) -> None:
    for v in [False, True]:
        if v:
            output_path = root / "output-v.txt"
        else:
            output_path = root / "output.txt"

        _, output = run(root, v)
        with open(output_path, "w") as f:
            f.write(output)


def generate_error_txts() -> None:
    print(f"Generating {CASES_DIR}/*/error.txt ...")

    for case_root in CASES:
        gen(case_root)

    print(f"Generating {CASES_DIR}/*/error.txt ... done")


if __name__ == "__main__":
    generate_error_txts()
