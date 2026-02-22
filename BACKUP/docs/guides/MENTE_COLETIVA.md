# 🌐 Mente Coletiva JARVIS - Guia de Configuração

## Visão Geral
A **Mente Coletiva** permite que múltiplas instâncias do JARVIS compartilhem conhecimento, memórias e aprendizado entre dispositivos, criando uma inteligência distribuída e colaborativa.

## Funcionalidades
- **Sincronização na Nuvem**: Via Google Drive para backup e compartilhamento entre dispositivos
- **Rede Local**: Descoberta automática e comunicação em tempo real na mesma rede Wi-Fi
- **Consensus Algorithm**: Sistema de votação para decisões importantes
- **Privacidade**: Criptografia de pacotes e controle de confiança

## Pré-requisitos
1. **Google Drive**: Instale o aplicativo do Google Drive no PC
2. **Mesma Conta**: Todos os dispositivos devem usar a mesma conta Windows/Microsoft
3. **Rede Wi-Fi**: Para comunicação local entre dispositivos próximos

## Configuração Automática
O JARVIS detecta automaticamente:
- Pasta local do Google Drive
- Dispositivos na rede com a mesma conta
- Capacidades de hardware (GPU, etc.)

## Configuração Manual (Interface Integrada)
1. Execute o JARVIS normalmente
2. Abra o **Stark Dashboard** (HUD → botão direito → Dashboard)
3. Vá na aba **"⚙️ Configurações"**
4. Na seção **"Mente Coletiva (Network Mesh)"**:
   - **Status**: Habilite para ativar
   - **Google Drive Sync**: Para sincronização na nuvem
   - **Rede Local**: Para descoberta automática
   - **Criptografia**: Para segurança dos dados
5. Clique em **"💾 Salvar Configurações"**

## Configuração Avançada (API Google Drive)
Para recursos avançados de sincronização:

1. Acesse [Google Cloud Console](https://console.cloud.google.com/)
2. Crie um novo projeto ou selecione existente
3. Habilite a **Google Drive API**
4. Crie **Credenciais OAuth 2.0** (Desktop Application)
5. Baixe o `client_secret.json`
6. Coloque em: `data/network_mesh/google_credentials/client_secret.json`
7. Na interface, configure o caminho das credenciais

## Como Funciona
1. **Descoberta**: JARVIS identifica outros dispositivos automaticamente
2. **Sincronização**: Memórias e aprendizados são compartilhados periodicamente
3. **Consensus**: Decisões complexas usam votação entre instâncias
4. **Recovery**: Se um dispositivo falhar, outros assumem funções críticas

## Monitoramento
- Logs em: `data/logs/jarvis_singularity.log`
- Status no HUD: "COLLECTIVE MIND: ACTIVE"
- Dashboard mostra dispositivos conectados

## Segurança
- **Criptografia**: Todos os pacotes são criptografados (TLS 1.3)
- **Confiança**: Apenas dispositivos da mesma conta são aceitos
- **Isolamento**: Dados sensíveis permanecem locais

## Troubleshooting
- **Não encontra Google Drive**: Verifique se o app está instalado e logado
- **Rede não conecta**: Verifique firewall e se dispositivos estão na mesma rede
- **Sync falha**: Verifique credenciais da API do Google Drive

---
*Sistema desenvolvido para criar uma inteligência verdadeiramente coletiva e distribuída.*