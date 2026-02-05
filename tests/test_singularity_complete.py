"""
Testes Completos do JARVIS Singularity
"""

import pytest
import asyncio
from pathlib import Path
import os

# Configurar variáveis de ambiente para testes
os.environ["GROQ_API_KEY"] = "test_key"
os.environ["GEMINI_API_KEY"] = "test_key"

class TestHiveMind:
    """Testes do Hive Mind"""
    
    def test_memory_manager(self):
        """Testa gerenciador de memória"""
        from jarvis_core.hive_mind import hybrid_memory
        
        # Armazenar memória curta
        hybrid_memory.store_short_term("user", "Teste de memória")
        
        # Verificar contexto
        context = hybrid_memory.get_context()
        assert len(context) > 0
        assert context[-1]["content"] == "Teste de memória"
        
        # Limpar
        hybrid_memory.clear_short_term()
        assert len(hybrid_memory.get_context()) == 0
    
    def test_context_sync(self):
        """Testa sincronização de contexto"""
        from jarvis_core.hive_mind.context_sync import context_sync
        
        # Salvar contexto
        test_context = {
            "last_command": "teste",
            "current_task": "testing"
        }
        
        result = context_sync.save_context("test_device", test_context)
        assert result == True
        
        # Carregar contexto
        loaded = context_sync.load_context()
        assert loaded is not None
        assert loaded["last_command"] == "teste"


class TestBrain:
    """Testes do Brain"""
    
    def test_context_manager(self):
        """Testa gerenciador de contexto"""
        from jarvis_core.brain.context_manager import context_manager
        
        # Limpar contexto
        context_manager.clear_context()
        
        # Adicionar mensagens
        context_manager.add_message("user", "Olá")
        context_manager.add_message("assistant", "Olá! Como posso ajudar?")
        
        # Verificar
        context = context_manager.get_context()
        assert len(context) == 2
        assert context[0]["role"] == "user"
        assert context[1]["role"] == "assistant"
    
    @pytest.mark.asyncio
    async def test_neural_router_decision(self):
        """Testa decisão do router"""
        from jarvis_core.brain import get_router, ModelType
        
        router = get_router()
        
        # Teste 1: Conversa simples → Groq
        model = router.decide_model("Olá!")
        assert model == ModelType.GROQ_FAST
        
        # Teste 2: Análise complexa → Gemini Pro
        model = router.decide_model("Analise detalhadamente este código e explique...")
        assert model == ModelType.GEMINI_PRO
        
        # Teste 3: Imagem → Gemini Vision
        model = router.decide_model("O que há nesta imagem?", {"has_image": True})
        assert model == ModelType.GEMINI_VISION


class TestSenses:
    """Testes dos Senses"""
    
    def test_vision_system(self):
        """Testa sistema de visão"""
        from jarvis_core.senses.vision_hybrid import vision_system
        
        # Criar imagem de teste
        test_image = Path("data/temp/test_image.png")
        test_image.parent.mkdir(parents=True, exist_ok=True)
        
        # Criar imagem simples
        from PIL import Image
        img = Image.new('RGB', (100, 100), color='red')
        img.save(test_image)
        
        # Testar análise nível 1
        result = vision_system.analyze(str(test_image), level="fast")
        assert "width" in result
        assert "height" in result
        assert result["level"] == "fast"
    
    def test_action_dispatcher(self):
        """Testa dispatcher de ações"""
        from jarvis_core.senses import action_dispatcher
        
        # Verificar estatísticas iniciais
        stats = action_dispatcher.get_stats()
        assert "ui_automation_success" in stats


class TestMouth:
    """Testes do Mouth"""
    
    def test_voice_modulation(self):
        """Testa modulação de voz"""
        from jarvis_core.mouth.voice_modulation import voice_modulation
        
        # Testar detecção de emoção
        emotion = voice_modulation.detect_emotion_from_text("Isso é urgente!")
        assert emotion == "serious"
        
        emotion = voice_modulation.detect_emotion_from_text("Parabéns!")
        assert emotion == "excited"
        
        # Testar modulação
        voice_modulation.set_emotion("happy")
        params = voice_modulation.get_modulation_params()
        assert params["rate"] > 1.0


class TestGuardian:
    """Testes do Guardian"""
    
    def test_privacy_filter(self):
        """Testa filtro de privacidade"""
        from jarvis_core.guardian import privacy_filter
        
        # Testar CPF
        text = "Meu CPF é 123.456.789-00"
        filtered, types = privacy_filter.filter_text(text)
        assert "CPF_REDACTED" in filtered
        assert "cpf" in types
        
        # Testar email
        text = "Email: teste@example.com"
        filtered, types = privacy_filter.filter_text(text)
        assert "EMAIL_REDACTED" in filtered
        assert "email" in types
    
    def test_health_monitor(self):
        """Testa monitor de saúde"""
        from jarvis_core.guardian.health_monitor import health_monitor
        
        # Verificar CPU
        cpu = health_monitor.check_cpu()
        assert 0 <= cpu <= 100
        
        # Verificar memória
        mem = health_monitor.check_memory()
        assert "percent" in mem
        assert 0 <= mem["percent"] <= 100
        
        # Verificar score
        score = health_monitor.get_health_score()
        assert 0 <= score <= 100
    
    def test_safe_mode(self):
        """Testa safe mode"""
        from jarvis_core.guardian.safe_mode import safe_mode
        
        # Testar diagnósticos
        results = safe_mode.run_diagnostics()
        assert "imports" in results
        assert "config" in results
        assert "memory" in results


class TestInterface:
    """Testes da Interface"""
    
    def test_theme_manager(self):
        """Testa gerenciador de temas"""
        from jarvis_core.interface.theme_manager import theme_manager
        
        # Listar temas
        themes = theme_manager.list_themes()
        assert "iron_man" in themes
        assert "jarvis" in themes
        
        # Trocar tema
        result = theme_manager.set_theme("matrix")
        assert result == True
        
        # Verificar cor
        color = theme_manager.get_color("primary")
        assert color == "#00FF00"
    
    def test_notification_system(self):
        """Testa sistema de notificações"""
        from jarvis_core.interface.notification_system import notification_system, NotificationType
        
        # Limpar notificações
        notification_system.clear_all()
        
        # Adicionar notificação
        notification_system.info("Teste")
        
        # Verificar
        active = notification_system.get_active()
        assert len(active) > 0


class TestWorld:
    """Testes do World"""
    
    def test_automation_scenes(self):
        """Testa cenas de automação"""
        from jarvis_core.world.automation_scenes import automation_scenes
        
        # Listar cenas
        scenes = automation_scenes.list_scenes()
        assert len(scenes) > 0
        assert any("party_mode" in s for s in scenes)
        
        # Criar cena customizada
        automation_scenes.create_scene("test_scene", "Teste", [
            {"action": "test", "params": {}}
        ])
        
        scenes = automation_scenes.list_scenes()
        assert any("test_scene" in s for s in scenes)


# Executar testes
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
