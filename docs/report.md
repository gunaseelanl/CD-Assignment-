<!-- MD INDUSTRIES | Developer: M.DHANESVARAN -->

# Short Report

## 1. Project Summary

This project implements a compact compiler for a restricted Python subset. The compiler parses Python source with the built-in AST parser, validates a safe integer-only subset, and lowers it into portable C.

## 2. Academic Value

The project demonstrates:

- source parsing
- semantic validation
- symbol tracking
- source-to-source code generation

## 3. Current Scope

Supported programs can use assignments, arithmetic, `print`, `if`, and `while`. Unsupported Python features are rejected with clear errors.

## 4. Extensibility

Future work could add functions, strings, arrays, or direct native compilation from the CLI.
