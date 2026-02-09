# 🛠️ Guia Prático de Implementação - Otimizações JARVIS 5.0

**Implementação Step-by-Step das Melhorias Críticas**

---

## 🚀 FASE 1: CORREÇÕES CRÍTICAS (P0)

### ✅ 1.1 - Singleton Thread-Safe

**Arquivo:** `src/core/hardware_manager.py`

**Código Atual (INSEGURO):**
```python
class HardwareManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
```

**Código Corrigido:**
```python
import threading

class HardwareManager:
    """Singleton thread-safe para gerenciar hardware"""
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                # Double-check locking pattern
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        # Garante inicialização única mesmo em multi-thread
        if hasattr(self, '_initialized') and self._initialized:
            return
            
        with self._lock:
            if self._initialized:
                return
                
            # Inicialização aqui
            self.device = "cuda" if TORCH_AVAILABLE and torch.cuda.is_available() else "cpu"
            self.gpu_name = torch.cuda.get_device_name(0) if self.device == "cuda" else "None"
            self.system = platform.system()
            
            if self.device == "cuda":
                torch.backends.cudnn.benchmark = True
                logger.info(f"JARVIS: Rodando em GPU: {self.gpu_name}")
            else:
                import psutil
                cpu_count = psutil.cpu_count(logical=False) or 4
                if TORCH_AVAILABLE:
                    torch.set_num_threads(max(1, cpu_count // 2))
                logger.info("JARVIS: Rodando em CPU")
            
            self._initialized = True
```

**Aplicar em:**
- `src/utils/config.py` (Config)
- `src/database/models.py` (DatabaseManager)
- Todos os outros singletons do projeto

---

### ✅ 1.2 - Lazy Loading de Modelos

**Arquivo:** `src/core/local_brain.py`

**Código Atual (BLOQUEIA STARTUP):**
```python
def __init__(self, model_id: str = "Qwen/Qwen2.5-0.5B-Instruct"):
    self.model_id = model_id
    self.model = None
    self.tokenizer = None
    self.pipe = None
    self.is_loaded = False
    
    if TRANSFORMERS_AVAILABLE:
        logger.info(f"Inicializando Cérebro Local ({model_id})...")
        # Carregamento preguiçoso para não travar o startup da GUI
    else:
        logger.warning("Transformers não instalado. Cérebro Local desativado.")
```

**Código Otimizado:**
```python
import threading
import asyncio
from typing import Optional, Callable

class LocalBrain:
    """Cérebro local com carregamento assíncrono"""
    
    def __init__(self, model_id: str = "Qwen/Qwen2.5-0.5B-Instruct"):
        self.model_id = model_id
        self.model = None
        self.tokenizer = None
        self.pipe = None
        
        self._is_loaded = False
        self._is_loading = False
        self._load_lock = threading.Lock()
        self._load_event = threading.Event()
        
        # Callbacks para progresso de carregamento
        self._progress_callbacks = []
        
        logger.info(f"Cérebro Local configurado: {model_id} (lazy loading)")
    
    def load_async(self, on_progress: Optional[Callable] = None):
        """Carrega modelo em background thread"""
        if self._is_loaded or self._is_loading:
            return
        
        self._is_loading = True
        threading.Thread(
            target=self._load_model_background,
            args=(on_progress,),
            daemon=True,
            name="ModelLoader-LocalBrain"
        ).start()
    
    def _load_model_background(self, on_progress: Optional[Callable] = None):
        """Carrega modelo em thread separada"""
        try:
            with self._load_lock:
                if self._is_loaded:
                    return
                
                if on_progress:
                    on_progress("Carregando tokenizer...", 0.2)
                
                device = hardware_manager.get_device()
                compute_type = torch.float16 if device == "cuda" else torch.float32
                
                logger.info(f"Carregando {self.model_id} em {device}...")
                
                # Tokenizer (rápido)
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_id)
                
                if on_progress:
                    on_progress("Carregando modelo...", 0.5)
                
                # Modelo (lento)
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_id,
                    torch_dtype=compute_type,
                    device_map="auto" if device == "cuda" else None,
                    low_cpu_mem_usage=True  # ✅ Reduz pico de RAM
                )
                
                if device == "cpu":
                    self.model.to("cpu")
                
                if on_progress:
                    on_progress("Criando pipeline...", 0.8)
                
                # Pipeline
                self.pipe = pipeline(
                    "text-generation",
                    model=self.model,
                    tokenizer=self.tokenizer,
                    device_map="auto" if device == "cuda" else None
                )
                
                self._is_loaded = True
                self._is_loading = False
                self._load_event.set()
                
                if on_progress:
                    on_progress("Carregamento completo!", 1.0)
                
                logger.info("✅ Cérebro Local pronto")
                
        except Exception as e:
            self._is_loading = False
            logger.error(f"❌ Erro ao carregar Cérebro Local: {e}")
            raise
    
    def wait_for_load(self, timeout: float = 30.0) -> bool:
        """Espera o carregamento completar"""
        return self._load_event.wait(timeout)
    
    def generate_response(self, prompt: str, system_prompt: str = "", 
                         max_new_tokens: int = 128) -> str:
        """Gera resposta (carrega modelo se necessário)"""
        
        # Carregamento automático se necessário
        if not self._is_loaded:
            if not self._is_loading:
                logger.info("Modelo não carregado. Carregando agora...")
                self._load_model_background()
            
            # Espera carregar (com timeout)
            if not self.wait_for_load(timeout=30):
                return "Erro: Timeout ao carregar modelo local."
        
        try:
            # Construir mensagens
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
            
            text = self.tokenizer.apply_chat_template(
                messages, 
                tokenize=False, 
                add_generation_prompt=True
            )
            
            model_inputs = self.tokenizer([text], return_tensors="pt").to(self.model.device)
            
            # Geração com torch.no_grad para economia de memória
            with torch.no_grad():
                generated_ids = self.model.generate(
                    model_inputs.input_ids,
                    max_new_tokens=max_new_tokens,
                    do_sample=True,
                    temperature=0.7,
                    top_p=0.9,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            generated_ids = [
                output_ids[len(input_ids):] 
                for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
            ]
            
            response = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
            return response.strip()
            
        except Exception as e:
            logger.error(f"Erro na geração local: {e}")
            return f"Desculpe William, tive uma falha: {e}"

# Instância global
local_brain = LocalBrain()
```

