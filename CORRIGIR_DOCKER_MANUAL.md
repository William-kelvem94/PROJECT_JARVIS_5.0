# Como Corrigir Docker + WSL no Windows

Seu Docker está com erro de API incompatível com WSL. Siga estes passos:

## Opção 1: Resetar Docker Desktop (Recomendado)

1. **Fechar Docker Desktop completamente**
   - Clique com botão direito no ícone do Docker na bandeja
   - Selecione "Quit Docker Desktop"

2. **Limpar configurações**
   ```powershell
   # Execute no PowerShell como Administrador
   Remove-Item -Recurse -Force $env:APPDATA\Docker
   Remove-Item -Recurse -Force $env:LOCALAPPDATA\Docker
   ```

3. **Reinstalar WSL2 (se necessário)**
   ```powershell
   # Como Administrador
   wsl --install
   wsl --set-default-version 2
   wsl --update
   ```

4. **Iniciar Docker Desktop**
   - Abra Docker Desktop normalmente
   - Vá em: Settings > General
   - Marque: ✅ "Use the WSL 2 based engine"
   - Apply & Restart

5. **Configurar WSL Integration**
   - Settings > Resources > WSL Integration
   - Marque: ✅ "Enable integration with my default WSL distro"
   - Apply & Restart

## Opção 2: Usar Backend Hyper-V

Se WSL não funcionar:

1. Docker Desktop > Settings > General
2. Desmarque: ❌ "Use the WSL 2 based engine"
3. Apply & Restart
4. Docker usará Hyper-V (mais lento, mas funciona)

## Opção 3: Reinstalar Docker Desktop

1. Desinstalar Docker Desktop completamente
2. Baixar nova versão: https://www.docker.com/products/docker-desktop
3. Instalar com configurações padrão
4. Na instalação, escolher "WSL 2" quando perguntado

## Opção 4: Usar Modo Local (Sem Docker)

Se Docker continuar com problemas, use:

```powershell
.\START_LOCAL_COMPLETO.ps1
```

Este script:
- Instala Ollama no Windows
- Roda Backend + Frontend localmente
- **TOTALMENTE FUNCIONAL** (não é demo!)

## Testar se Docker está OK

Após corrigir, teste:

```powershell
docker --version
docker ps
docker run hello-world
```

Se funcionar sem erros, execute:

```powershell
.\INSTALL_AND_RUN.ps1
```

## Contato

- Erro persiste? Use modo local com `START_LOCAL_COMPLETO.ps1`
- É funcional e completo, apenas não usa Docker

