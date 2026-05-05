"""
MD INDUSTRIES
Developer: M.DHANESVARAN
Core compiler for a restricted Python subset.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
from pathlib import Path


class CompileError(Exception):
    """Raised when source code cannot be compiled by the subset compiler."""


class ExecutionError(Exception):
    """Raised when source execution fails inside the subset runtime."""


def _line_of(node: ast.AST) -> str:
    return f"line {getattr(node, 'lineno', '?')}"


@dataclass
class ValidationState:
    assigned: set[str] = field(default_factory=set)
    variables: list[str] = field(default_factory=list)
    variable_set: set[str] = field(default_factory=set)

    def remember_variable(self, name: str) -> None:
        if name not in self.variable_set:
            self.variable_set.add(name)
            self.variables.append(name)


class Validator(ast.NodeVisitor):
    def __init__(self) -> None:
        self.state = ValidationState()

    def validate(self, tree: ast.Module) -> list[str]:
        self._visit_block(tree.body)
        return self.state.variables

    def _visit_block(self, statements: list[ast.stmt]) -> set[str]:
        for statement in statements:
            self.visit(statement)
        return set(self.state.assigned)

    def _visit_block_with_assigned(
        self,
        statements: list[ast.stmt],
        assigned: set[str],
    ) -> set[str]:
        previous = self.state.assigned
        self.state.assigned = set(assigned)
        try:
            return self._visit_block(statements)
        finally:
            self.state.assigned = previous

    def generic_visit(self, node: ast.AST) -> None:
        raise CompileError(f"Unsupported syntax at {_line_of(node)}: {type(node).__name__}")

    def visit_Module(self, node: ast.Module) -> None:
        self._visit_block(node.body)

    def visit_Assign(self, node: ast.Assign) -> None:
        if len(node.targets) != 1 or not isinstance(node.targets[0], ast.Name):
            raise CompileError(f"Only simple name assignment is supported at {_line_of(node)}")
        self.visit(node.value)
        name = node.targets[0].id
        self.state.remember_variable(name)
        self.state.assigned.add(name)

    def visit_AugAssign(self, node: ast.AugAssign) -> None:
        if not isinstance(node.target, ast.Name):
            raise CompileError(f"Only simple name updates are supported at {_line_of(node)}")
        self._validate_operator(node.op)
        if node.target.id not in self.state.assigned:
            raise CompileError(
                f"Variable '{node.target.id}' used before assignment at {_line_of(node)}"
            )
        self.visit(node.value)
        self.state.remember_variable(node.target.id)

    def visit_Expr(self, node: ast.Expr) -> None:
        if not isinstance(node.value, ast.Call):
            raise CompileError(f"Only print calls are allowed as expressions at {_line_of(node)}")
        self.visit(node.value)

    def visit_Call(self, node: ast.Call) -> None:
        if not isinstance(node.func, ast.Name) or node.func.id != "print":
            raise CompileError(f"Only print(expr) is supported at {_line_of(node)}")
        if len(node.args) != 1 or node.keywords:
            raise CompileError(f"print expects exactly one positional argument at {_line_of(node)}")
        self.visit(node.args[0])

    def visit_If(self, node: ast.If) -> None:
        self.visit(node.test)
        before = set(self.state.assigned)
        body_after = self._visit_block_with_assigned(node.body, before)
        if node.orelse:
            else_after = self._visit_block_with_assigned(node.orelse, before)
            self.state.assigned = body_after & else_after
        else:
            self.state.assigned = before

    def visit_While(self, node: ast.While) -> None:
        if node.orelse:
            raise CompileError(f"while-else is not supported at {_line_of(node)}")
        self.visit(node.test)
        before = set(self.state.assigned)
        self._visit_block_with_assigned(node.body, before)
        self.state.assigned = before

    def visit_Name(self, node: ast.Name) -> None:
        if isinstance(node.ctx, ast.Load) and node.id not in self.state.assigned:
            raise CompileError(f"Variable '{node.id}' used before assignment at {_line_of(node)}")

    def visit_Constant(self, node: ast.Constant) -> None:
        if isinstance(node.value, bool):
            return
        if isinstance(node.value, int):
            return
        raise CompileError(f"Only integer and boolean literals are supported at {_line_of(node)}")

    def visit_BinOp(self, node: ast.BinOp) -> None:
        self._validate_operator(node.op)
        self.visit(node.left)
        self.visit(node.right)

    def visit_UnaryOp(self, node: ast.UnaryOp) -> None:
        if not isinstance(node.op, ast.USub):
            raise CompileError(f"Only unary minus is supported at {_line_of(node)}")
        self.visit(node.operand)

    def visit_Compare(self, node: ast.Compare) -> None:
        if len(node.ops) != 1 or len(node.comparators) != 1:
            raise CompileError(f"Chained comparisons are not supported at {_line_of(node)}")
        if not isinstance(
            node.ops[0],
            (ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE),
        ):
            raise CompileError(f"Unsupported comparison operator at {_line_of(node)}")
        self.visit(node.left)
        self.visit(node.comparators[0])

    def visit_BoolOp(self, node: ast.BoolOp) -> None:
        if not isinstance(node.op, (ast.And, ast.Or)):
            raise CompileError(f"Unsupported boolean operator at {_line_of(node)}")
        for value in node.values:
            self.visit(value)

    def _validate_operator(self, op: ast.AST) -> None:
        if not isinstance(op, (ast.Add, ast.Sub, ast.Mult, ast.FloorDiv, ast.Mod)):
            raise CompileError(f"Unsupported operator: {type(op).__name__}")


class CGenerator:
    def __init__(self, variables: list[str]) -> None:
        self.variables = variables

    def generate(self, tree: ast.Module) -> str:
        lines = [
            "/*",
            " * MD INDUSTRIES",
            " * Developer: M.DHANESVARAN",
            " * Generated by pyportcc",
            " */",
            "",
            "#include <stdio.h>",
            "#include <stdlib.h>",
            "",
            "static int py_floor_div(int left, int right) {",
            "    int quotient;",
            "    int remainder;",
            '    if (right == 0) { fprintf(stderr, "division by zero\\n"); exit(1); }',
            "    quotient = left / right;",
            "    remainder = left % right;",
            "    if (remainder != 0 && ((remainder > 0) != (right > 0))) {",
            "        quotient -= 1;",
            "    }",
            "    return quotient;",
            "}",
            "",
            "static int py_mod(int left, int right) {",
            "    int remainder;",
            '    if (right == 0) { fprintf(stderr, "modulo by zero\\n"); exit(1); }',
            "    remainder = left % right;",
            "    if (remainder != 0 && ((remainder > 0) != (right > 0))) {",
            "        remainder += right;",
            "    }",
            "    return remainder;",
            "}",
            "",
            "int main(void) {",
        ]
        if self.variables:
            for name in self.variables:
                lines.append(f"    int {name} = 0;")
            lines.append("")
        for statement in tree.body:
            lines.extend(self._emit_statement(statement, 1))
        lines.append("    return 0;")
        lines.append("}")
        lines.append("")
        return "\n".join(lines)

    def _emit_statement(self, node: ast.stmt, indent: int) -> list[str]:
        prefix = "    " * indent
        if isinstance(node, ast.Assign):
            target = node.targets[0]
            return [f"{prefix}{target.id} = {self._emit_expr(node.value)};"]
        if isinstance(node, ast.AugAssign):
            if isinstance(node.op, ast.FloorDiv):
                return [
                    f"{prefix}{node.target.id} = py_floor_div({node.target.id}, {self._emit_expr(node.value)});"
                ]
            if isinstance(node.op, ast.Mod):
                return [f"{prefix}{node.target.id} = py_mod({node.target.id}, {self._emit_expr(node.value)});"]
            op = _BINARY_OPERATORS[type(node.op)]
            return [f"{prefix}{node.target.id} {op}= {self._emit_expr(node.value)};"]
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            return [f'{prefix}printf("%d\\n", {self._emit_expr(node.value.args[0])});']
        if isinstance(node, ast.If):
            lines = [f"{prefix}if ({self._emit_expr(node.test)}) {{"]
            for statement in node.body:
                lines.extend(self._emit_statement(statement, indent + 1))
            if node.orelse:
                lines.append(f"{prefix}}} else {{")
                for statement in node.orelse:
                    lines.extend(self._emit_statement(statement, indent + 1))
            lines.append(f"{prefix}}}")
            return lines
        if isinstance(node, ast.While):
            lines = [f"{prefix}while ({self._emit_expr(node.test)}) {{"]
            for statement in node.body:
                lines.extend(self._emit_statement(statement, indent + 1))
            lines.append(f"{prefix}}}")
            return lines
        raise CompileError(f"Unsupported statement during code generation at {_line_of(node)}")

    def _emit_expr(self, node: ast.AST) -> str:
        if isinstance(node, ast.Constant):
            if isinstance(node.value, bool):
                return "1" if node.value else "0"
            return str(node.value)
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            return f"(-{self._emit_expr(node.operand)})"
        if isinstance(node, ast.BinOp):
            left = self._emit_expr(node.left)
            right = self._emit_expr(node.right)
            if isinstance(node.op, ast.FloorDiv):
                return f"py_floor_div({left}, {right})"
            if isinstance(node.op, ast.Mod):
                return f"py_mod({left}, {right})"
            op = _BINARY_OPERATORS[type(node.op)]
            return f"({left} {op} {right})"
        if isinstance(node, ast.Compare):
            op = _COMPARE_OPERATORS[type(node.ops[0])]
            return f"({self._emit_expr(node.left)} {op} {self._emit_expr(node.comparators[0])})"
        if isinstance(node, ast.BoolOp):
            joiner = " && " if isinstance(node.op, ast.And) else " || "
            return "(" + joiner.join(self._emit_expr(value) for value in node.values) + ")"
        raise CompileError(f"Unsupported expression during code generation at {_line_of(node)}")


_BINARY_OPERATORS = {
    ast.Add: "+",
    ast.Sub: "-",
    ast.Mult: "*",
    ast.Mod: "%",
}

_COMPARE_OPERATORS = {
    ast.Eq: "==",
    ast.NotEq: "!=",
    ast.Lt: "<",
    ast.LtE: "<=",
    ast.Gt: ">",
    ast.GtE: ">=",
}


def _parse_and_validate(source: str, filename: str) -> tuple[ast.Module, list[str]]:
    try:
        tree = ast.parse(source, filename=filename)
    except SyntaxError as exc:
        line = exc.lineno or "?"
        message = exc.msg or "invalid syntax"
        raise CompileError(f"Syntax error at line {line}: {message}") from exc

    validator = Validator()
    variables = validator.validate(tree)
    return tree, variables


def compile_source(source: str, filename: str = "<memory>") -> str:
    tree, variables = _parse_and_validate(source, filename)
    generator = CGenerator(variables)
    return generator.generate(tree)


def execute_source(source: str, filename: str = "<memory>", max_steps: int = 100_000) -> str:
    tree, _ = _parse_and_validate(source, filename)
    runtime = _Interpreter(max_steps=max_steps)
    runtime.run(tree)
    if not runtime.output_lines:
        return ""
    return "\n".join(runtime.output_lines) + "\n"


def compile_file(input_path: str, output_path: str) -> None:
    source_path = Path(input_path)
    output_file = Path(output_path)
    source = source_path.read_text(encoding="utf-8")
    generated = compile_source(source, filename=str(source_path))
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(generated, encoding="utf-8", newline="\n")


class _Interpreter:
    def __init__(self, max_steps: int) -> None:
        self.env: dict[str, int] = {}
        self.output_lines: list[str] = []
        self.max_steps = max_steps
        self.steps = 0

    def run(self, tree: ast.Module) -> None:
        self._run_block(tree.body)

    def _tick(self, node: ast.AST) -> None:
        self.steps += 1
        if self.steps > self.max_steps:
            raise ExecutionError(f"Maximum execution steps exceeded at {_line_of(node)}")

    def _run_block(self, statements: list[ast.stmt]) -> None:
        for statement in statements:
            self._run_statement(statement)

    def _run_statement(self, node: ast.stmt) -> None:
        self._tick(node)
        if isinstance(node, ast.Assign):
            target = node.targets[0]
            self.env[target.id] = self._eval_expr(node.value)
            return
        if isinstance(node, ast.AugAssign):
            name = node.target.id
            current = self.env[name]
            value = self._eval_expr(node.value)
            if isinstance(node.op, ast.Add):
                self.env[name] = current + value
                return
            if isinstance(node.op, ast.Sub):
                self.env[name] = current - value
                return
            if isinstance(node.op, ast.Mult):
                self.env[name] = current * value
                return
            if isinstance(node.op, ast.FloorDiv):
                self.env[name] = self._py_floor_div(current, value, node)
                return
            if isinstance(node.op, ast.Mod):
                self.env[name] = self._py_mod(current, value, node)
                return
            raise ExecutionError(f"Unsupported update operator at {_line_of(node)}")
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            rendered = self._eval_expr(node.value.args[0])
            self.output_lines.append(str(rendered))
            return
        if isinstance(node, ast.If):
            if self._eval_expr(node.test):
                self._run_block(node.body)
            else:
                self._run_block(node.orelse)
            return
        if isinstance(node, ast.While):
            while self._eval_expr(node.test):
                self._run_block(node.body)
            return
        raise ExecutionError(f"Unsupported statement during execution at {_line_of(node)}")

    def _eval_expr(self, node: ast.AST) -> int:
        self._tick(node)
        if isinstance(node, ast.Constant):
            if isinstance(node.value, bool):
                return 1 if node.value else 0
            return int(node.value)
        if isinstance(node, ast.Name):
            return self.env[node.id]
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            return -self._eval_expr(node.operand)
        if isinstance(node, ast.BinOp):
            left = self._eval_expr(node.left)
            right = self._eval_expr(node.right)
            if isinstance(node.op, ast.Add):
                return left + right
            if isinstance(node.op, ast.Sub):
                return left - right
            if isinstance(node.op, ast.Mult):
                return left * right
            if isinstance(node.op, ast.FloorDiv):
                return self._py_floor_div(left, right, node)
            if isinstance(node.op, ast.Mod):
                return self._py_mod(left, right, node)
        if isinstance(node, ast.Compare):
            left = self._eval_expr(node.left)
            right = self._eval_expr(node.comparators[0])
            op = node.ops[0]
            if isinstance(op, ast.Eq):
                return 1 if left == right else 0
            if isinstance(op, ast.NotEq):
                return 1 if left != right else 0
            if isinstance(op, ast.Lt):
                return 1 if left < right else 0
            if isinstance(op, ast.LtE):
                return 1 if left <= right else 0
            if isinstance(op, ast.Gt):
                return 1 if left > right else 0
            if isinstance(op, ast.GtE):
                return 1 if left >= right else 0
        if isinstance(node, ast.BoolOp):
            if isinstance(node.op, ast.And):
                return 1 if all(self._eval_expr(value) != 0 for value in node.values) else 0
            if isinstance(node.op, ast.Or):
                return 1 if any(self._eval_expr(value) != 0 for value in node.values) else 0
        raise ExecutionError(f"Unsupported expression during execution at {_line_of(node)}")

    def _py_floor_div(self, left: int, right: int, node: ast.AST) -> int:
        if right == 0:
            raise ExecutionError(f"division by zero at {_line_of(node)}")
        quotient = left // right
        return quotient

    def _py_mod(self, left: int, right: int, node: ast.AST) -> int:
        if right == 0:
            raise ExecutionError(f"modulo by zero at {_line_of(node)}")
        return left % right
