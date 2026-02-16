"""
JARVIS 5.0 - ReAct Agent (Reasoning + Acting)
==============================================
Sprint 4: Predictive & Autonomous
Loop ReAct explÃ­cito com Gemini function calling

USAGE: from src.core.react_agent import ReActAgent
"""

<<<<<<< Updated upstream
import sys
import os
from pathlib import Path
=======
import ast
>>>>>>> Stashed changes
import json
import logging
from typing import Dict, Optional, Any
from src.utils.logger_reflection import reflect_logger
from src.utils.safe_math import safe_eval

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SAFE_CODE_EXEC_BUILTINS = {
    "abs": abs,
    "len": len,
    "min": min,
    "max": max,
    "sum": sum,
    "sorted": sorted,
    "range": range,
    "round": round,
}

# Add project root
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    import google.generativeai as genai

    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    logger.warning("Google GenAI not available")


class ReActAgent:
    """
    ReAct Agent (Reasoning + Acting)

    Loop explÃ­cito:
    1. **Thought**: Raciocinar sobre prÃ³ximo passo
    2. **Action**: Escolher e executar tool
    3. **Observation**: Observar resultado
    4. Repeat atÃ© resposta final

    Max 5 iteraÃ§Ãµes para evitar loops infinitos

    Tools disponÃ­veis:
    - file_read: Ler arquivo
    - file_write: Escrever arquivo
    - web_search: Buscar na web (via Gemini)
    - vision_qa: Analisar imagem
    - code_exec: Executar cÃ³digo Python (sandbox)
    - calculate: Calcular expressÃ£o matemÃ¡tica
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model="gemini-2.0-flash-exp",
        max_iterations=5,
    ):
        """
        Args:
            api_key: Google API key
            model: Gemini model
            max_iterations: Max reasoning loops
        """
        self.model_name = model
        self.max_iterations = max_iterations
        self.model = None
        self.chat = None

        if not GENAI_AVAILABLE:
            logger.error("Google GenAI not available")
            return

        # Get API key
        if api_key:
            self.api_key = api_key
        else:
            self.api_key = os.getenv("GEMINI_API_KEY")

        if not self.api_key:
            logger.warning(
                "âš ï¸ No Gemini API key provided - ReAct Agent will operate in LOCAL mode only."
            )
            return  # Local reasoning handled in run() fallback

        # Configure
        try:
            genai.configure(api_key=self.api_key)

            # Define tools (function declarations)
            function_declarations = [
                {
                    "name": "file_read",
                    "description": "Read contents of a file",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "File path to read",
                            }
                        },
                        "required": ["path"],
                    },
                },
                {
                    "name": "file_write",
                    "description": "Write content to a file",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "File path to write",
                            },
                            "content": {
                                "type": "string",
                                "description": "Content to write",
                            },
                        },
                        "required": ["path", "content"],
                    },
                },
                {
                    "name": "web_search",
                    "description": "Search the web for information",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Search query"}
                        },
                        "required": ["query"],
                    },
                },
                {
                    "name": "calculate",
                    "description": "Evaluate mathematical expression",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "expression": {
                                "type": "string",
                                "description": 'Math expression (e.g., "2+2*3")',
                            }
                        },
                        "required": ["expression"],
                    },
                },
                {
                    "name": "code_exec",
                    "description": "Execute Python code in sandbox (safe)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "code": {
                                "type": "string",
                                "description": "Python code to execute",
                            }
                        },
                        "required": ["code"],
                    },
                },
            ]

            # Create model with tools (Corrected format for SDK)
            try:
<<<<<<< Updated upstream
                from google.ai.generativelanguage_v1beta.types import Tool
<<<<<<< HEAD
                # If we could import Tool, we might structure it differently, 
=======
                from google.ai.generativelanguage_v1beta.types import Tool  # noqa: F401

                # If we could import Tool, we might structure it differently,
>>>>>>> Stashed changes
=======

                # If we could import Tool, we might structure it differently,
>>>>>>> dev-new-version
                # but standard dict typically works if schema is perfect.
            except ImportError:
                pass

            self.model = genai.GenerativeModel(
                model_name=model,
                tools=[{"function_declarations": function_declarations}],
            )

            self.tools_list = [t["name"] for t in function_declarations]
            logger.info(
                f"âœ… ReAct Agent initialized ({model}, {len(function_declarations)} tools)"
            )

        except Exception as e:
            logger.info(
                f"â„¹ï¸ ReAct Agent (Gemini) indisponÃ­vel: {e}. Usando Local Brain."
            )
            self.model = None
            self.tools_list = []

    def _execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> str:
        """
        Execute tool function

        Args:
            tool_name: Tool to execute
            parameters: Tool parameters

        Returns:
            Tool output as string
        """
        logger.info(f"ðŸ”§ Executing tool: {tool_name}")
        logger.debug(f"   Parameters: {parameters}")

        try:
            if tool_name == "file_read":
                path = parameters["path"]
                if os.path.exists(path):
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()
                    return f"File content:\n{content[:1000]}"  # Limit output
                else:
                    return f"Error: File not found: {path}"

            elif tool_name == "file_write":
                path = parameters["path"]
                content = parameters["content"]
                Path(path).parent.mkdir(parents=True, exist_ok=True)
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)
                return f"Successfully wrote {len(content)} characters to {path}"

            elif tool_name == "web_search":
                query = parameters["query"]
                # Use Gemini for web search (simulated)
                return f"Web search results for '{query}':\n[Simulated: Top results would appear here]"

            elif tool_name == "calculate":
                expression = parameters["expression"]
                # Secure evaluation using safe_eval (AST-based)
                result = safe_eval(expression)
                return f"Result: {result}"
<<<<<<< HEAD
<<<<<<< Updated upstream
            
            elif tool_name == 'code_exec':
                code = parameters['code']
=======

            elif tool_name == "code_exec":
                code = parameters["code"]
>>>>>>> dev-new-version
                # Execute in restricted namespace (sandbox)
                namespace = {}
                exec(code, {"__builtins__": {}}, namespace)
                return f"Executed successfully. Namespace: {namespace}"
<<<<<<< HEAD
            
=======

            elif tool_name == "code_exec":
                code = parameters["code"]
                return self._safe_code_exec(code)

>>>>>>> Stashed changes
=======

>>>>>>> dev-new-version
            else:
                return f"Error: Unknown tool '{tool_name}'"

        except Exception as e:
            return f"Error executing {tool_name}: {str(e)}"
<<<<<<< HEAD
<<<<<<< Updated upstream
    
=======

    def _validate_code_exec(self, code: str) -> Optional[str]:
        """Validate code_exec payload with strict AST and token checks."""
        if not isinstance(code, str) or not code.strip():
            return "Empty code payload."

        if len(code) > 500:
            return "Code payload too large."

        lowered = code.lower()
        forbidden_snippets = (
            "import ",
            "__",
            "open(",
            "exec(",
            "eval(",
            "compile(",
            "globals(",
            "locals(",
            "os.",
            "sys.",
            "subprocess",
            "socket",
            "pathlib",
        )
        if any(snippet in lowered for snippet in forbidden_snippets):
            return "Forbidden token detected in code payload."

        try:
            tree = ast.parse(code, mode="exec")
        except SyntaxError as exc:
            return f"Syntax error: {exc}"

        allowed_names = set(SAFE_CODE_EXEC_BUILTINS.keys()) | {"result"}
        forbidden_nodes = (
            ast.Import,
            ast.ImportFrom,
            ast.With,
            ast.Try,
            ast.Lambda,
            ast.ClassDef,
            ast.FunctionDef,
            ast.AsyncFunctionDef,
            ast.Attribute,
            ast.Delete,
            ast.Global,
            ast.Nonlocal,
            ast.Raise,
        )

        for node in ast.walk(tree):
            if isinstance(node, forbidden_nodes):
                return f"Forbidden syntax: {type(node).__name__}"

            if isinstance(node, ast.Call):
                if not isinstance(node.func, ast.Name):
                    return "Only direct safe built-in calls are allowed."
                if node.func.id not in SAFE_CODE_EXEC_BUILTINS:
                    return f"Function '{node.func.id}' is not allowed."

            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                if node.id not in allowed_names:
                    return f"Identifier '{node.id}' is not allowed."

        return None

    def _safe_code_exec(self, code: str) -> str:
        """Execute tightly-scoped code with an allowlisted built-in namespace."""
        validation_error = self._validate_code_exec(code)
        if validation_error:
            return f"Error executing code_exec: {validation_error}"

        namespace: Dict[str, Any] = {}
        compiled = compile(ast.parse(code, mode="exec"), "<safe_code_exec>", "exec")
        # Exec é usado intencionalmente **após** validação estrita via AST e allowlist.
        # Builtins são restritos em SAFE_CODE_EXEC_BUILTINS; capturamos exceções de
        # tempo de execução para evitar crash da função.
        try:
            exec(
                compiled, {"__builtins__": SAFE_CODE_EXEC_BUILTINS}, namespace
            )  # nosec: validated by _validate_code_exec
        except Exception as e:
            logger.exception("Erro ao executar código seguro")
            return f"Error executing code_exec: {e}"

        serializable_types = (str, int, float, bool, list, dict, tuple, type(None))
        safe_namespace = {
            key: value
            for key, value in namespace.items()
            if not key.startswith("__") and isinstance(value, serializable_types)
        }

        return f"Executed successfully. Namespace: {safe_namespace}"

>>>>>>> Stashed changes
=======

>>>>>>> dev-new-version
    def run(self, task: str, verbose: bool = True) -> Dict[str, Any]:
        """
        Run ReAct loop (uses Gemini if available, otherwise fallback to LocalBrain)
        """
        if not self.model or not self.api_key:
            return self._run_local(task, verbose)

        # Original Gemini loop...
        if verbose:
            logger.info("=" * 70)
            logger.info("ðŸ¤– ReAct Agent Starting (GEMINI MODE)")
            logger.info("=" * 70)
            logger.info(f"ðŸ“‹ Task: {task}")
            logger.info("")

        # Start chat
        self.chat = self.model.start_chat()

        # System prompt
        system_prompt = f"""You are a ReAct agent. Follow this pattern:

