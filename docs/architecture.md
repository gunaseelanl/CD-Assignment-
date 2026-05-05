<!-- MD INDUSTRIES | Developer: M.DHANESVARAN -->

# Compiler Architecture

## Overview

The compiler targets a compact Python subset and emits portable C. It reuses Python's built-in parser through the standard-library `ast` module and keeps the custom logic focused on semantic restriction and code generation.

## Pipeline

1. Source parsing with `ast.parse`
2. subset validation and assignment-before-use checks
3. symbol collection for generated variable declarations
4. C code generation
5. optional native compilation with a host C compiler

## Main Modules

- `pyportcc/compiler.py`
- `pyportcc/__main__.py`
- `scripts/test_portable.py`

## Supported Statements

```txt
NAME = expression
NAME op= expression
print(expression)
if expression:
    ...
else:
    ...
while expression:
    ...
```

## Supported Expressions

```txt
NUMBER | True | False | NAME
-expression
expression + expression
expression - expression
expression * expression
expression // expression
expression % expression
expression compare_op expression
```
