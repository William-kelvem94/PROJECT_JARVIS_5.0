"""
Event Bus - Sistema de Mensageria para Comunicação entre Microserviços
Implementa padrão publish-subscribe para eventos assíncronos
"""

import asyncio
import json
from typing import Dict, List, Callable, Any, Optional
from enum import Enum
from dataclasses import dataclass, asdict
from datetime import datetime
from core.logger import logger

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("Redis não disponível. Usando Event Bus em memória.")

class EventType(Enum):
    """Tipos de eventos no sistema."""
    COMMAND = "command"
    EVENT = "event"
    QUERY = "query"
    RESPONSE = "response"
    ERROR = "error"
    HEALTH_CHECK = "health_check"

@dataclass
class Event:
    """Estrutura de evento."""
    id: str
    type: EventType
    source: str
    destination: Optional[str]
    payload: Dict[str, Any]
    timestamp: datetime
    correlation_id: Optional[str] = None
    reply_to: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte evento para dicionário."""
        data = asdict(self)
        data["type"] = self.type.value
        data["timestamp"] = self.timestamp.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Event":
        """Cria evento a partir de dicionário."""
        data["type"] = EventType(data["type"])
        data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        return cls(**data)

class EventBus:
    """
    Event Bus para comunicação assíncrona entre serviços.
    Suporta Redis para distribuição ou memória para desenvolvimento.
    """
    
    def __init__(self, use_redis: bool = False, redis_url: str = "redis://localhost:6379"):
        """
        Inicializa Event Bus.
        
        Args:
            use_redis: Se True, usa Redis (requer redis instalado)
            redis_url: URL do Redis
        """
        self.use_redis = use_redis and REDIS_AVAILABLE
        self.redis_client = None
        self.subscribers: Dict[str, List[Callable]] = {}
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.running = False
        
        if self.use_redis:
            try:
                self.redis_client = redis.from_url(redis_url, decode_responses=True)
                logger.info(f"Event Bus conectado ao Redis: {redis_url}")
            except Exception as e:
                logger.warning(f"Erro ao conectar Redis, usando memória: {e}")
                self.use_redis = False
        
        logger.info(f"Event Bus inicializado (Redis: {self.use_redis})")
    
    async def start(self):
        """Inicia o Event Bus."""
        if self.running:
            return
        
        self.running = True
        
        if self.use_redis:
            # Iniciar worker para processar mensagens do Redis
            asyncio.create_task(self._redis_subscriber())
        else:
            # Iniciar worker para processar fila em memória
            asyncio.create_task(self._message_processor())
        
        logger.info("Event Bus iniciado")
    
    async def stop(self):
        """Para o Event Bus."""
        self.running = False
        logger.info("Event Bus parado")
    
    async def publish(self, event: Event, channel: Optional[str] = None) -> bool:
        """
        Publica um evento.
        
        Args:
            event: Evento a publicar
            channel: Canal específico (opcional)
        
        Returns:
            True se publicou com sucesso
        """
        try:
            channel = channel or "events"
            
            if self.use_redis and self.redis_client:
                # Publicar no Redis
                await asyncio.to_thread(
                    self.redis_client.publish,
                    channel,
                    json.dumps(event.to_dict())
                )
            else:
                # Adicionar à fila local
                await self.message_queue.put((channel, event))
            
            logger.debug(f"Evento publicado: {event.id} em {channel}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao publicar evento: {e}")
            return False
    
    def subscribe(self, channel: str, handler: Callable):
        """
        Inscreve handler em um canal.
        
        Args:
            channel: Canal para inscrever
            handler: Função async que recebe Event
        """
        if channel not in self.subscribers:
            self.subscribers[channel] = []
        
        self.subscribers[channel].append(handler)
        logger.info(f"Handler inscrito em {channel}: {handler.__name__}")
    
    async def request(
        self,
        event: Event,
        channel: str,
        timeout: float = 30.0
    ) -> Optional[Event]:
        """
        Envia requisição e aguarda resposta (request-reply pattern).
        
        Args:
            event: Evento de requisição
            channel: Canal para enviar
            timeout: Timeout em segundos
        
        Returns:
            Evento de resposta ou None
        """
        # Criar canal de resposta único
        reply_channel = f"reply_{event.id}"
        response_received = asyncio.Event()
        response_event = None
        
        async def response_handler(reply_event: Event):
            nonlocal response_event
            if reply_event.correlation_id == event.id:
                response_event = reply_event
                response_received.set()
        
        # Inscrever no canal de resposta
        self.subscribe(reply_channel, response_handler)
        
        # Definir reply_to no evento
        event.reply_to = reply_channel
        
        # Publicar evento
        await self.publish(event, channel)
        
        # Aguardar resposta
        try:
            await asyncio.wait_for(response_received.wait(), timeout=timeout)
            return response_event
        except asyncio.TimeoutError:
            logger.warning(f"Timeout aguardando resposta para {event.id}")
            return None
        finally:
            # Remover handler
            if reply_channel in self.subscribers:
                self.subscribers[reply_channel].remove(response_handler)
    
    async def _redis_subscriber(self):
        """Worker para processar eventos do Redis."""
        pubsub = self.redis_client.pubsub()
        
        # Inscrever em todos os canais conhecidos
        for channel in self.subscribers.keys():
            pubsub.subscribe(channel)
        
        while self.running:
            try:
                message = await asyncio.to_thread(pubsub.get_message, timeout=1.0)
                
                if message and message["type"] == "message":
                    channel = message["channel"]
                    event_data = json.loads(message["data"])
                    event = Event.from_dict(event_data)
                    
                    await self._dispatch_event(channel, event)
                    
            except Exception as e:
                logger.error(f"Erro no Redis subscriber: {e}")
                await asyncio.sleep(1)
    
    async def _message_processor(self):
        """Worker para processar mensagens da fila local."""
        while self.running:
            try:
                # Aguardar mensagem com timeout
                try:
                    channel, event = await asyncio.wait_for(
                        self.message_queue.get(),
                        timeout=1.0
                    )
                except asyncio.TimeoutError:
                    continue
                
                await self._dispatch_event(channel, event)
                
            except Exception as e:
                logger.error(f"Erro no processador de mensagens: {e}")
    
    async def _dispatch_event(self, channel: str, event: Event):
        """Despacha evento para handlers inscritos."""
        handlers = self.subscribers.get(channel, [])
        
        # Executar todos os handlers
        tasks = []
        for handler in handlers:
            if asyncio.iscoroutinefunction(handler):
                tasks.append(handler(event))
            else:
                # Handler síncrono, executar em thread
                tasks.append(asyncio.to_thread(handler, event))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

