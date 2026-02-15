import re
import random
import logging

logger = logging.getLogger(__name__)

class AtomicVoiceFilter:
    """Filtro final que garante 100% voz natural, bloqueando falas tÃ©cnicas."""
    
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
        """Adiciona um novo apelido persistente."""
        cls._ensure_initialized()
        nick_lower = nickname.lower().strip()
        if not nick_lower or nick_lower in cls.WAKE_WORDS:
            return False
            
        cls.WAKE_WORDS.append(nick_lower)
        try:
            from src.utils.config import config
            current = config.get_setting("audio.nicknames", [])
            if nick_lower not in current:
                current.append(nick_lower)
                config.set_setting("audio.nicknames", current)
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar apelido: {e}")
            return False

    @classmethod
    def set_primary_name(cls, name: str) -> bool:
        """Define um novo nome primário (prioridade na lista)."""
        cls._ensure_initialized()
        name_lower = name.lower().strip()
        if not name_lower: return False
        
        if name_lower in cls.WAKE_WORDS:
            cls.WAKE_WORDS.remove(name_lower)
        cls.WAKE_WORDS.insert(0, name_lower)
            
        try:
            from src.utils.config import config
            config.set_setting("audio.primary_name", name_lower)
            return True
        except Exception as e:
            logger.error(f"Erro ao definir nome primário: {e}")
            return False

    TECH_BLOCKLIST = [
        # Palavras tÃ©cnicas em inglÃªs que vazam com frequÃªncia
        'speak', 'say', 'tell', 'command', 'execute', 'run',
        'http', 'https', 'www', 'localhost', '127.0.0.1',
        'C:', 'D:', 'E:', 'F:', 'G:', 'Z:', 'program files',
        '\\', '//',
        
        # Termos de programaÃ§Ã£o
        'function', 'method', 'class', 'object', 'variable',
        'array', 'list', 'dict', 'tuple', 'set',
        'import', 'export', 'require', 'include',
        'null', 'undefined', 'nan', 'void',
        
        # IDs e nÃºmeros tÃ©cnicos
        'PID', 'UID', 'GUID', 'UUID',
        '0x', '0b', '0o'
    ]
    
    # PadrÃµes que indicam fala "suja"
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
        """Filtra qualquer resquÃ­cio tÃ©cnico da resposta"""
        if not raw_response:
            return ""
            
        # 1. VerificaÃ§Ã£o rÃ¡pida - palavras bloqueadas
        lower_response = raw_response.lower()
        
        # Ignora blocklist se for uma frase muito curta e comum (ex: "Run" pode ser correr, mas aqui bloqueamos pelo contexto de IA)
        # Mas para garantir, vamos bloquear tudo que for estritamente tÃ©cnico
        
        for blocked in cls.TECH_BLOCKLIST:
            # Verifica palavra exata para evitar falsos positivos (ex: "say" em "ensaiar")
            # Mas caminhos como C: sÃ£o bloqueio imediato
            if blocked in lower_response:
                # Se for caminho de drive, Ã© crÃ­tico
                if blocked[1] == ':' and len(blocked) == 2:
                     logger.warning(f"ðŸ”‡ Filtro AtÃ´mico acionado: Drive Letter detectado ({blocked})")
                     return cls._generate_safe_fallback()
                
                # Para palavras comuns, verifica limites de palavra
                if re.search(r'\b' + re.escape(blocked) + r'\b', lower_response):
                    logger.warning(f"ðŸ”‡ Filtro AtÃ´mico acionado: Termo tÃ©cnico '{blocked}'")
                    # Tenta apenas remover a frase tÃ©cnica se possÃ­vel, ou fallback total
                    return cls._generate_safe_fallback()
        
        # 2. VerificaÃ§Ã£o de padrÃµes regex
        for pattern in cls.PATTERN_BLOCKERS:
            if re.search(pattern, raw_response, re.IGNORECASE):
                logger.warning(f"ðŸ”‡ Filtro AtÃ´mico acionado: PadrÃ£o regex detectado")
                return cls._generate_safe_fallback()
        
        # 3. Limpeza de caracteres especiais soltos
        # Remove caracteres que nÃ£o fazem sentido na fala (ex: *, #, _, @)
        clean_response = re.sub(r'[*_#@$]', '', raw_response)
        
        return clean_response.strip()
    
    @classmethod
    def has_wake_word(cls, text: str) -> bool:
        """Verifica se o nome do JARVIS ou palavra de ativaÃ§Ã£o estÃ¡ presente na frase."""
        cls._ensure_initialized()
        if not text:
            return False
            
        lower_text = text.lower()
        # Verifica se alguma palavra de ativaÃ§Ã£o estÃ¡ presente
        for word in cls.WAKE_WORDS:
            if word in lower_text:
                return True
        return False
    
    @staticmethod
    def _generate_safe_fallback() -> str:
        """Retorna uma resposta segura quando detecta tÃ©cnico"""
        fallbacks = [
            "Analisei os dados tÃ©cnicos solicitados.",
            "Processamento concluÃ­do com sucesso, senhor.",
            "As informaÃ§Ãµes foram carregadas no sistema.",
            "Tenho os detalhes tÃ©cnicos aqui, caso precise visualizar.",
            "OperaÃ§Ã£o realizada. O sistema estÃ¡ estÃ¡vel."
        ]
        return random.choice(fallbacks)
