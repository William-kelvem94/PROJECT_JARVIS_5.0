"""
Testes para os novos módulos do JARVIS 5.0
"""

import pytest
import sys
import os

# Adicionar path do projeto
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class TestSemanticMemory:
    """Testes para SemanticMemory."""
    
    def test_import(self):
        """Testa se módulo pode ser importado."""
        try:
            from modules.memory.semantic_memory import SemanticMemory
            assert True
        except ImportError as e:
            pytest.skip(f"Dependências não instaladas: {e}")
    
    def test_initialization_without_dependencies(self):
        """Testa inicialização sem dependências."""
        try:
            from modules.memory.semantic_memory import SemanticMemory
            memory = SemanticMemory()
            pytest.fail("Deveria lançar erro sem dependências")
        except ImportError:
            assert True  # Esperado quando dependências não instaladas


class TestSecurityModule:
    """Testes para SecurityManager."""
    
    def test_import(self):
        """Testa se módulo pode ser importado."""
        from modules.system.security_module import SecurityManager, PermissionLevel
        assert True
    
    def test_initialization(self):
        """Testa inicialização do SecurityManager."""
        from modules.system.security_module import SecurityManager
        security = SecurityManager()
        assert security is not None
    
    def test_permission_check(self):
        """Testa verificação de permissões."""
        from modules.system.security_module import SecurityManager, PermissionLevel
        security = SecurityManager()
        security.set_permission_level(PermissionLevel.USER)
        
        # Comandos permitidos para USER
        assert security.check_permission("search") == True
        assert security.check_permission("open_app") == True
        
        # Comandos não permitidos para USER
        assert security.check_permission("delete_file") == False
        assert security.check_permission("shutdown") == False
    
    def test_safe_command_detection(self):
        """Testa detecção de comandos perigosos."""
        from modules.system.security_module import SecurityManager
        security = SecurityManager()
        
        # Comando perigoso
        is_safe, reason = security.is_safe_command("rm -rf /")
        assert is_safe == False
        assert reason is not None
        
        # Comando seguro
        is_safe, reason = security.is_safe_command("echo hello")
        assert is_safe == True
    
    def test_audit_log(self):
        """Testa log de auditoria."""
        from modules.system.security_module import SecurityManager
        security = SecurityManager()
        
        # Fazer algumas ações
        security.check_permission("search")
        security.is_safe_command("test command")
        
        # Verificar log
        logs = security.get_audit_log(limit=10)
        assert isinstance(logs, list)


class TestTaskDecomposition:
    """Testes para TaskDecomposer e TaskExecutor."""
    
    def test_import(self):
        """Testa se módulos podem ser importados."""
        from modules.processing.task_decomposition import TaskDecomposer, TaskExecutor, Task
        assert True
    
    def test_task_creation(self):
        """Testa criação de Task."""
        from modules.processing.task_decomposition import Task, TaskStatus
        
        task = Task(
            task_id="test_1",
            description="Tarefa de teste",
            action="test_action",
            parameters={"param1": "value1"}
        )
        
        assert task.task_id == "test_1"
        assert task.status == TaskStatus.PENDING
        assert task.parameters["param1"] == "value1"
    
    def test_task_decomposition(self):
        """Testa decomposição de tarefas."""
        from modules.processing.task_decomposition import TaskDecomposer
        
        decomposer = TaskDecomposer()
        plan = decomposer.decompose("Enviar email para João")
        
        assert plan is not None
        assert len(plan.tasks) > 0
        assert plan.plan_id is not None
    
    def test_task_executor(self):
        """Testa executor de tarefas."""
        from modules.processing.task_decomposition import TaskExecutor, Task, TaskStatus
        
        executor = TaskExecutor()
        
        # Criar tarefa simples
        task = Task("test_1", "Teste", "test_action")
        
        # Registrar handler
        def test_handler(params):
            return {"success": True, "result": "OK"}
        
        executor.register_handler("test_action", test_handler)
        
        # Executar
        success = executor.execute_task(task)
        
        assert success == True
        assert task.status == TaskStatus.COMPLETED


