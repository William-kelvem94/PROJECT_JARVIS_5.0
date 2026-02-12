import re
import random
import logging

logger = logging.getLogger(__name__)

class AtomicVoiceFilter:
    """Filtro final que garante 100% voz natural, bloqueando falas técnicas."""
    
    WAKE_WORDS = [
        'jarvis', 'james', 'gerber', 'javis', 'jarvi', 'star', 'stark', 'singularity'
    ]
    
    _initialized = False

    @classmethod
    def _ensure_initialized(cls):
        """Garante que os apelidos customizados foram carregados"""
        if not cls._initialized:
            try:
                from src.utils.config import config
                custom = config.get_setting("audio.nicknames", [])
                for nick in custom:
                    nick_lower = nick.lower().strip()
                    if nick_lower and nick_lower not in cls.WAKE_WORDS:
                        cls.WAKE_WORDS.append(nick_lower)
            except Exception as e:
                logger.error(f"Erro ao carregar apelidos customizados: {e}")
            cls._initialized = True

    @classmethod
    def add_nickname(cls, nickname: str) -> bool:
        """Adiciona um novo apelido e persiste na configuração"""
        cls._ensure_initialized()
        nick_lower = nickname.lower().strip()
        if not nick_lower:
            return False
            
        if nick_lower not in cls.WAKE_WORDS:
            cls.WAKE_WORDS.append(nick_lower)
            
        try:
            from src.utils.config import config
            custom = config.get_setting("audio.nicknames", [])
            if nick_lower not in custom:
                custom.append(nick_lower)
                config.set_setting("audio.nicknames", custom)
                return True
        except Exception as e:
            logger.error(f"Erro ao salvar novo apelido: {e}")
            
        return False

    TECH_BLOCKLIST = [
        # Palavras técnicas em inglês que vazam com frequência
        'speak', 'say', 'tell', 'command', 'execute', 'run',
        'http', 'https', 'www', 'localhost', '127.0.0.1',
        'C:', 'D:', 'E:', 'F:', 'G:', 'Z:', 'program files',
        '\\', '//',
        
        # Termos de programação
        'function', 'method', 'class', 'object', 'variable',
        'array', 'list', 'dict', 'tuple', 'set',
        'import', 'export', 'require', 'include',
        'null', 'undefined', 'nan', 'void',
        
        # IDs e números técnicos
        'PID', 'UID', 'GUID', 'UUID',
        '0x', '0b', '0o'
    ]
    
    # Padrões que indicam fala "suja"
    PATTERN_BLOCKERS = [
        r'[a-zA-Z]:\\[^ ]+',  # Caminhos Windows
        r'/[^ ]+',            # Caminhos Unix
        r'\d+\.\d+\.\d+\.\d+', # IPs
        r'[a-f0-9]{32,}',     # Hashes
        r'_[a-z]+_',          # snake_case variables
        r'\(\)',              # Empty functions
    ]
    
    @classmethod
    def filter_response(cls, raw_response: str) -> str:
        """Filtra qualquer resquício técnico da resposta"""
        if not raw_response:
            return ""
            
        # 1. Verificação rápida - palavras bloqueadas
        lower_response = raw_response.lower()
        
        # Ignora blocklist se for uma frase muito curta e comum (ex: "Run" pode ser correr, mas aqui bloqueamos pelo contexto de IA)
        # Mas para garantir, vamos bloquear tudo que for estritamente técnico
        
        for blocked in cls.TECH_BLOCKLIST:
            # Verifica palavra exata para evitar falsos positivos (ex: "say" em "ensaiar")
            # Mas caminhos como C: são bloqueio imediato
            if blocked in lower_response:
                # Se for caminho de drive, é crítico
                if blocked[1] == ':' and len(blocked) == 2:
                     logger.warning(f"🔇 Filtro Atômico acionado: Drive Letter detectado ({blocked})")
                     return cls._generate_safe_fallback()
                
                # Para palavras comuns, verifica limites de palavra
                if re.search(r'\b' + re.escape(blocked) + r'\b', lower_response):
                    logger.warning(f"🔇 Filtro Atômico acionado: Termo técnico '{blocked}'")
                    # Tenta apenas remover a frase técnica se possível, ou fallback total
                    return cls._generate_safe_fallback()
        
        # 2. Verificação de padrões regex
        for pattern in cls.PATTERN_BLOCKERS:
            if re.search(pattern, raw_response, re.IGNORECASE):
                logger.warning(f"🔇 Filtro Atômico acionado: Padrão regex detectado")
                return cls._generate_safe_fallback()
        
        # 3. Limpeza de caracteres especiais soltos
        # Remove caracteres que não fazem sentido na fala (ex: *, #, _, @)
        clean_response = re.sub(r'[*_#@$]', '', raw_response)
        
        return clean_response.strip()
    
    @classmethod
    def has_wake_word(cls, text: str) -> bool:
        """Verifica se o nome do JARVIS ou palavra de ativação está presente na frase."""
        cls._ensure_initialized()
        if not text:
            return False
            
        lower_text = text.lower()
        # Verifica se alguma palavra de ativação está presente
        for word in cls.WAKE_WORDS:
            if word in lower_text:
                return True
        return False
    
    @staticmethod
    def _generate_safe_fallback() -> str:
        """Retorna uma resposta segura quando detecta técnico"""
        fallbacks = [
            "Analisei os dados técnicos solicitados.",
            "Processamento concluído com sucesso, senhor.",
            "As informações foram carregadas no sistema.",
            "Tenho os detalhes técnicos aqui, caso precise visualizar.",
            "Operação realizada. O sistema está estável."
        ]
        return random.choice(fallbacks)
