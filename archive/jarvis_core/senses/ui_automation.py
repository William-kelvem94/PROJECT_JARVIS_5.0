"""
Senses - UI Automation Module
Controle nativo do Windows sem coordenadas
"""

import logging
from typing import Optional, List, Dict
import time

logger = logging.getLogger(__name__)

class NeuralTouch:
    """Controle de UI via Windows Automation"""
    
    def __init__(self):
        self.auto = None
        
        try:
            import uiautomation as auto
            self.auto = auto
            logger.info("✅ UI Automation inicializado")
        except ImportError:
            logger.warning("⚠️ uiautomation não instalado. Controle de UI desabilitado.")
    
    def find_window(self, name: str, partial_match: bool = True) -> Optional[object]:
        """Encontra janela por nome"""
        if not self.auto:
            return None
        
        try:
            if partial_match:
                window = self.auto.WindowControl(searchDepth=1, SubName=name)
            else:
                window = self.auto.WindowControl(searchDepth=1, Name=name)
            
            if window.Exists(maxSearchSeconds=2):
                return window
            
            return None
        except Exception as e:
            logger.error(f"❌ Erro ao buscar janela '{name}': {e}")
            return None
    
    def find_element(self, window, element_type: str, name: str) -> Optional[object]:
        """Encontra elemento dentro de uma janela"""
        if not self.auto or not window:
            return None
        
        try:
            # Mapear tipos
            type_map = {
                "button": window.ButtonControl,
                "edit": window.EditControl,
                "text": window.TextControl,
                "list": window.ListControl,
                "menu": window.MenuItemControl,
                "tab": window.TabItemControl
            }
            
            control_func = type_map.get(element_type.lower())
            
            if not control_func:
                logger.error(f"❌ Tipo desconhecido: {element_type}")
                return None
            
            element = control_func(Name=name)
            
            if element.Exists(maxSearchSeconds=2):
                return element
            
            return None
        except Exception as e:
            logger.error(f"❌ Erro ao buscar elemento '{name}': {e}")
            return None
    
    def click_element(self, app_name: str, element_name: str, element_type: str = "button") -> bool:
        """Clica em elemento por nome"""
        logger.info(f"🖱️ Clicando em '{element_name}' do '{app_name}'...")
        
        # Encontrar janela
        window = self.find_window(app_name)
        
        if not window:
            logger.error(f"❌ Janela '{app_name}' não encontrada")
            return False
        
        # Encontrar elemento
        element = self.find_element(window, element_type, element_name)
        
        if not element:
            logger.error(f"❌ Elemento '{element_name}' não encontrado")
            return False
        
        try:
            # Clicar
            element.Click()
            logger.info(f"✅ Clique executado: {element_name}")
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao clicar: {e}")
            return False
    
    def type_text(self, app_name: str, field_name: str, text: str) -> bool:
        """Digita texto em campo"""
        logger.info(f"⌨️ Digitando em '{field_name}' do '{app_name}'...")
        
        # Encontrar janela
        window = self.find_window(app_name)
        
        if not window:
            logger.error(f"❌ Janela '{app_name}' não encontrada")
            return False
        
        # Encontrar campo
        field = self.find_element(window, "edit", field_name)
        
        if not field:
            logger.error(f"❌ Campo '{field_name}' não encontrado")
            return False
        
        try:
            # Digitar
            field.SetValue(text)
            logger.info(f"✅ Texto digitado: {text[:50]}...")
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao digitar: {e}")
            return False
    
    def get_element_tree(self, app_name: str, max_depth: int = 3) -> Dict:
        """Retorna árvore de elementos da janela"""
        window = self.find_window(app_name)
        
        if not window:
            return {}
        
        try:
            tree = self._build_tree(window, max_depth=max_depth)
            return tree
        except Exception as e:
            logger.error(f"❌ Erro ao construir árvore: {e}")
            return {}
    
    def _build_tree(self, element, current_depth: int = 0, max_depth: int = 3) -> Dict:
        """Constrói árvore recursivamente"""
        if current_depth >= max_depth:
            return {}
        
        tree = {
            "name": element.Name,
            "type": element.ControlTypeName,
            "children": []
        }
        
        try:
            for child in element.GetChildren():
                child_tree = self._build_tree(child, current_depth + 1, max_depth)
                if child_tree:
                    tree["children"].append(child_tree)
        except:
            pass
        
        return tree
    
    def wait_for_element(self, app_name: str, element_name: str, 
                        element_type: str = "button", timeout: int = 10) -> bool:
        """Espera elemento aparecer"""
        logger.info(f"⏳ Aguardando '{element_name}' aparecer...")
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            window = self.find_window(app_name)
            
            if window:
                element = self.find_element(window, element_type, element_name)
                
                if element:
                    logger.info(f"✅ Elemento apareceu!")
                    return True
            
            time.sleep(0.5)
        
        logger.warning(f"⏰ Timeout aguardando '{element_name}'")
        return False


# Instância global
neural_touch = NeuralTouch()


# Teste
if __name__ == "__main__":
    touch = NeuralTouch()
    
    # Exemplo: Clicar no botão Minimizar do Notepad
    # touch.click_element("Notepad", "Minimize", "button")
    
    # Exemplo: Digitar no Notepad
    # touch.type_text("Notepad", "Text Editor", "Hello from JARVIS!")
    
    print("✅ UI Automation pronto!")
