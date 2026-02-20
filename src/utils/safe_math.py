import ast
import operator
import math
from typing import Any, Union, List, Tuple


def safe_eval(expression: str) -> Union[int, float, List, Tuple]:
    """
    Safely evaluate a mathematical expression string using Python's AST.

    This function parses the expression into an Abstract Syntax Tree (AST) and
    recursively evaluates it, allowing only a specific set of operators and functions.
    This prevents arbitrary code execution vulnerabilities associated with `eval()`.

    Args:
        expression (str): The mathematical expression to evaluate.

    Returns:
        Union[int, float, List, Tuple]: The result of the evaluation.

    Raises:
        ValueError: If the expression contains disallowed nodes, functions, or operators.
        SyntaxError: If the expression is invalid syntax.
    """

    # Allowed operators mapping
    operators = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Pow: operator.pow,
        ast.Mod: operator.mod,
        ast.BitXor: operator.xor,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
    }

    # Allowed functions mapping
    functions = {
        "abs": abs,
        "round": round,
        "min": min,
        "max": max,
        "sum": sum,
        "pow": pow,
        "sqrt": math.sqrt,
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "log": math.log,
        "exp": math.exp,
        "ceil": math.ceil,
        "floor": math.floor,
        "factorial": math.factorial,
        "degrees": math.degrees,
        "radians": math.radians,
    }

    # Allowed constants mapping
    constants = {
        "pi": math.pi,
        "e": math.e,
        "tau": math.tau,
        "inf": math.inf,
        "nan": math.nan,
    }

    def _eval(node: Any) -> Any:
        if isinstance(node, ast.Constant):  # Python 3.8+
            if isinstance(node.value, (int, float)):
                return node.value
            raise ValueError(f"Constant type {type(node.value)} not allowed")

        elif isinstance(node, ast.Num):  # Older python
            return node.n

        elif isinstance(node, ast.Name):
            if node.id in constants:
                return constants[node.id]
            raise ValueError(f"Variable '{node.id}' not allowed")

        elif isinstance(node, ast.List):
            return [_eval(elt) for elt in node.elts]

        elif isinstance(node, ast.Tuple):
            return tuple(_eval(elt) for elt in node.elts)

        elif isinstance(node, ast.BinOp):
            left = _eval(node.left)
            right = _eval(node.right)
            # Handle operator lookup
            op_type = type(node.op)
            if op_type in operators:
                try:
                    return operators[op_type](left, right)
                except ZeroDivisionError:
                    raise ValueError("Division by zero")
                except OverflowError:
                    raise ValueError("Result too large")
            raise ValueError(f"Operator {op_type.__name__} not allowed")

        elif isinstance(node, ast.UnaryOp):
            operand = _eval(node.operand)
            op_type = type(node.op)
            if op_type in operators:
                return operators[op_type](operand)
            raise ValueError(f"Operator {op_type.__name__} not allowed")

        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
                if func_name in functions:
                    # Recursively evaluate all arguments
                    args = [_eval(arg) for arg in node.args]
                    try:
                        return functions[func_name](*args)
                    except Exception as e:
                        raise ValueError(f"Error calling {func_name}: {str(e)}")
                raise ValueError(f"Function '{func_name}' not allowed")
            raise ValueError("Call to non-named function not allowed")

        elif isinstance(node, ast.Expression):
            return _eval(node.body)

        else:
            raise ValueError(f"Node type {type(node).__name__} not allowed")

    # Limit expression length to prevent DoS via extremely long strings
    if len(expression) > 1000:
        raise ValueError("Expression too long")

    try:
        # Parse the expression into an AST
        node = ast.parse(expression.strip(), mode="eval")
        return _eval(node.body)
    except (SyntaxError, ValueError, TypeError) as e:
        raise ValueError(f"Invalid expression: {str(e)}")
    except Exception as e:
        # Catch-all for other potential errors during evaluation
        raise ValueError(f"Evaluation error: {str(e)}")
