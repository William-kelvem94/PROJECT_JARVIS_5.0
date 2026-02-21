"""
TraceManager - Sistema de rastreamento distribuído para JARVIS 5.0
Gerencia traces, spans e observabilidade de operações.
"""

import json
import logging
import time
import uuid
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any
from contextlib import asynccontextmanager
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class TraceSpan:
    """Representa um span individual em um trace."""

    span_id: str
    trace_id: str
    parent_span_id: Optional[str]
    name: str
    start_time: float
    end_time: Optional[float] = None
    duration_ms: Optional[float] = None
    attributes: Dict[str, Any] = None
    events: List[Dict[str, Any]] = None
    status: str = "ok"
    error_message: Optional[str] = None

    def __post_init__(self):
        if self.attributes is None:
            self.attributes = {}
        if self.events is None:
            self.events = []

    def add_event(self, name: str, attributes: Dict[str, Any] = None):
        """Adiciona um evento ao span."""
        event = {"name": name, "timestamp": time.time(), "attributes": attributes or {}}
        self.events.append(event)

    def set_error(self, error_message: str):
        """Marca o span como erro."""
        self.status = "error"
        self.error_message = error_message
        self.add_event("error", {"message": error_message})

    def finish(self):
        """Finaliza o span."""
        self.end_time = time.time()
        self.duration_ms = (self.end_time - self.start_time) * 1000


@dataclass
class Trace:
    """Representa um trace completo."""

    trace_id: str
    root_span_id: str
    spans: Dict[str, TraceSpan]
    start_time: float
    end_time: Optional[float] = None
    total_duration_ms: Optional[float] = None
    service_name: str = "jarvis"
    attributes: Dict[str, Any] = None

    def __post_init__(self):
        if self.attributes is None:
            self.attributes = {}

    def add_span(self, span: TraceSpan):
        """Adiciona um span ao trace."""
        self.spans[span.span_id] = span

    def finish(self):
        """Finaliza o trace."""
        self.end_time = time.time()
        if self.root_span_id in self.spans:
            root_span = self.spans[self.root_span_id]
            if root_span.end_time:
                self.total_duration_ms = (
                    root_span.end_time - root_span.start_time
                ) * 1000


