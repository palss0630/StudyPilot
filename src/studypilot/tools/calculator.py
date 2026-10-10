"""Safe calculator tool using AST."""
import ast
import operator
import math
import traceback
from typing import Any

from src.studypilot.config import logger

_SAFE_NAMES = {
    "abs": abs,
    "round": round,
    "min": min,
    "max": max,
    "pow": pow,
    "sqrt": math.sqrt,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "log": math.log,
    "log10": math.log10,
    "log2": math.log2,
    "pi": math.pi,
    "e": math.e,
    "ceil": math.ceil,
    "floor": math.floor,
    "factorial": math.factorial
}

class SafeEvaluator(ast.NodeVisitor):
    def visit_Constant(self, node: ast.Constant) -> Any:
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError(f"Unsupported constant type: {type(node.value)}")

    def visit_Name(self, node: ast.Name) -> Any:
        if node.id in _SAFE_NAMES and isinstance(_SAFE_NAMES[node.id], (int, float)):
            return _SAFE_NAMES[node.id]
        raise ValueError(f"Disallowed name: {node.id}")

    def visit_UnaryOp(self, node: ast.UnaryOp) -> Any:
        operand = self.visit(node.operand)
        if isinstance(node.op, ast.UAdd):
            return +operand
        elif isinstance(node.op, ast.USub):
            return -operand
        raise ValueError(f"Unsupported unary operator: {type(node.op)}")

    def visit_BinOp(self, node: ast.BinOp) -> Any:
        left = self.visit(node.left)
        right = self.visit(node.right)
        
        if isinstance(node.op, ast.Add):
            return left + right
        elif isinstance(node.op, ast.Sub):
            return left - right
        elif isinstance(node.op, ast.Mult):
            return left * right
        elif isinstance(node.op, ast.Div):
            return left / right
        elif isinstance(node.op, ast.FloorDiv):
            return left // right
        elif isinstance(node.op, ast.Mod):
            return left % right
        elif isinstance(node.op, ast.Pow):
            if left > 1000 or right > 100:
                raise ValueError("Power operation operands too large")
            return left ** right
        raise ValueError(f"Unsupported binary operator: {type(node.op)}")

    def visit_Compare(self, node: ast.Compare) -> Any:
        # Simplistic compare for safety if needed, or reject entirely.
        # Allowing basic eq, lt, gt
        left = self.visit(node.left)
        for op, comp in zip(node.ops, node.comparators):
            right = self.visit(comp)
            if isinstance(op, ast.Eq):
                left = left == right
            elif isinstance(op, ast.NotEq):
                left = left != right
            elif isinstance(op, ast.Lt):
                left = left < right
            elif isinstance(op, ast.LtE):
                left = left <= right
            elif isinstance(op, ast.Gt):
                left = left > right
            elif isinstance(op, ast.GtE):
                left = left >= right
            else:
                raise ValueError(f"Unsupported comparison operator: {type(op)}")
            if not left:
                return False
        return left

    def visit_Call(self, node: ast.Call) -> Any:
        if not isinstance(node.func, ast.Name):
            raise ValueError("Unsupported function call")
            
        func_name = node.func.id
        if func_name not in _SAFE_NAMES or isinstance(_SAFE_NAMES[func_name], (int, float)):
            raise ValueError(f"Disallowed function: {func_name}")
            
        func = _SAFE_NAMES[func_name]
        args = [self.visit(arg) for arg in node.args]
        return func(*args)

    def visit_Expression(self, node: ast.Expression) -> Any:
        return self.visit(node.body)

    def generic_visit(self, node: ast.AST) -> Any:
        raise ValueError(f"Unsupported node type: {type(node)}")


def calculator(expression: str) -> str:
    """Safely evaluate a mathematical expression."""
    try:
        tree = ast.parse(expression, mode='eval')
        evaluator = SafeEvaluator()
        result = evaluator.visit(tree)
        return str(result)
    except Exception as e:
        logger.error(f"Calculator error for '{expression}': {e}\n{traceback.format_exc()}")
        return f"Error evaluating expression: {e}"
