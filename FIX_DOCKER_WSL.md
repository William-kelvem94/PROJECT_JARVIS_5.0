# 🔧 Corrigir Docker + WSL2 no Windows

## 🚨 Problema Detectado

Seu Docker Desktop precisa do WSL2 para funcionar, mas o WSL2 não está instalado ou configurado corretamente.

## ✅ Solução Rápida (Recomendada)

### Passo 1: Instalar WSL2

Abra **PowerShell como Administrador** e execute:

```powershell
# Instalar WSL2
wsl --install

# Se já estiver instalado mas não funcionar:
wsl --update
```

**Reinicie o computador após este comando!**

### Passo 2: Verificar Instalação

Após reiniciar, abra PowerShell normal e execute:

```powershell
wsl --list --verbose
```

Você deve ver algo como:
```
NAME      STATE           VERSION
Ubuntu    Running         2
```

### Passo 3: Configurar Docker Desktop

1. Abra **Docker Desktop**
2. Vá em **Settings** (ícone de engrenagem)
3. Na seção **General**:
   - ✅ Marque "Use the WSL 2 based engine"
4. Na seção **Resources > WSL Integration**:
   - ✅ Enable integration with my default WSL distro
   - ✅ Marque a distribuição Ubuntu
5. Clique em **Apply & Restart**

### Passo 4: Testar Docker

```powershell
docker ps
```

Se funcionar, verá:
```
CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES
```

---

## 🆘 Se Ainda Não Funcionar

### Opção A: Resetar Docker Desktop

1. Feche Docker Desktop
2. Abra PowerShell como **Administrador**:

```powershell
# Parar serviços
Stop-Service -Name com.docker.service -Force
Stop-Service -Name docker -Force

# Resetar WSL
wsl --shutdown

# Reiniciar Docker Desktop
Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"
```

3. Aguarde ~30 segundos
4. Teste: `docker ps`

### Opção B: Reinstalar WSL2

```powershell
# Como Administrador
wsl --unregister Ubuntu
wsl --install
```

**Reinicie o PC**

### Opção C: Instalar Ubuntu Manualmente

```powershell
# Como Administrador
wsl --install -d Ubuntu-22.04
```

Após instalação:
- Defina username/password
- Reinicie Docker Desktop

---

## 🐧 Alternativa: Usar Docker sem WSL2 (Não Recomendado)

Se WSL2 não funcionar, você pode usar Hyper-V:

1. Docker Desktop > Settings
2. General > **Desmarque** "Use WSL 2 based engine"
3. Apply & Restart

**Nota**: Performance será pior

---

## 📞 Comandos Úteis de Diagnóstico

```powershell
# Verificar WSL
wsl --status
wsl --list --verbose

# Verificar Docker
docker --version
docker ps

# Ver logs Docker Desktop
# Menu: Settings > Troubleshoot > View logs

# Resetar tudo
wsl --shutdown
Restart-Service docker
```

---

## ✅ Depois de Corrigir

Após o Docker funcionar, volte e execute:

```powershell
cd D:\Documents\GitHub\PROJECT_JARVIS_3.0
python setup.py
docker-compose up -d --build
```

---

## 🚀 Enquanto isso: Rodar Localmente (Sem Docker)

Se quiser testar enquanto corrige o Docker, veja: `RUN_LOCAL.md`

