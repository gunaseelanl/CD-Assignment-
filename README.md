<!--
  MD INDUSTRIES
  Developer: M.DHANESVARAN
  Project: Portable Python Subset Compiler
-->

# Compiler-Design-DSL_RegNo_Name

This repository contains a lightweight portable compiler for a restricted Python subset. The compiler is written in pure Python, uses the standard-library `ast` parser, validates a controlled integer-only subset, and emits portable C code.

## Supported Source Features

- integer and boolean literals
- variable assignment
- `+=`, `-=`, `*=`, `//=`, `%=` updates
- arithmetic with `+`, `-`, `*`, `//`, `%`
- comparisons with `==`, `!=`, `<`, `<=`, `>`, `>=`
- `if` / `else`
- `while`
- `print(expr)`

## Current Limits

- integer-only code generation
- single-argument `print`
- no functions, imports, classes, lists, strings, or floats

## Pipeline

`source.py -> Python AST -> semantic validation -> portable C output`

## Why It Is Portable

- no `flex`
- no `bison`
- no `cmake`
- no third-party Python dependencies
- only Python 3.11+ is required for the compiler

## Repository Layout

- `pyportcc/` compiler package
- `test/` sample inputs
- `output/` generated artifacts
- `scripts/` build and test helpers
- `docs/` project notes

## Quick Start

```powershell
powershell -ExecutionPolicy Bypass -File scripts/build_portable.ps1
python -m pyportcc test/sample.py output/sample.c
powershell -ExecutionPolicy Bypass -File scripts/test_portable.ps1
```

## Run The IDE

Launch the Batman-themed dark IDE:

```powershell
python -m pyportcc --ide
```

Inside the IDE you can:

- write or open a `.py` source file
- compile it to C
- inspect the generated C code
- save both source and output files

## Run From Terminal

Compile a file directly:

```powershell
python -m pyportcc test/sample.py output/sample.c
```

Or use the local launcher created by the build script:

```powershell
bin\pyportcc.cmd test\sample.py output\sample.c
```

## Example Input

```python
x = 10
y = 20
x = x + y * 2
print(x)
print(x - 5)
```

## Example Output

```txt
50
45
```