class TraceManager:
    """
    Gerenciador de rastreamento distribuído para observabilidade completa.
    """

    def __init__(self, max_traces: int = 1000, trace_dir: Path = None):
        self.max_traces = max_traces
        self.active_traces: Dict[str, Trace] = {}
        self.completed_traces: Dict[str, Trace] = {}
        self.active_spans: Dict[str, TraceSpan] = {}
        self.trace_dir = trace_dir or Path("data/logs/traces")
        self.trace_dir.mkdir(parents=True, exist_ok=True)

        # Configuração de sampling
        self.sample_rate = 1.0  # 100% sampling por padrão

    def should_sample(self) -> bool:
        """Determina se deve samplear o trace."""
        return True  # Sempre samplear por enquanto

    def start_trace(self, name: str, attributes: Dict[str, Any] = None) -> str:
        """
        Inicia um novo trace.

        Args:
            name: Nome do trace
            attributes: Atributos iniciais

        Returns:
            ID do trace criado
        """
        if not self.should_sample():
            return None

        trace_id = str(uuid.uuid4())
        root_span_id = str(uuid.uuid4())

        root_span = TraceSpan(
            span_id=root_span_id,
            trace_id=trace_id,
            parent_span_id=None,
            name=name,
            start_time=time.time(),
            attributes=attributes or {},
        )

        trace = Trace(
            trace_id=trace_id,
            root_span_id=root_span_id,
            spans={root_span_id: root_span},
            start_time=time.time(),
            attributes=attributes or {},
        )

        self.active_traces[trace_id] = trace
        self.active_spans[root_span_id] = root_span

        logger.debug(f"Started trace: {trace_id} - {name}")
        return trace_id

    def start_span(
        self, name: str, parent_span_id: str = None, attributes: Dict[str, Any] = None
    ) -> Optional[str]:
        """
        Inicia um novo span dentro de um trace.

        Args:
            name: Nome do span
            parent_span_id: ID do span pai
            attributes: Atributos do span

        Returns:
            ID do span criado ou None se não deve samplear
        """
        if not self.should_sample():
            return None

        # Encontra o trace do span pai
        parent_span = self.active_spans.get(parent_span_id)
        if not parent_span:
            logger.warning(f"Parent span {parent_span_id} not found")
            return None

        trace = self.active_traces.get(parent_span.trace_id)
        if not trace:
            logger.warning(f"Trace {parent_span.trace_id} not found")
            return None

        span_id = str(uuid.uuid4())
        span = TraceSpan(
            span_id=span_id,
            trace_id=trace.trace_id,
            parent_span_id=parent_span_id,
            name=name,
            start_time=time.time(),
            attributes=attributes or {},
        )

        trace.add_span(span)
        self.active_spans[span_id] = span

        logger.debug(f"Started span: {span_id} - {name} (parent: {parent_span_id})")
        return span_id

    def add_span_event(
        self, span_id: str, event_name: str, attributes: Dict[str, Any] = None
    ):
        """
        Adiciona um evento a um span.

        Args:
            span_id: ID do span
            event_name: Nome do evento
            attributes: Atributos do evento
        """
        span = self.active_spans.get(span_id)
        if span:
            span.add_event(event_name, attributes)
        else:
            logger.warning(f"Span {span_id} not found for event {event_name}")

    def set_span_error(self, span_id: str, error_message: str):
        """
        Marca um span como erro.

        Args:
            span_id: ID do span
            error_message: Mensagem de erro
        """
        span = self.active_spans.get(span_id)
        if span:
            span.set_error(error_message)
        else:
            logger.warning(f"Span {span_id} not found for error")

    def finish_span(self, span_id: str):
        """
        Finaliza um span.

        Args:
            span_id: ID do span
        """
        span = self.active_spans.get(span_id)
        if span:
            span.finish()
            logger.debug(
                f"Finished span: {span_id} - {span.name} ({span.duration_ms:.2f}ms)"
            )
        else:
            logger.warning(f"Span {span_id} not found to finish")

    def finish_trace(self, trace_id: str):
        """
        Finaliza um trace e o move para completed.

        Args:
            trace_id: ID do trace
        """
        trace = self.active_traces.get(trace_id)
        if trace:
            trace.finish()

            # Move para completed
            self.completed_traces[trace_id] = trace
            del self.active_traces[trace_id]

            # Limpa spans ativos deste trace
            span_ids_to_remove = [
                sid
                for sid, span in self.active_spans.items()
                if span.trace_id == trace_id
            ]
            for sid in span_ids_to_remove:
                del self.active_spans[sid]

            # Salva o trace
            self._save_trace(trace)

            # Mantém limite de traces
            if len(self.completed_traces) > self.max_traces:
                oldest_trace_id = min(
                    self.completed_traces.keys(),
                    key=lambda x: self.completed_traces[x].start_time,
                )
                del self.completed_traces[oldest_trace_id]

            logger.info(f"Finished trace: {trace_id} ({trace.total_duration_ms:.2f}ms)")
        else:
            logger.warning(f"Trace {trace_id} not found to finish")

    def _save_trace(self, trace: Trace):
        """Salva um trace em arquivo."""
        try:
            trace_file = self.trace_dir / f"{trace.trace_id}.json"
            trace_data = {
                "trace_id": trace.trace_id,
                "root_span_id": trace.root_span_id,
                "start_time": trace.start_time,
                "end_time": trace.end_time,
                "total_duration_ms": trace.total_duration_ms,
                "service_name": trace.service_name,
                "attributes": trace.attributes,
                "spans": {sid: asdict(span) for sid, span in trace.spans.items()},
            }

            with open(trace_file, "w", encoding="utf-8") as f:
                json.dump(trace_data, f, indent=2, default=str)

        except Exception as e:
            logger.error(f"Failed to save trace {trace.trace_id}: {e}")

    def get_trace(self, trace_id: str) -> Optional[Trace]:
        """
        Obtém um trace por ID.

        Args:
            trace_id: ID do trace

        Returns:
            Trace ou None se não encontrado
        """
        return self.completed_traces.get(trace_id)

    def get_active_traces(self) -> List[Trace]:
        """Retorna lista de traces ativos."""
        return list(self.active_traces.values())

    def get_completed_traces(self, limit: int = 100) -> List[Trace]:
        """Retorna lista de traces completados."""
        traces = list(self.completed_traces.values())
        return sorted(traces, key=lambda x: x.start_time, reverse=True)[:limit]

    def get_trace_summary(self, trace_id: str) -> Optional[Dict[str, Any]]:
        """
        Retorna um resumo de um trace.

        Args:
            trace_id: ID do trace

        Returns:
            Dicionário com resumo ou None
        """
        trace = self.get_trace(trace_id)
        if not trace:
            return None

        return {
            "trace_id": trace.trace_id,
            "root_span_name": trace.spans[trace.root_span_id].name,
            "start_time": trace.start_time,
            "total_duration_ms": trace.total_duration_ms,
            "span_count": len(trace.spans),
            "status": "completed",
            "attributes": trace.attributes,
        }

    @asynccontextmanager
    async def trace_context(self, name: str, attributes: Dict[str, Any] = None):
        """
        Context manager para tracing automático.

        Usage:
            async with trace_manager.trace_context("operation_name"):
                # código a ser traced
                pass
        """
        trace_id = self.start_trace(name, attributes)
        try:
            yield trace_id
        except Exception as e:
            if trace_id:
                root_span_id = self.active_traces[trace_id].root_span_id
                self.set_span_error(root_span_id, str(e))
            raise
        finally:
            if trace_id:
                self.finish_trace(trace_id)

    @asynccontextmanager
    async def span_context(
        self, name: str, parent_span_id: str = None, attributes: Dict[str, Any] = None
    ):
        """
        Context manager para span automático.

        Usage:
            async with trace_manager.span_context("sub_operation", parent_span_id):
                # código a ser traced
                pass
        """
        span_id = self.start_span(name, parent_span_id, attributes)
        try:
            yield span_id
        except Exception as e:
            if span_id:
                self.set_span_error(span_id, str(e))
            raise
        finally:
            if span_id:
                self.finish_span(span_id)


# Singleton instance
trace_manager = TraceManager()
