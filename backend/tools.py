"""
Tool router and implementations:

- calculator: safe arithmetic via ast parsing (supports + - * / ** parentheses)
- file_writer: writes content to file within sandbox/apps or given safe path
- app_builder: simple web app generator (uses builder.generate_app)
- route_tool(step_text): simple heuristic router to pick a tool
"""
from __future__ import annotations
import ast
import operator as op
import os
from typing import Tuple

from . import builder, config, utils

logger = utils.logger

# Allowed operators mapping
_ALLOWED_OPERATORS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.USub: op.neg,
    ast.UAdd: op.pos,
    ast.Mod: op.mod,
}

def _eval_expr(node: ast.AST) -> float:
    if isinstance(node, ast.Num):  # type: ignore[attr-defined]
        return node.n  # type: ignore[attr-defined]
    if isinstance(node, ast.BinOp):
        left = _eval_expr(node.left)
        right = _eval_expr(node.right)
        oper = _ALLOWED_OPERATORS[type(node.op)]
        return oper(left, right)
    if isinstance(node, ast.UnaryOp):
        operand = _eval_expr(node.operand)
        oper = _ALLOWED_OPERATORS[type(node.op)]
        return oper(operand)
    raise ValueError("Unsupported expression node: %r" % node)

def calculator(expression: str) -> str:
    """Safe evaluation of arithmetic expressions using ast."""
    try:
        tree = ast.parse(expression, mode="eval")
        # Validate nodes
        result = _eval_expr(tree.body)  # type: ignore[attr-defined]
        return str(result)
    except Exception as exc:
        logger.exception("Calculator error")
        return f"Calculator error: {exc}"

def _safe_path_join(base: str, target: str) -> str:
    """Prevent path traversal; ensure target inside base."""
    base_path = os.path.abspath(base)
    joined = os.path.abspath(os.path.join(base_path, target))
    if not joined.startswith(base_path):
        raise ValueError("Attempted path traversal")
    return joined

def file_writer(relative_path: str, content: str) -> str:
    """
    Writes content to a file inside the sandbox/apps directory by default.
    relative_path is path relative to sandbox/apps to prevent escaping.
    """
    base = config.SANDBOX_DIR
    full_path = _safe_path_join(base, relative_path)
    d = os.path.dirname(full_path)
    os.makedirs(d, exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)
    logger.info("Wrote file: %s", full_path)
    return full_path

def app_builder(step_text: str) -> str:
    """
    Interpret the step_text to produce an app name/description and call builder.generate_app.
    """
    # Very naive parsing: treat entire step_text as app name or "build app: NAME"
    if ":" in step_text:
        parts = step_text.split(":", 1)
        name = parts[1].strip()
    else:
        # fallback to first 6 words
        name = " ".join(step_text.split()[:6]).strip() or "AI App"
    path = builder.generate_app(name=name, description=f"Auto-generated for step: {step_text}")
    return path

def route_tool(step_text: str) -> Tuple[str, str]:
    """
    Decide which tool to run based on step_text, run it, and return (tool_name, result).
    Heuristics:
    - if 'calculate' or math expression detected -> calculator
    - if 'write' or 'create file' -> file_writer
    - if 'build' and 'app' -> app_builder
    - default: echo the step as unhandled
    """
    st = step_text.lower()
    # detect straightforward math: digits and math operators
    if any(token in st for token in ("calculate", "compute")) or any(ch in st for ch in "+-*/%*"):
        # extract expression heuristically
        expr = step_text
        # try to extract after 'calculate' or 'compute'
        for kw in ("calculate", "compute"):
            if kw in st:
                expr = step_text.lower().split(kw, 1)[-1].strip(" :")
                break
        result = calculator(expr)
        return "calculator", result

    if "build" in st and "app" in st:
        path = app_builder(step_text)
        return "app_builder", f"app generated at {path}"

    if any(kw in st for kw in ("write file", "create file", "save to", "write to")):
        # naive parse to get target path and content
        # format expected: "write file: path -> content"
        if ":" in step_text:
            _, rest = step_text.split(":", 1)
            if "->" in rest:
                target, content = rest.split("->", 1)
                target = target.strip()
                content = content.strip()
            else:
                # fallback - write a simple note
                target = rest.strip().split()[0]
                content = rest.strip()
        else:
            target = "note.txt"
            content = step_text
        try:
            fp = file_writer(target, content)
            return "file_writer", f"wrote file at {fp}"
        except Exception as exc:
            return "file_writer", f"failed to write file: {exc}"

    # default: echo
    return "echo", f"no tool matched; echoing step: {step_text}"
