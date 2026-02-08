# ============================================================================
# JARVIS SINGULARITY - Code Generator (Phase 2: Auto-Programming)
# ============================================================================
# Gera e executa código Python sob demanda
# ============================================================================

import os
import sys
import ast
import logging
import subprocess
from typing import Optional, Dict, Any
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

# ============================================================================
# CODE GENERATOR
# ============================================================================
class CodeGenerator:
    """
    Gera código Python sob demanda usando LLM.
    
    CAPACIDADES:
    - Gerar scripts Python a partir de descrição
    - Validar sintaxe antes de executar
    - Salvar scripts gerados
    - Executar scripts com segurança
    """
    
    def __init__(self):
        """Inicializa o Code Generator"""
        logger.info("🔧 Inicializando Code Generator...")
        
        # Pasta para scripts gerados
        self.scripts_dir = Path("data/generated_scripts")
        self.scripts_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"✅ Code Generator online - Scripts em: {self.scripts_dir}")
    
    def generate_script(self, task_description: str, llm_client=None) -> Optional[str]:
        """
        Gera código Python a partir de descrição.
        
        Args:
            task_description: Descrição da tarefa
            llm_client: Cliente LLM (local_brain ou gemini)
        
        Returns:
            Código Python gerado ou None
        """
        try:
            # Prompt para geração de código
            prompt = f"""Você é um programador Python expert. Gere um script Python completo e funcional para a seguinte tarefa:

TAREFA: {task_description}

REQUISITOS:
1. Código deve ser completo e executável
2. Incluir imports necessários
3. Adicionar tratamento de erros
4. Incluir docstrings
5. Usar boas práticas Python
6. NÃO incluir markdown ou explicações, APENAS código Python puro

CÓDIGO:"""
            
            # Usar LLM para gerar código
            if llm_client:
                response = llm_client.generate(prompt)
                code = self._extract_code_from_response(response)
            else:
                logger.warning("⚠️ LLM não disponível - usando template básico")
                code = self._generate_basic_template(task_description)
            
            return code
        
        except Exception as e:
            logger.error(f"❌ Erro ao gerar script: {e}")
            return None
    
    def _extract_code_from_response(self, response: str) -> str:
        """Extrai código Python de resposta LLM"""
        # Remover markdown code blocks se existirem
        if "```python" in response:
            code = response.split("```python")[1].split("```")[0].strip()
        elif "```" in response:
            code = response.split("```")[1].split("```")[0].strip()
        else:
            code = response.strip()
        
        return code
    
    def _generate_basic_template(self, task: str) -> str:
        """Gera template básico quando LLM não disponível"""
        return f'''"""
Script gerado automaticamente pelo JARVIS
Tarefa: {task}
Data: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""

def main():
    """Função principal"""
    print("Script gerado pelo JARVIS")
    print(f"Tarefa: {task}")
    # TODO: Implementar lógica aqui
    pass

if __name__ == "__main__":
    main()
'''
    
    def validate_code(self, code: str) -> Dict[str, Any]:
        """
        Valida sintaxe do código Python.
        
        Args:
            code: Código Python
        
        Returns:
            Dict com 'valid' (bool) e 'error' (str ou None)
        """
        try:
            ast.parse(code)
            return {"valid": True, "error": None}
        except SyntaxError as e:
            return {
                "valid": False,
                "error": f"Erro de sintaxe na linha {e.lineno}: {e.msg}"
            }
        except Exception as e:
            return {
                "valid": False,
                "error": f"Erro ao validar: {str(e)}"
            }
    
    def save_script(self, code: str, filename: Optional[str] = None) -> Path:
        """
        Salva script gerado.
        
        Args:
            code: Código Python
            filename: Nome do arquivo (opcional)
        
        Returns:
            Path do arquivo salvo
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"script_{timestamp}.py"
        
        if not filename.endswith(".py"):
            filename += ".py"
        
        filepath = self.scripts_dir / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(code)
            
            logger.info(f"✅ Script salvo: {filepath}")
            return filepath
        
        except Exception as e:
            logger.error(f"❌ Erro ao salvar script: {e}")
            raise
    
    def execute_script(self, filepath: Path, timeout: int = 30) -> Dict[str, Any]:
        """
        Executa script Python.
        
        Args:
            filepath: Path do script
            timeout: Timeout em segundos
        
        Returns:
            Dict com stdout, stderr, returncode
        """
        try:
            result = subprocess.run(
                [sys.executable, str(filepath)],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "success": result.returncode == 0
            }
        
        except subprocess.TimeoutExpired:
            return {
                "stdout": "",
                "stderr": f"Script excedeu timeout de {timeout}s",
                "returncode": -1,
                "success": False
            }
        except Exception as e:
            return {
                "stdout": "",
                "stderr": str(e),
                "returncode": -1,
                "success": False
            }
    
    def generate_and_execute(
        self, 
        task_description: str,
        llm_client=None,
        auto_execute: bool = False
    ) -> Dict[str, Any]:
        """
        Pipeline completo: gera, valida, salva e opcionalmente executa.
        
        Args:
            task_description: Descrição da tarefa
            llm_client: Cliente LLM
            auto_execute: Se True, executa automaticamente
        
        Returns:
            Dict com código, filepath, validation, execution
        """
        result = {
            "code": None,
            "filepath": None,
            "validation": None,
            "execution": None
        }
        
        # 1. Gerar código
        logger.info(f"📝 Gerando código para: '{task_description}'")
        code = self.generate_script(task_description, llm_client)
        
        if not code:
            logger.error("❌ Falha ao gerar código")
            return result
        
        result["code"] = code
        
        # 2. Validar
        logger.info("🔍 Validando código...")
        validation = self.validate_code(code)
        result["validation"] = validation
        
        if not validation["valid"]:
            logger.error(f"❌ Código inválido: {validation['error']}")
            return result
        
        logger.info("✅ Código válido")
        
        # 3. Salvar
        try:
            filepath = self.save_script(code)
            result["filepath"] = str(filepath)
        except Exception as e:
            logger.error(f"❌ Erro ao salvar: {e}")
            return result
        
        # 4. Executar (se solicitado)
        if auto_execute:
            logger.info("▶️ Executando script...")
            execution = self.execute_script(filepath)
            result["execution"] = execution
            
            if execution["success"]:
                logger.info("✅ Script executado com sucesso")
            else:
                logger.error(f"❌ Erro na execução: {execution['stderr']}")
        
        return result


# ============================================================================
# SINGLETON INSTANCE
# ============================================================================
code_generator = CodeGenerator()
