import re
import json


class ContextSanitizer:
    """Transforma dados tÃ©cnicos em linguagem natural para evitar 'alucinaÃ§Ãµes' tÃ©cnicas do LLM."""

    SANITIZATION_RULES = {
        # Caminhos do Windows (C:\Users\...) â†’ DescriÃ§Ãµes amigÃ¡veis
        r'[A-Za-z]:[/\\][^"\n]*[/\\]Users[/\\][^"\n]*[/\\]Documents[/\\][^"\n]*': "[Meus Documentos]",
        r'[A-Za-z]:[/\\][^"\n]*[/\\]Users[/\\][^"\n]*[/\\]': "[Pasta do UsuÃ¡rio]",
        r'[A-Za-z]:[/\\][^"\n]*[/\\]Windows[/\\][^"\n]*': "[Sistema Windows]",
        r'[A-Za-z]:[/\\][^"\n]*': "[Caminho de Arquivo]",
        # URLs e links â†’ DescriÃ§Ãµes (Exceto se for muito curto)
        r'https?://[^\s"\']{15,}': "[Link Online]",
        r'www\.[^\s"\']{15,}': "[Site]",
        # Comandos tÃ©cnicos â†’ Neutraliza
        r"cmd\.exe": "Prompt de Comando",
        r"powershell\.exe": "PowerShell",
        r"speak\([^)]*\)": "falar sobre isso",
        # IDs e hashes â†’ Remove
        r"PID: \d+": "[Processo]",
        r"0x[0-9a-fA-F]{4,}": "[EndereÃ§o de MemÃ³ria]",
        r"[a-f0-9]{32,}": "[Hash]",
    }

    @classmethod
    def sanitize_context(cls, raw_context: str) -> str:
        """Limpa completamente o contexto tÃ©cnico"""
        sanitized = raw_context
        for pattern, replacement in cls.SANITIZATION_RULES.items():
            sanitized = re.sub(
                pattern,
                replacement,
                sanitized,
                flags=re.IGNORECASE)

        # Remove mÃºltiplos espaÃ§os e linhas vazias
        sanitized = "\n".join(
            [line.strip() for line in sanitized.split("\n") if line.strip()]
        )

        return sanitized

    @classmethod
    def create_human_prompt(
        cls, user_input: str, technical_context: str or dict
    ) -> str:
        """Cria prompt humanizado para o LLM"""

        # Se for disct, converte para string
        if isinstance(technical_context, dict):
            context_str = json.dumps(
                technical_context, indent=2, ensure_ascii=False)
        else:
            context_str = str(technical_context)

        clean_context = cls.sanitize_context(context_str)

        return f"""VocÃª Ã© JARVIS, assistente pessoal do William.

REGRAS ABSOLUTAS DE VOZ:
1. Fale APENAS em portuguÃªs do Brasil.
2. NUNCA cite caminhos de arquivo (C:\\...), URLs ou cÃ³digos.
3. Use linguagem natural, culta e direta.
4. Se o contexto tiver "[Caminho de Arquivo]", diga apenas "o arquivo" ou "os dados".
5. Ignore detalhes tÃ©cnicos e foque na intenÃ§Ã£o do usuÃ¡rio.

Contexto Simplificado:
{clean_context}

UsuÃ¡rio: {user_input}

JARVIS:"""