**Thought**: Analyze the task and decide what to do next
**Action**: Choose a tool and parameters
**Observation**: Observe the tool result

Continue this loop until you can provide a final answer.
Available tools: {', '.join(self.tools_list)}

Task: {task}
"""

        steps = []
        iteration = 0

        try:
            # Send initial prompt
            response = self.chat.send_message(system_prompt)

            while iteration < self.max_iterations:
                iteration += 1

                if verbose:
                    logger.info(f"{'='*70}")
                    logger.info(f"ðŸ”„ Iteration {iteration}/{self.max_iterations}")
                    logger.info(f"{'='*70}")

                # Check if function call
                if response.candidates[0].content.parts[0].function_call:
                    # Extract function call
                    function_call = (
                        response.candidates[0].content.parts[0].function_call
                    )
                    tool_name = function_call.name
                    parameters = dict(function_call.args)

                    if verbose:
                        reflect_logger.reflect(
                            f"Analyzing function call for tool '{tool_name}'",
                            layer="LOGIC",
                        )
                        logger.info(f"ðŸ’­ Thought: Using tool '{tool_name}'")
                        logger.info(
                            f"ðŸ”§ Action: {tool_name}({json.dumps(parameters, indent=2)})"
                        )

                        # Explicitly log the thought for distillation
                        self.last_thought = (
                            f"Decided to use {tool_name} to address {task}"
                        )

                    # Execute tool
                    tool_result = self._execute_tool(tool_name, parameters)

                    if verbose:
                        logger.info(f"ðŸ‘ï¸  Observation: {tool_result[:200]}...")

                    steps.append(
                        {
                            "iteration": iteration,
                            "tool": tool_name,
                            "parameters": parameters,
                            "result": tool_result,
                        }
                    )

                    # Send result back to model
                    response = self.chat.send_message(
                        genai.types.content_types.FunctionResponse(
                            name=tool_name, response={"result": tool_result}
                        )
                    )

                else:
                    # Final answer
                    answer = response.text

                    if verbose:
                        logger.info(f"\n{'='*70}")
                        logger.info("âœ… Final Answer")
                        logger.info(f"{'='*70}")
                        logger.info(answer)
                        logger.info("")

                    return {
                        "success": True,
                        "answer": answer,
                        "iterations": iteration,
                        "steps": steps,
                    }

            # Max iterations reached
            if verbose:
                logger.warning(
                    f"âš ï¸  Max iterations ({self.max_iterations}) reached"
                )

            return {
                "success": False,
                "answer": "Max iterations reached without final answer",
                "iterations": iteration,
                "steps": steps,
            }

        except Exception as e:
            logger.error(f"ReAct error: {e}")
            return {
                "success": False,
                "answer": f"Error: {str(e)}",
                "iterations": iteration,
                "steps": steps,
            }

    def _run_local(self, task: str, verbose: bool = True) -> Dict[str, Any]:
        """
        Fallback Reasoning Loop using LocalBrain (Qwen 1.5B)
        """
        try:
            from src.core.intelligence.local_brain import local_brain

            if verbose:
                logger.info("=" * 70)
                logger.info("ðŸ¤– ReAct Agent Starting (LOCAL OFFLINE MODE)")
                logger.info("=" * 70)
                logger.info(f"ðŸ“‹ Task: {task}")

            # Simplified ReAct prompt for smaller models
            prompt = f"""You are JARVIS, an autonomous agent. Complete this task.