class TestVoiceModules:
    """Testes para módulos de voz."""
    
    def test_whisper_import(self):
        """Testa importação do WhisperModule."""
        try:
            from modules.input.whisper_module import WhisperModule
            assert True
        except ImportError as e:
            pytest.skip(f"Whisper não instalado: {e}")
    
    def test_advanced_tts_import(self):
        """Testa importação do AdvancedTTSModule."""
        try:
            from modules.input.advanced_tts import AdvancedTTSModule
            assert True
        except ImportError as e:
            pytest.skip(f"TTS não instalado: {e}")
    
    def test_wake_word_import(self):
        """Testa importação do WakeWordDetector."""
        from modules.input.wake_word_detector import SimpleWakeWordDetector
        assert True


class TestIntegrations:
    """Testes para módulos de integração."""
    
    def test_calendar_import(self):
        """Testa importação do CalendarIntegration."""
        from modules.action.calendar_integration import CalendarIntegration
        assert True
    
    def test_calendar_initialization(self):
        """Testa inicialização do CalendarIntegration."""
        from modules.action.calendar_integration import CalendarIntegration
        
        # Inicializar sem credenciais (não vai funcionar mas não deve dar erro)
        calendar = CalendarIntegration(provider="google")
        assert calendar is not None
        assert calendar.provider == "google"
    
    def test_email_import(self):
        """Testa importação do EmailIntegration."""
        from modules.action.email_integration import EmailIntegration
        assert True
    
    def test_email_initialization(self):
        """Testa inicialização do EmailIntegration."""
        from modules.action.email_integration import EmailIntegration
        
        # Inicializar sem credenciais
        email = EmailIntegration(provider="gmail")
        assert email is not None
        assert email.provider == "gmail"


class TestJarvisIntegration:
    """Testes para JarvisCore e integração completa."""
    
    def test_import(self):
        """Testa importação do JarvisCore."""
        from jarvis_integration import JarvisCore, quick_start
        assert True
    
    def test_quick_start_basic(self):
        """Testa inicialização rápida em modo básico."""
        from jarvis_integration import quick_start
        
        jarvis = quick_start(mode="basic", wake_word=False)
        assert jarvis is not None
        
        # Verificar status
        status = jarvis.get_status()
        assert isinstance(status, dict)
        assert "voice_available" in status
        assert "security_enabled" in status
    
    def test_process_command(self):
        """Testa processamento de comando."""
        from jarvis_integration import quick_start
        
        jarvis = quick_start(mode="basic")
        response = jarvis.process_command("teste de comando")
        
        assert response is not None
        assert isinstance(response, str)
    
    def test_memory_integration(self):
        """Testa integração com memória."""
        from jarvis_integration import quick_start
        
        jarvis = quick_start(mode="basic")
        
        # Processar comando
        jarvis.process_command("Olá JARVIS")
        
        # Verificar memória
        stats = jarvis.memory.get_stats()
        assert stats["conversations"] > 0


class TestPersistentMemory:
    """Testes para PersistentMemory."""
    
    def test_import(self):
        """Testa importação."""
        from modules.memory.persistent_memory import PersistentMemory
        assert True
    
    def test_initialization(self):
        """Testa inicialização."""
        from modules.memory.persistent_memory import PersistentMemory
        import tempfile
        
        # Usar diretório temporário
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = f"{tmpdir}/test_memory.db"
            memory = PersistentMemory(db_path=db_path)
            assert memory is not None
    
    def test_conversation_storage(self):
        """Testa armazenamento de conversas."""
        from modules.memory.persistent_memory import PersistentMemory
        import tempfile
        
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = f"{tmpdir}/test_memory.db"
            memory = PersistentMemory(db_path=db_path)
            
            # Salvar conversa
            memory.save_conversation("user", "Teste de mensagem")
            
            # Recuperar
            history = memory.get_conversation_history(limit=10)
            assert len(history) > 0
            assert history[0]["content"] == "Teste de mensagem"
    
    def test_preferences(self):
        """Testa armazenamento de preferências."""
        from modules.memory.persistent_memory import PersistentMemory
        import tempfile
        
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = f"{tmpdir}/test_memory.db"
            memory = PersistentMemory(db_path=db_path)
            
            # Salvar preferência
            memory.save_user_preference("idioma", "pt-BR")
            
            # Recuperar
            idioma = memory.get_user_preference("idioma")
            assert idioma == "pt-BR"


def run_all_tests():
    """Executa todos os testes."""
    import subprocess
    result = subprocess.run(
        ["pytest", __file__, "-v", "--tb=short"],
        capture_output=True,
        text=True
    )
    print(result.stdout)
    print(result.stderr)
    return result.returncode


if __name__ == "__main__":
    # Executar testes
    exit_code = run_all_tests()
    sys.exit(exit_code)
