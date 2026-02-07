# 🔧 Instalação do Face Recognition (Opcional)

O módulo `face_recognition` é **opcional** no JARVIS 5.0. Ele permite reconhecimento facial avançado (FaceID), mas requer compilação de bibliotecas C++ que podem ser complexas no Windows.

## ⚠️ Por que é Opcional?

O `face_recognition` depende do `dlib`, que precisa:
- **CMake** (ferramenta de compilação)
- **Visual Studio Build Tools** (compilador C++)
- **Tempo de compilação** (5-10 minutos)

**O JARVIS funciona perfeitamente sem ele!** Usa detecção de presença básica via OpenCV.

---

## 🚀 Opção 1: Instalar CMake e Compilar (Recomendado)

### **Passo 1: Instalar CMake**

#### **Windows (Automático via Chocolatey)**
```powershell
# Instalar Chocolatey (se não tiver)
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Instalar CMake
choco install cmake -y

# Reiniciar terminal e verificar
cmake --version
```

#### **Windows (Manual)**
1. Baixa de: https://cmake.org/download/
2. Executa o instalador
3. **IMPORTANTE**: Marca "Add CMake to system PATH"
4. Reinicia o terminal

### **Passo 2: Instalar Visual Studio Build Tools**

```powershell
# Via Chocolatey
choco install visualstudio2022buildtools -y

# Ou baixa manual de:
# https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2022
```

### **Passo 3: Instalar face_recognition**

```bash
pip install face_recognition
```

**Tempo estimado**: 5-10 minutos (compilação do dlib)

---

## 🎯 Opção 2: Usar Binários Pré-Compilados (Mais Rápido)

### **Windows com Python 3.11**

```bash
# 1. Instalar dlib pré-compilado
pip install https://github.com/z-mahmud22/Dlib_Windows_Python3.x/raw/main/dlib-19.24.1-cp311-cp311-win_amd64.whl

# 2. Instalar face_recognition
pip install face_recognition
```

**Tempo estimado**: 1-2 minutos

### **Outras versões do Python**

Encontra o wheel correto em:
- https://github.com/z-mahmud22/Dlib_Windows_Python3.x

---

## ✅ Verificar Instalação

```python
import face_recognition
print("✅ Face Recognition instalado com sucesso!")
```

---

## 🔄 Reativar no JARVIS

Depois de instalar, descomenta a linha no `requirements.txt`:

```diff
mediapipe
-# face_recognition  # OPCIONAL: Requer CMake + dlib (ver docs/install_face_recognition.md)
+face_recognition
watchdog
```

E no `src/core/maintenance_manager.py`:

```diff
critical_modules = {
    "cv2": "opencv-contrib-python",
    "pyautogui": "pyautogui",
    "mediapipe": "mediapipe",
-   # "face_recognition": "face_recognition",  # OPCIONAL: Requer CMake + dlib
+   "face_recognition": "face_recognition",
    "ultralytics": "ultralytics",
```

Reinicia o JARVIS e ele detectará automaticamente!

---

## 🆘 Problemas Comuns

### **Erro: "CMake is not installed"**
- Instala CMake (ver Passo 1)
- Reinicia o terminal
- Verifica com `cmake --version`

### **Erro: "error: Microsoft Visual C++ 14.0 is required"**
- Instala Visual Studio Build Tools (ver Passo 2)

### **Erro: "Failed building wheel for dlib"**
- Usa binários pré-compilados (Opção 2)

---

## 💡 Alternativa: Usar Apenas OpenCV

O JARVIS já tem detecção de presença via **Haar Cascade** (OpenCV):
- ✅ Funciona sem compilação
- ✅ Detecta rostos em tempo real
- ❌ Não reconhece identidades específicas

**Para a maioria dos casos, isto é suficiente!** 🎉
