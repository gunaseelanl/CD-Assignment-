"""
MD INDUSTRIES
Developer: M.DHANESVARAN
CLI entry point for the portable Python subset compiler.
"""

from __future__ import annotations

import argparse
import sys

from .compiler import CompileError, compile_file
from .ide import launch_ide


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pyportcc",
        description="Compile a restricted Python source file into portable C.",
    )
    parser.add_argument(
        "--ide",
        action="store_true",
        help="Launch the Batman-themed desktop IDE.",
    )
    parser.add_argument("input", nargs="?", help="Path to the input Python source file.")
    parser.add_argument("output", nargs="?", help="Path to the output C file.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.ide:
        launch_ide()
        return 0
    if not args.input or not args.output:
        parser.error("the following arguments are required: input, output")
    try:
        compile_file(args.input, args.output)
    except CompileError as exc:
        print(f"Compilation failed: {exc}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"I/O error: {exc}", file=sys.stderr)
        return 1

    print(f"Compilation successful. C written to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
