"""
MD INDUSTRIES
Developer: M.DHANESVARAN
Portable verification for the Python subset compiler.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT / "output"
SAMPLE_SOURCE = ROOT / "test" / "sample.py"
INVALID_SOURCE = ROOT / "test" / "semantic_error.py"
GENERATED_C = OUTPUT_DIR / "sample.c"
EXPECTED_OUTPUT = (OUTPUT_DIR / "expected_output.txt").read_text(encoding="utf-8").strip()


def run_command(command: list[str], expect_success: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if expect_success and result.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(command)}\n{result.stderr}")
    if not expect_success and result.returncode == 0:
        raise RuntimeError(f"Command unexpectedly succeeded: {' '.join(command)}")
    return result


def verify_generated_c() -> None:
    text = GENERATED_C.read_text(encoding="utf-8")
    required_snippets = [
        "int main(void)",
        'printf("%d\\n", x);',
        "while ((i < 3)) {",
        "if ((total > 2)) {",
    ]
    for snippet in required_snippets:
        if snippet not in text:
            raise RuntimeError(f"Generated C is missing required snippet: {snippet}")


def maybe_run_native_output() -> None:
    compiler = shutil.which("clang") or shutil.which("gcc")
    if not compiler:
        print("No host C compiler detected. Skipping native execution test.")
        return

    executable = OUTPUT_DIR / ("sample.exe" if sys.platform.startswith("win") else "sample.out")
    run_command([compiler, str(GENERATED_C), "-o", str(executable)])
    result = run_command([str(executable)])
    actual = result.stdout.strip()
    (OUTPUT_DIR / "runtime_output.txt").write_text(actual + "\n", encoding="utf-8")
    if actual != EXPECTED_OUTPUT:
        raise RuntimeError("Native execution output mismatch.")


def main() -> int:
    OUTPUT_DIR.mkdir(exist_ok=True)
    run_command([sys.executable, "-m", "pyportcc", str(SAMPLE_SOURCE), str(GENERATED_C)])
    verify_generated_c()
    run_command(
        [sys.executable, "-m", "pyportcc", str(INVALID_SOURCE), str(OUTPUT_DIR / "invalid.c")],
        expect_success=False,
    )
    maybe_run_native_output()
    print("Portable test passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
