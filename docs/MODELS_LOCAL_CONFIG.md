# 🧠 Guia de Cérebro Local (Modelos Recomendados para LM Studio)

Para que o `PROJECT_JARVIS_5.0` funcione 100% Offline (com o backend enviando chamadas para a porta 1234 do seu LM Studio), você deve escolher o "cérebro" adequado dependendo do equipamento que você está usando (Desktop vs Notebook).

Todos os modelos baixados devem ser preferencialmente no formato **GGUF** (K-Quants como `Q4_K_M` ou `Q5_K_M`), que garantem rapidez com baixíssimo uso de memória RAM.

---

## 🏆 Cérebro Oficial (O Definitivo)
### 🥇 WILL-JARVIS-1.5B-Q4_K_M.gguf
* **Função:** A personalidade mestra e alma construída unicamente para o seu ecossistema.
* **Origem:** Gerado automaticamente na GTX 1050 Ti ao final das 300 Épocas do script de fine-tuning.
* **Onde Rodar:** Roda **voando** tanto no Desktop (GPU) quanto no seu Notebook Galaxy Book 2 360 (CPU), pois consome apenas ~1.5 GB de RAM. Combina lógica perfeita do Qwen2.5 com o Método de Raciocínio (CoT) da sua base local.

---

## 🧪 Cérebros Tradicionais (Teste Imediato)

Se você for testar o Jarvis agora no Notebook antes de o WILL-JARVIS terminar de treinar, baixe estes modelos no próprio buscador do seu LM Studio:

### 1. 🤓 Llama-3.2-3B-Instruct (O "Professor")
* **Autor de Busca no LM Studio:** `lmstudio-community` ou `bartowski`.
* **Uso Ideal:** Para coversar, debater ideias, testar o Frontend de Chat e testar se a arquitetura de Memória e o RAG (`mem0`) estão sendo interpretados perfeitamente com a *Persona humana*. 
* **Tamanho de RAM:** ~2.1 GB.

### 2. 💻 Qwen2.5-Coder-3B-Instruct (O "Robô Operário")
* **Autor de Busca no LM Studio:** `Qwen` ou `bartowski`.
* **Uso Ideal:** Para codificação bruta ou reestruturação dura do seu projeto C#/TS em tempo real. Ele vai acertar toda a parte lógica, mas sua voz vai ser seca, direta, e não "conhecerá" a sua vida local como o Jarvis ensinado conhece.
* **Tamanho de RAM:** ~2.5 GB.

---

## ⚙️ Como Ativar (Passo a Passo)

1. Encontre a "Lupinha" (Search) no seu **LM Studio** e procure o nome do modelo.
2. Baixe o arquivo terminando em `Q4_K_M.gguf` (Exemplo rápido: `llama-3.2-3b-instruct-q4_k_m.gguf`).
3. Vá na aba do lado esquerdo chamada **"<--> Developer / Local Server"**.
4. Faça o Load (carregamento) do cérebro para a memória.
5. Clique verde no topo em **Start Server**.
6. Vá na pasta do projeto e inicie o `start-jarvis.bat`. *Ele fará o Ping na porta 1234 e a conexão se estabelecerá magneticamente.*