Task: {task}

Tools available: {', '.join(self.tools_list)}

Reason step-by-step and provide a FINAL ANSWER."""

            answer = local_brain.generate_response(
                prompt, system_prompt="You are JARVIS. Be efficient and direct."
            )

            reflect_logger.reflect(
                f"Local brain generating answer for: {task}", layer="OFFLINE_CORE"
            )

            return {
                "success": True,
                "answer": answer,
                "iterations": 1,
                "steps": [
                    {
                        "iteration": 1,
                        "thought": "Direct reasoning via LocalBrain",
                        "result": "Answer generated",
                    }
                ],
            }
        except Exception as e:
            logger.error(f"Local ReAct fallback failed: {e}")
            return {
                "success": False,
                "answer": f"Local error: {e}",
                "iterations": 0,
                "steps": [],
            }


# Example usage
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS ReAct Agent")
    parser.add_argument("--task", type=str, required=True, help="Task to complete")
    parser.add_argument("--api-key", type=str, help="Gemini API key")
    parser.add_argument("--max-iterations", type=int, default=5, help="Max iterations")

    args = parser.parse_args()

    # Create agent
    agent = ReActAgent(api_key=args.api_key, max_iterations=args.max_iterations)

    if not agent.model:
        print("âŒ Failed to initialize ReAct agent")
        sys.exit(1)

    # Run task
    result = agent.run(args.task, verbose=True)

    # Print summary
    print("\n" + "=" * 70)
    print("ðŸ“Š Summary")
    print("=" * 70)
    print(f"Success: {result['success']}")
    print(f"Iterations: {result['iterations']}")
    print(f"Steps taken: {len(result['steps'])}")
    print(f"\nFinal Answer:\n{result['answer']}")
