"""
Streaming LLM Module - Streaming Real de Respostas
Implementa streaming de tokens para feedback instantâneo
"""

import asyncio
import time
from typing import AsyncIterator, Optional, Dict, Any
from core.local_llm import LocalLLM
from core.logger import logger

class StreamingLLM:
    """
    Wrapper para LLM com suporte a streaming assíncrono.
    Permite enviar tokens conforme são gerados via WebSocket.
    """
    
    def __init__(self, llm: LocalLLM):
        """
        Inicializa streaming LLM.
        
        Args:
            llm: Instância de LocalLLM
        """
        self.llm = llm
        logger.info("StreamingLLM inicializado")
    
    async def generate_stream_async(
        self,
        prompt: str,
        system: Optional[str] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """
        Gera resposta com streaming assíncrono.
        
        Args:
            prompt: Prompt do usuário
            system: Mensagem de sistema (opcional)
            **kwargs: Parâmetros adicionais
        
        Yields:
            Tokens da resposta conforme são gerados
        """
        queue = asyncio.Queue()
        stop_event = asyncio.Event()
        
        def run_stream():
            """Executa o stream síncrono em thread separada."""
            try:
                stream = self.llm.generate_stream(prompt, system, **kwargs)
                for token in stream:
                    if stop_event.is_set():
                        break
                    # Adicionar token à queue de forma não-bloqueante
                    try:
                        queue.put_nowait(token)
                    except:
                        pass
                queue.put_nowait(None)  # Sinal de fim
            except Exception as e:
                logger.error(f"Erro no stream síncrono: {e}")
                queue.put_nowait(f"Erro: {str(e)}")
                queue.put_nowait(None)
        
        try:
            # Executar stream em thread separada
            loop = asyncio.get_event_loop()
            task = loop.run_in_executor(None, run_stream)
            
            # Timeout máximo para evitar loop infinito (aumentado para dar tempo do modelo carregar)
            max_wait_time = 150.0  # 150 segundos
            start_time = time.time()
            
            # Consumir tokens da queue
            while True:
                # Verificar timeout global
                elapsed = time.time() - start_time
                if elapsed > max_wait_time:
                    logger.warning("Timeout máximo atingido no streaming")
                    stop_event.set()
                    break
                
                try:
                    # Aguardar token com timeout para verificar se task terminou
                    token = await asyncio.wait_for(queue.get(), timeout=0.5)
                    if token is None:  # Fim do stream
                        break
                    yield token
                except asyncio.TimeoutError:
                    # Verificar se a task terminou
                    if task.done():
                        # Processar tokens restantes
                        while not queue.empty():
                            try:
                                token = queue.get_nowait()
                                if token is None:
                                    return
                                yield token
                            except:
                                break
                        break
                    continue
                
        except Exception as e:
            logger.error(f"Erro no streaming assíncrono: {e}")
            stop_event.set()
            yield f"Erro ao processar: {str(e)}"
    
    async def chat_stream_async(
        self,
        messages: list,
        **kwargs
    ) -> AsyncIterator[str]:
        """
        Chat com streaming assíncrono.
        
        Args:
            messages: Lista de mensagens
            **kwargs: Parâmetros adicionais
        
        Yields:
            Tokens da resposta conforme são gerados
        """
        queue = asyncio.Queue()
        stop_event = asyncio.Event()
        
        def run_stream():
            """Executa o stream síncrono em thread separada."""
            try:
                stream = self.llm.chat_stream(messages, **kwargs)
                for token in stream:
                    if stop_event.is_set():
                        break
                    try:
                        queue.put_nowait(token)
                    except:
                        pass
                queue.put_nowait(None)  # Sinal de fim
            except Exception as e:
                logger.error(f"Erro no chat stream síncrono: {e}")
                queue.put_nowait(f"Erro: {str(e)}")
                queue.put_nowait(None)
        
        try:
            # Executar stream em thread separada
            loop = asyncio.get_event_loop()
            task = loop.run_in_executor(None, run_stream)
            
            # Timeout máximo para evitar loop infinito (aumentado para dar tempo do modelo carregar)
            max_wait_time = 150.0  # 150 segundos
            start_time = time.time()
            
            # Consumir tokens da queue
            while True:
                # Verificar timeout global
                elapsed = time.time() - start_time
                if elapsed > max_wait_time:
                    logger.warning("Timeout máximo atingido no chat streaming")
                    stop_event.set()
                    break
                
                try:
                    token = await asyncio.wait_for(queue.get(), timeout=0.5)
                    if token is None:  # Fim do stream
                        break
                    yield token
                except asyncio.TimeoutError:
                    if task.done():
                        while not queue.empty():
                            try:
                                token = queue.get_nowait()
                                if token is None:
                                    return
                                yield token
                            except:
                                break
                        break
                    continue
                
        except Exception as e:
            logger.error(f"Erro no chat streaming assíncrono: {e}")
            stop_event.set()
            yield f"Erro ao processar: {str(e)}"

