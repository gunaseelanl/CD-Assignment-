# Repository Guidelines

## Project Structure & Module Organization

The compiler lives in `src/`. Core modules are split by stage: `lexer.l` for Flex, `parser.y` for Bison, `ast.*` for syntax tree structures, `semantic.*` for validation, `symbol_table.*` for identifier tracking, `codegen.*` for LLVM IR emission, and `driver.c` for the CLI entry point. Documentation is in `docs/`, sample inputs are in `test/`, generated artifacts belong in `output/`, and cross-platform helper scripts are in `scripts/`. Reference assets, including architecture diagrams, are stored outside the repo root in `../Reference/`.

## Build, Test, and Development Commands

Use the command set that matches your machine:

- `make` builds `bin/minicc` with Flex and Bison on Unix-like systems.
- `cmake -S . -B build && cmake --build build` configures a portable build.
- `sh scripts/build_portable.sh` runs tool checks and a Unix build.
- `powershell -ExecutionPolicy Bypass -File scripts/build_portable.ps1` does the same on Windows.
- `sh scripts/test_portable.sh` or `powershell -ExecutionPolicy Bypass -File scripts/test_portable.ps1` builds, compiles `test/sample.c`, lowers IR with `llc`, links, runs, and compares against `output/expected_output.txt`.

## Coding Style & Naming Conventions

Use C99-compatible code, 4-space indentation, and ASCII-only source unless a file already requires otherwise. Keep functions small and stage-specific. Use lowercase snake_case for C functions (`semantic_analyze`), lowercase filenames for C modules (`symbol_table.c`), and uppercase token names in Flex/Bison (`INT`, `RETURN`, `PRINTF`). Preserve the file header identifying `MD INDUSTRIES` and `M.DHANESVARAN`.

## Testing Guidelines

Add one focused input per behavior in `test/`. Name valid programs by feature, for example `arithmetic_precedence.c`, and invalid programs by failure mode, for example `undeclared_variable.c`. A change that affects parsing, semantics, or codegen should include at least one new test input and, when relevant, an expected output file in `output/`.

## Commit & Pull Request Guidelines

This directory is not currently a Git repository, so there is no historical convention to mirror. Use short imperative commit subjects such as `Add return statement codegen` or `Fix parser precedence`. Pull requests should describe the affected compiler stage, list added tests, note any toolchain requirements, and include screenshots only when documentation or execution output changed.
