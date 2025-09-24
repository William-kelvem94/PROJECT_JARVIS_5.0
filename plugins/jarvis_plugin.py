# Plugin de integração Jarvis (exemplo de estrutura para plugins customizados)

class JarvisPlugin:
    def process(self, text: str) -> str:
        # Aqui pode ser implementada lógica customizada do Jarvis
        return f"[Jarvis Plugin] {text}"