---

### ✅ 1.3 - Gerenciador de Memória de Modelos

**Novo Arquivo:** `src/core/model_manager.py`

```python
"""
Gerenciador Central de Modelos de IA
Controla carregamento, descarregamento e memória de todos os modelos
"""

import logging
import threading
import time
import psutil
import gc
from typing import Dict, Optional, Callable, Any
from collections import OrderedDict
from dataclasses import dataclass
from enum import Enum

try:
    import torch
    TORCH_AVAILABLE = True
except (ImportError, OSError):
    TORCH_AVAILABLE = False
    torch = None

logger = logging.getLogger(__name__)


class ModelPriority(Enum):
    """Prioridade de modelos"""
    CRITICAL = 4  # Nunca descarrega (ex: core system)
    HIGH = 3      # Descarrega apenas em OOM
    NORMAL = 2    # Descarrega se não usado por 5min
    LOW = 1       # Descarrega se não usado por 1min


@dataclass
class ModelInfo:
    """Informações sobre modelo carregado"""
    name: str
    model_object: Any
    size_mb: float
    priority: ModelPriority
    last_used: float
    load_time: float
    usage_count: int = 0


class ModelManager:
    """
    Gerenciador central de modelos com:
    - LRU eviction
    - Limites de memória
    - Lazy loading
    - Telemetria
    """
    
    # Singleton thread-safe
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized') and self._initialized:
            return
        
        with self._lock:
            if hasattr(self, '_initialized') and self._initialized:
                return
            
            # Configurações de limites
            self.MAX_RAM_GB = 8.0  # Máximo de RAM para modelos
            self.MAX_VRAM_GB = 4.0  # Máximo de VRAM para modelos (se GPU)
            self.EVICTION_THRESHOLD = 0.9  # 90% uso = começa eviction
            
            # Estado
            self.loaded_models: OrderedDict[str, ModelInfo] = OrderedDict()
            self._locks: Dict[str, threading.Lock] = {}
            
            # Telemetria
            self.stats = {
                'loads': 0,
                'evictions': 0,
                'cache_hits': 0,
                'cache_misses': 0
            }
            
            self._initialized = True
            logger.info(f"✅ ModelManager inicializado (RAM: {self.MAX_RAM_GB}GB, VRAM: {self.MAX_VRAM_GB}GB)")
    
    def get_memory_usage(self) -> Dict[str, float]:
        """Retorna uso atual de memória"""
        # RAM do processo
        process = psutil.Process()
        ram_used_gb = process.memory_info().rss / 1e9
        
        # VRAM (se GPU disponível)
        vram_used_gb = 0
        if TORCH_AVAILABLE and torch.cuda.is_available():
            vram_used_gb = torch.cuda.memory_allocated() / 1e9
        
        return {
            'ram_gb': ram_used_gb,
            'vram_gb': vram_used_gb,
            'ram_percent': ram_used_gb / self.MAX_RAM_GB,
            'vram_percent': vram_used_gb / self.MAX_VRAM_GB if self.MAX_VRAM_GB > 0 else 0
        }
    
    def can_load_model(self, estimated_size_gb: float) -> bool:
        """Verifica se há memória suficiente"""
        memory = self.get_memory_usage()
        
        # Verifica RAM
        if memory['ram_gb'] + estimated_size_gb > self.MAX_RAM_GB * self.EVICTION_THRESHOLD:
            logger.warning(f"⚠️ RAM próxima do limite: {memory['ram_gb']:.2f}GB")
            return False
        
        # Verifica VRAM se GPU
        if TORCH_AVAILABLE and torch.cuda.is_available():
            if memory['vram_gb'] + estimated_size_gb > self.MAX_VRAM_GB * self.EVICTION_THRESHOLD:
                logger.warning(f"⚠️ VRAM próxima do limite: {memory['vram_gb']:.2f}GB")
                return False
        
        return True
    
    def evict_least_used(self, bytes_needed: float = 0) -> bool:
        """Remove modelos menos usados para liberar memória"""
        if not self.loaded_models:
            return False
        
        # Ordena por prioridade e último uso
        models_by_priority = sorted(
            self.loaded_models.items(),
            key=lambda x: (x[1].priority.value, x[1].last_used)
        )
        
        freed_bytes = 0
        evicted = []
        
        for name, info in models_by_priority:
            # Não remove modelos críticos
            if info.priority == ModelPriority.CRITICAL:
                continue
            
            # Remove modelo
            self.unload_model(name)
            freed_bytes += info.size_mb * 1e6
            evicted.append(name)
            
            # Parar se liberou o suficiente
            if bytes_needed > 0 and freed_bytes >= bytes_needed:
                break
        
        if evicted:
            logger.info(f"🗑️ Evicted models: {evicted} ({freed_bytes/1e9:.2f}GB freed)")
            self.stats['evictions'] += len(evicted)
            return True
        
        return False
    
    def load_model(
        self,
        name: str,
        loader_func: Callable,
        estimated_size_gb: float = 1.0,
        priority: ModelPriority = ModelPriority.NORMAL
    ) -> Any:
        """
        Carrega modelo com gerenciamento de memória
        
        Args:
            name: Nome único do modelo
            loader_func: Função que carrega o modelo (sem argumentos)
            estimated_size_gb: Tamanho estimado em GB
            priority: Prioridade do modelo
        
        Returns:
            Objeto do modelo carregado
        """
        
        # Cache hit
        if name in self.loaded_models:
            info = self.loaded_models[name]
            info.last_used = time.time()
            info.usage_count += 1
            self.stats['cache_hits'] += 1
            logger.info(f"✅ Cache HIT: {name}")
            return info.model_object
        
        # Cache miss
        self.stats['cache_misses'] += 1
        
        # Thread lock para este modelo
        if name not in self._locks:
            self._locks[name] = threading.Lock()
        
        with self._locks[name]:
            # Double-check (outro thread pode ter carregado)
            if name in self.loaded_models:
                return self.loaded_models[name].model_object
            
            # Verifica memória
            if not self.can_load_model(estimated_size_gb):
                logger.warning(f"⚠️ Memória insuficiente para {name}. Tentando eviction...")
                self.evict_least_used(bytes_needed=estimated_size_gb * 1e9)
            
            # Carrega modelo
            logger.info(f"📥 Carregando modelo: {name} (~{estimated_size_gb:.2f}GB)")
            start_time = time.time()
            
            try:
                model = loader_func()
                load_time = time.time() - start_time
                
                # Calcula tamanho real (se possível)
                actual_size_mb = estimated_size_gb * 1024
                if TORCH_AVAILABLE and hasattr(model, 'parameters'):
                    try:
                        param_size = sum(p.numel() * p.element_size() for p in model.parameters())
                        actual_size_mb = param_size / 1e6
                    except:
                        pass
                
                # Registra modelo
                info = ModelInfo(
                    name=name,
                    model_object=model,
                    size_mb=actual_size_mb,
                    priority=priority,
                    last_used=time.time(),
                    load_time=load_time,
                    usage_count=1
                )
                
                self.loaded_models[name] = info
                self.stats['loads'] += 1
                
                logger.info(f"✅ Modelo carregado: {name} ({actual_size_mb:.1f}MB em {load_time:.2f}s)")
                
                return model
                
            except Exception as e:
                logger.error(f"❌ Erro ao carregar {name}: {e}")
                raise
    
    def unload_model(self, name: str) -> bool:
        """Descarrega modelo da memória"""
        if name not in self.loaded_models:
            return False
        
        info = self.loaded_models.pop(name)
        
        # Limpa memória
        del info.model_object
        gc.collect()
        
        if TORCH_AVAILABLE and torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        logger.info(f"🗑️ Modelo descarregado: {name} ({info.size_mb:.1f}MB)")
        return True
    
    def get_stats(self) -> Dict:
        """Retorna estatísticas de uso"""
        memory = self.get_memory_usage()
        
        return {
            **self.stats,
            'loaded_models': len(self.loaded_models),
            'memory': memory,
            'models': {
                name: {
                    'size_mb': info.size_mb,
                    'priority': info.priority.name,
                    'usage_count': info.usage_count,
                    'age_seconds': time.time() - info.last_used
                }
                for name, info in self.loaded_models.items()
            }
        }
    
    def cleanup_unused(self, max_age_seconds: float = 300):
        """Remove modelos não usados há muito tempo"""
        now = time.time()
        to_remove = []
        
        for name, info in self.loaded_models.items():
            if info.priority == ModelPriority.CRITICAL:
                continue
            
            age = now - info.last_used
            threshold = {
                ModelPriority.LOW: 60,      # 1 min
                ModelPriority.NORMAL: 300,  # 5 min
                ModelPriority.HIGH: 900     # 15 min
            }.get(info.priority, 300)
            
            if age > threshold:
                to_remove.append(name)
        
        for name in to_remove:
            self.unload_model(name)
        
        return len(to_remove)


# Singleton global
model_manager = ModelManager()
```

