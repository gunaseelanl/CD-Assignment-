# MD INDUSTRIES

Developer: `M.DHANESVARAN`

## Portable Build Strategy

The compiler is a pure-Python package. The build step only prepares local launcher scripts and output directories.

## Required Tool

- `python` 3.11 or newer

## Optional Tool

- `gcc`, `clang`, or another C compiler if you want to build the generated C into a native executable

## Launch Options

- CLI: `python -m pyportcc input.py output.c`
- IDE: `python -m pyportcc --ide`