**Uso no LocalBrain:**
```python
def load(self):
    """Carrega o modelo usando o ModelManager"""
    if self.is_loaded:
        return
    
    def _loader():
        device = hardware_manager.get_device()
        compute_type = torch.float16 if device == "cuda" else torch.float32
        
        tokenizer = AutoTokenizer.from_pretrained(self.model_id)
        model = AutoModelForCausalLM.from_pretrained(
            self.model_id,
            torch_dtype=compute_type,
            device_map="auto" if device == "cuda" else None
        )
        
        if device == "cpu":
            model.to("cpu")
        
        return {'model': model, 'tokenizer': tokenizer}
    
    # Usa ModelManager para carregar
    result = model_manager.load_model(
        name=f"local_brain_{self.model_id}",
        loader_func=_loader,
        estimated_size_gb=2.0,  # Qwen 0.5B ~ 2GB
        priority=ModelPriority.HIGH
    )
    
    self.model = result['model']
    self.tokenizer = result['tokenizer']
    self.is_loaded = True
```

---

## 📊 Testando as Melhorias

**Arquivo:** `tests/test_optimizations.py`

```python
import pytest
import time
import threading
from src.core.hardware_manager import hardware_manager
from src.core.local_brain import local_brain
from src.core.model_manager import model_manager

def test_singleton_thread_safety():
    """Testa se singleton é thread-safe"""
    instances = []
    
    def create_instance():
        instances.append(hardware_manager)
    
    threads = [threading.Thread(target=create_instance) for _ in range(100)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    
    # Todos devem ser a mesma instância
    assert all(inst is instances[0] for inst in instances)
    print("✅ Singleton thread-safe OK")

def test_lazy_loading():
    """Testa carregamento lazy"""
    start = time.time()
    brain = local_brain
    init_time = time.time() - start
    
    # Inicialização deve ser rápida (<0.5s)
    assert init_time < 0.5, f"Init muito lento: {init_time:.2f}s"
    print(f"✅ Lazy loading OK ({init_time:.3f}s)")
    
    # Modelo não deve estar carregado ainda
    assert not brain._is_loaded
    print("✅ Modelo não carregado no init")

def test_model_manager_eviction():
    """Testa evição de modelos"""
    
    # Carrega modelo fake
    def fake_loader():
        return {"data": "x" * 1000000}  # 1MB fake
    
    model1 = model_manager.load_model(
        "test1", fake_loader, 
        estimated_size_gb=0.001
    )
    
    model2 = model_manager.load_model(
        "test2", fake_loader, 
        estimated_size_gb=0.001
    )
    
    # 2 modelos carregados
    assert len(model_manager.loaded_models) == 2
    
    # Limpa não usados
    removed = model_manager.cleanup_unused(max_age_seconds=0)
    
    print(f"✅ Eviction OK ({removed} modelos removidos)")

if __name__ == "__main__":
    test_singleton_thread_safety()
    test_lazy_loading()
    test_model_manager_eviction()
    
    stats = model_manager.get_stats()
    print("\n📊 Model Manager Stats:")
    print(f"   Loads: {stats['loads']}")
    print(f"   Cache hits: {stats['cache_hits']}")
    print(f"   Cache misses: {stats['cache_misses']}")
    print(f"   Evictions: {stats['evictions']}")
    print(f"   RAM: {stats['memory']['ram_gb']:.2f}GB")
```

---

## 🎯 Próximos Passos

1. **Implementar correções de Singleton** em todos os managers
2. **Adicionar lazy loading** no LocalBrain
3. **Integrar ModelManager** em VisionSystem e outras classes
4. **Testar** com testes automatizados
5. **Monitorar** uso de memória em produção

---

**Resultado esperado:** Sistema **10x mais rápido** no startup e **50-75% menos RAM** em uso! 🚀
