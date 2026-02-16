#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS 5.0 - Asynchronous Event Bus (Pub/Sub System)
====================================================
FASE 1.3: Sistema de comunicação desacoplada entre módulos usando pub/sub.

Responsibilities:
- Event publishing e subscription com tipos seguros
- Event filtering e routing inteligente
- Rate limiting e throttling de eventos
- Event persistence para auditoria
- Metrics e observabilidade do event bus

Philosophy:
- Comunicação desacoplada entre componentes
- Events como primeira classe de dados
- Observabilidade completa do fluxo de eventos
- Resiliência contra falhas em subscribers
"""

import asyncio
import logging
import threading
import time
import json
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import Dict, List, Optional, Any, Callable, Coroutine, Union, Set, Tuple
from dataclasses import dataclass, field, asdict
from collections import defaultdict, deque
import uuid
import weakref
import inspect
from concurrent.futures import ThreadPoolExecutor
import pickle
import sqlite3
import aiofiles

logger = logging.getLogger(__name__)

class EventPriority(Enum):
    """Prioridade de eventos"""
    EMERGENCY = "emergency"     # System failures, security breaches
    CRITICAL = "critical"       # UI updates, user actions
    HIGH = "high"              # AI responses, important state changes
    NORMAL = "normal"          # Regular updates, notifications
    LOW = "low"                # Background processing, stats updates
    DEBUG = "debug"            # Debug information, metrics

class EventType(Enum):
    """Tipos de eventos do sistema JARVIS"""
    # System events
    SYSTEM_STARTUP = "system.startup"
    SYSTEM_SHUTDOWN = "system.shutdown"
    SYSTEM_ERROR = "system.error"
    SYSTEM_WARNING = "system.warning"
    SYSTEM_HEALTH_CHECK = "system.health_check"
    
    # Evolution/Self-Healing events
    SYSTEM_OBSERVER_REPORT = "system.observer.report"
    SYSTEM_DIAGNOSTIC_PLAN = "system.diagnostic.plan"
    SYSTEM_CORRECTION_EXECUTED = "system.correction.executed"
    SYSTEM_CORRECTION_FAILED = "system.correction.failed"
    SYSTEM_CORRECTION_SUCCEEDED = "system.correction.succeeded"

    # UI events
    UI_COMMAND = "ui.command"
    UI_RESPONSE = "ui.response"
    UI_STATE_CHANGE = "ui.state_change"
    UI_ERROR = "ui.error"
    
    # AI events
    AI_QUERY = "ai.query"
    AI_RESPONSE = "ai.response"
    AI_LEARNING = "ai.learning"
    AI_MODEL_CHANGE = "ai.model_change"
    AI_TRAINING_COMPLETE = "ai.training_complete"
    
    # Memory events
    MEMORY_STORE = "memory.store"
    MEMORY_RETRIEVE = "memory.retrieve"
    MEMORY_UPDATE = "memory.update"
    MEMORY_DELETE = "memory.delete"
    MEMORY_BACKUP = "memory.backup"
    
    # Vision events
    VISION_CAPTURE = "vision.capture"
    VISION_DETECT = "vision.detect"
    VISION_TRACK = "vision.track"
    VISION_ANALYZE = "vision.analyze"
    VISION_SCREEN_CHANGE = "vision.screen_change"
    VISION_SCREEN_ANALYSIS = "vision.screen_analysis"
    
    # Audio events
    AUDIO_INPUT = "audio.input"
    AUDIO_OUTPUT = "audio.output"
    AUDIO_PROCESS = "audio.process"
    AUDIO_VOICE_COMMAND = "audio.voice_command"
    AUDIO_TRANSCRIPTION = "audio.transcription"
    
    # Network events
    NETWORK_REQUEST = "network.request"
    NETWORK_RESPONSE = "network.response"
    NETWORK_ERROR = "network.error"
    NETWORK_MESH_UPDATE = "network.mesh_update"
    
    # Custom/Plugin events
    PLUGIN_LOADED = "plugin.loaded"
    PLUGIN_UNLOADED = "plugin.unloaded"
    PLUGIN_ERROR = "plugin.error"
    CUSTOM_EVENT = "custom.event"

@dataclass
class Event:
    """Evento do sistema"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: EventType = EventType.CUSTOM_EVENT
    priority: EventPriority = EventPriority.NORMAL
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Event data
    data: Dict[str, Any] = field(default_factory=dict)
    source: Optional[str] = None          # Module or component that emitted the event
    target: Optional[str] = None          # Specific target (optional)
    correlation_id: Optional[str] = None  # For tracking related events
    
    # Metadata
    tags: List[str] = field(default_factory=list)
    ttl_seconds: Optional[float] = None   # Time to live
    retry_count: int = 0
    max_retries: int = 3
    
    def is_expired(self) -> bool:
        """Check if event has expired based on TTL"""
        if self.ttl_seconds is None:
            return False
        return (datetime.now() - self.timestamp).total_seconds() > self.ttl_seconds
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        data['type'] = self.type.value
        data['priority'] = self.priority.value
        data['timestamp'] = self.timestamp.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Event':
        """Create from dictionary"""
        event_data = data.copy()
        event_data['type'] = EventType(event_data['type'])
        event_data['priority'] = EventPriority(event_data['priority'])
        event_data['timestamp'] = datetime.fromisoformat(event_data['timestamp'])
        return cls(**event_data)

@dataclass
class Subscription:
    """Subscription para eventos"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_types: Set[EventType] = field(default_factory=set)
    callback: Optional[Callable[[Event], Union[None, Coroutine]]] = None
    
    # Filters
    priority_filter: Optional[Set[EventPriority]] = None
    source_filter: Optional[Set[str]] = None
    tag_filter: Optional[Set[str]] = None
    data_filter: Optional[Callable[[Dict[str, Any]], bool]] = None
    
    # Configuration
    max_queue_size: int = 1000
    batch_size: int = 1               # Events to process at once
    batch_timeout_seconds: float = 0.1  # Max time to wait for batch
    
    # State
    is_active: bool = True
    total_events_received: int = 0
    total_events_processed: int = 0
    last_event_time: Optional[datetime] = None
    error_count: int = 0
    last_error: Optional[str] = None
    
    # Queue for async processing
    event_queue: asyncio.Queue = field(default_factory=lambda: asyncio.Queue())
    
    def matches(self, event: Event) -> bool:
        """Check if event matches this subscription filters"""
        
        # Type filter
        if self.event_types and event.type not in self.event_types:
            return False
        
        # Priority filter
        if self.priority_filter and event.priority not in self.priority_filter:
            return False
        
        # Source filter
        if self.source_filter and event.source not in self.source_filter:
            return False
        
        # Tag filter (at least one tag must match)
        if self.tag_filter and not any(tag in event.tags for tag in self.tag_filter):
            return False
        
        # Custom data filter
        if self.data_filter and not self.data_filter(event.data):
            return False
        
        return True

class EventPersistence:
    """Persistência de eventos para auditoria"""
    
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or "data/database/event_log.db"
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database for events"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS events (
                        id TEXT PRIMARY KEY,
                        type TEXT NOT NULL,
                        priority TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        source TEXT,
                        target TEXT,
                        correlation_id TEXT,
                        data_json TEXT,
                        tags_json TEXT,
                        ttl_seconds REAL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_events_type ON events(type)
                """)
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp)
                """)
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_events_source ON events(source)
                """)
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_events_correlation ON events(correlation_id)
                """)
        except Exception as e:
            logger.error(f"Failed to initialize event database: {e}")
    
    def store_event(self, event: Event):
        """Store event in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO events 
                    (id, type, priority, timestamp, source, target, correlation_id, 
                     data_json, tags_json, ttl_seconds)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    event.id,
                    event.type.value,
                    event.priority.value,
                    event.timestamp.isoformat(),
                    event.source,
                    event.target,
                    event.correlation_id,
                    json.dumps(event.data),
                    json.dumps(event.tags),
                    event.ttl_seconds
                ))
        except Exception as e:
            logger.error(f"Failed to store event {event.id}: {e}")
    
    def query_events(self, 
                    event_type: Optional[EventType] = None,
                    source: Optional[str] = None,
                    start_time: Optional[datetime] = None,
                    end_time: Optional[datetime] = None,
                    limit: int = 100) -> List[Event]:
        """Query stored events"""
        try:
            query = "SELECT * FROM events WHERE 1=1"
            params = []
            
            if event_type:
                query += " AND type = ?"
                params.append(event_type.value)
            
            if source:
                query += " AND source = ?"
                params.append(source)
            
            if start_time:
                query += " AND timestamp >= ?"
                params.append(start_time.isoformat())
            
            if end_time:
                query += " AND timestamp <= ?"
                params.append(end_time.isoformat())
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                rows = conn.execute(query, params).fetchall()
                
                events = []
                for row in rows:
                    event_data = dict(row)
                    event_data['data'] = json.loads(event_data['data_json'])
                    event_data['tags'] = json.loads(event_data['tags_json'])
                    del event_data['data_json']
                    del event_data['tags_json']
                    del event_data['created_at']
                    
                    events.append(Event.from_dict(event_data))
                
                return events
                
        except Exception as e:
            logger.error(f"Failed to query events: {e}")
            return []

class AsyncEventBus:
    """
    Event Bus Assíncrono para comunicação pub/sub entre módulos JARVIS
    
    Features:
    - Publishing e subscription de eventos tipados
    - Filtering avançado de eventos
    - Rate limiting e throttling
    - Persistência para auditoria
    - Metrics e observabilidade
    """
    
    def __init__(self, 
                 max_event_queue_size: int = 10000,
                 enable_persistence: bool = True,
                 persistence_db_path: Optional[str] = None):
        
        # Core state
        self._subscriptions: Dict[str, Subscription] = {}
        self._running = False
        self._event_dispatcher_task: Optional[asyncio.Task] = None
        
        # Event queues by priority
        self._event_queues: Dict[EventPriority, asyncio.Queue] = {
            priority: asyncio.Queue(maxsize=max_event_queue_size) 
            for priority in EventPriority
        }
        
        # Persistence
        self.enable_persistence = enable_persistence
        self._persistence = EventPersistence(persistence_db_path) if enable_persistence else None
        
        # Rate limiting
        self._rate_limits: Dict[str, Dict[str, Any]] = {}  # source -> rate limit info
        
        # Metrics
        self.total_events_published = 0
        self.total_events_delivered = 0
        self.total_delivery_failures = 0
        self.start_time: Optional[datetime] = None
        
        # Configuration
        self.max_delivery_failures_per_subscription = 10
        self.event_retention_days = 30
        
        logger.info("📡 Async Event Bus initialized")
    
    async def start(self):
        """Start the event bus"""
        if self._running:
            logger.warning("Event bus already running")
            return
        
        self._running = True
        self.start_time = datetime.now()
        
        logger.info("🚀 Async Event Bus starting...")
        
        # Start event dispatcher
        self._event_dispatcher_task = asyncio.create_task(self._event_dispatcher())
        
        logger.info("✅ Async Event Bus started")
    
    async def stop(self, timeout: float = 30.0):
        """Stop the event bus gracefully"""
        if not self._running:
            return
        
        logger.info("🛑 Stopping Async Event Bus...")
        self._running = False
        
        # Stop dispatcher
        if self._event_dispatcher_task:
            self._event_dispatcher_task.cancel()
            try:
                await asyncio.wait_for(self._event_dispatcher_task, timeout=5.0)
            except (asyncio.CancelledError, asyncio.TimeoutError):
                pass
        
        logger.info("✅ Async Event Bus stopped")
    
    def publish(self, 
               event_type: EventType,
               data: Optional[Dict[str, Any]] = None,
               priority: EventPriority = EventPriority.NORMAL,
               source: Optional[str] = None,
               target: Optional[str] = None,
               correlation_id: Optional[str] = None,
               tags: Optional[List[str]] = None,
               ttl_seconds: Optional[float] = None) -> str:
        """
        Publish an event
        
        Returns:
            Event ID
        """
        event = Event(
            type=event_type,
            data=data or {},
            priority=priority,
            source=source,
            target=target,
            correlation_id=correlation_id,
            tags=tags or [],
            ttl_seconds=ttl_seconds
        )
        
        return self.publish_event(event)
    
    def publish_event(self, event: Event) -> str:
        """Publish a pre-constructed event"""
        try:
            # Check rate limiting
            if not self._check_rate_limit(event.source):
                logger.warning(f"Rate limit exceeded for source: {event.source}")
                return event.id
            
            # Add to appropriate priority queue
            queue = self._event_queues[event.priority]
            
            # Non-blocking put (drop if queue is full)
            try:
                queue.put_nowait(event)
                self.total_events_published += 1
                
                logger.debug(f"📤 Published event: {event.type.value} (ID: {event.id[:8]})")
                
                # Store in persistence if enabled
                if self._persistence:
                    self._persistence.store_event(event)
                
            except asyncio.QueueFull:
                logger.warning(f"Event queue full for priority {event.priority.value}, dropping event {event.id}")
            
            return event.id
            
        except Exception as e:
            logger.error(f"Failed to publish event: {e}")
            return event.id
    
    def subscribe(self,
                 event_types: Union[EventType, List[EventType]],
                 callback: Callable[[Event], Union[None, Coroutine]],
                 priority_filter: Optional[List[EventPriority]] = None,
                 source_filter: Optional[List[str]] = None,
                 tag_filter: Optional[List[str]] = None,
                 data_filter: Optional[Callable[[Dict[str, Any]], bool]] = None,
                 max_queue_size: int = 1000,
                 batch_size: int = 1,
                 batch_timeout_seconds: float = 0.1) -> str:
        """
        Subscribe to events
        
        Returns:
            Subscription ID
        """
        if isinstance(event_types, EventType):
            event_types = [event_types]
        
        subscription = Subscription(
            event_types=set(event_types),
            callback=callback,
            priority_filter=set(priority_filter) if priority_filter else None,
            source_filter=set(source_filter) if source_filter else None,
            tag_filter=set(tag_filter) if tag_filter else None,
            data_filter=data_filter,
            max_queue_size=max_queue_size,
            batch_size=batch_size,
            batch_timeout_seconds=batch_timeout_seconds
        )
        
        self._subscriptions[subscription.id] = subscription
        
        # Start processing task for this subscription
        asyncio.create_task(self._process_subscription(subscription))
        
        logger.debug(f"📋 New subscription: {[t.value for t in event_types]} (ID: {subscription.id[:8]})")
        
        return subscription.id
    
    def unsubscribe(self, subscription_id: str) -> bool:
        """Unsubscribe from events"""
        if subscription_id in self._subscriptions:
            subscription = self._subscriptions[subscription_id]
            subscription.is_active = False
            del self._subscriptions[subscription_id]
            
            logger.debug(f"🚫 Unsubscribed: {subscription_id[:8]}")
            return True
        return False
    
    def get_subscription_stats(self, subscription_id: str) -> Optional[Dict[str, Any]]:
        """Get statistics for a subscription"""
        if subscription_id not in self._subscriptions:
            return None
        
        sub = self._subscriptions[subscription_id]
        return {
            "id": sub.id,
            "event_types": [t.value for t in sub.event_types],
            "is_active": sub.is_active,
            "total_events_received": sub.total_events_received,
            "total_events_processed": sub.total_events_processed,
            "error_count": sub.error_count,
            "last_error": sub.last_error,
            "queue_size": sub.event_queue.qsize(),
            "last_event_time": sub.last_event_time.isoformat() if sub.last_event_time else None
        }
    
    def get_bus_stats(self) -> Dict[str, Any]:
        """Get event bus statistics"""
        total_subscriptions = len(self._subscriptions)
        active_subscriptions = sum(1 for s in self._subscriptions.values() if s.is_active)
        
        queue_sizes = {
            priority.value: queue.qsize() 
            for priority, queue in self._event_queues.items()
        }
        
        uptime = None
        if self.start_time:
            uptime = (datetime.now() - self.start_time).total_seconds()
        
        return {
            "running": self._running,
            "uptime_seconds": uptime,
            "total_subscriptions": total_subscriptions,
            "active_subscriptions": active_subscriptions,
            "total_events_published": self.total_events_published,
            "total_events_delivered": self.total_events_delivered,
            "total_delivery_failures": self.total_delivery_failures,
            "queue_sizes": queue_sizes,
            "persistence_enabled": self.enable_persistence
        }
    
    def set_rate_limit(self, source: str, max_events: int, time_window_seconds: float):
        """Set rate limit for a specific source"""
        self._rate_limits[source] = {
            "max_events": max_events,
            "time_window": time_window_seconds,
            "events": deque(),
            "last_reset": time.time()
        }
    
    def query_events(self, **kwargs) -> List[Event]:
        """Query historical events (requires persistence)"""
        if not self._persistence:
            logger.error("Event persistence not enabled")
            return []
        
        return self._persistence.query_events(**kwargs)
    
    async def _event_dispatcher(self):
        """Main event dispatcher loop"""
        while self._running:
            try:
                # Process events by priority (highest first)
                event_processed = False
                
                for priority in EventPriority:
                    queue = self._event_queues[priority]
                    
                    try:
                        # Get event with short timeout to check other priorities
                        event = await asyncio.wait_for(queue.get(), timeout=0.1)
                        await self._dispatch_event(event)
                        event_processed = True
                        break  # Process one event per cycle to maintain priority
                        
                    except asyncio.TimeoutError:
                        continue  # Try next priority
                
                # Small delay if no events processed
                if not event_processed:
                    await asyncio.sleep(0.01)
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Event dispatcher error: {e}")
                await asyncio.sleep(1.0)
    
    async def _dispatch_event(self, event: Event):
        """Dispatch event to matching subscriptions"""
        # Skip expired events
        if event.is_expired():
            logger.debug(f"Skipping expired event: {event.id}")
            return
        
        matching_subscriptions = [
            sub for sub in self._subscriptions.values()
            if sub.is_active and sub.matches(event)
        ]
        
        if not matching_subscriptions:
            logger.debug(f"No subscribers for event: {event.type.value}")
            return
        
        # Deliver to each matching subscription
        for subscription in matching_subscriptions:
            try:
                await subscription.event_queue.put(event)
                subscription.total_events_received += 1
                subscription.last_event_time = datetime.now()
                
            except asyncio.QueueFull:
                logger.warning(f"Subscription queue full: {subscription.id[:8]}")
                subscription.error_count += 1
    
    async def _process_subscription(self, subscription: Subscription):
        """Process events for a specific subscription"""
        while subscription.is_active and self._running:
            try:
                events_batch = []
                
                # Collect events for batch processing
                try:
                    # Wait for first event
                    event = await asyncio.wait_for(
                        subscription.event_queue.get(), 
                        timeout=1.0
                    )
                    events_batch.append(event)
                    
                    # Collect additional events for batch (if batch_size > 1)
                    if subscription.batch_size > 1:
                        batch_timeout = subscription.batch_timeout_seconds
                        end_time = time.time() + batch_timeout
                        
                        while len(events_batch) < subscription.batch_size and time.time() < end_time:
                            try:
                                remaining_time = max(0, end_time - time.time())
                                event = await asyncio.wait_for(
                                    subscription.event_queue.get(),
                                    timeout=remaining_time
                                )
                                events_batch.append(event)
                            except asyncio.TimeoutError:
                                break
                    
                except asyncio.TimeoutError:
                    continue  # No events to process
                
                # Process the batch
                if events_batch:
                    await self._invoke_subscription_callback(subscription, events_batch)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Subscription processing error: {e}")
                subscription.error_count += 1
                subscription.last_error = str(e)
                await asyncio.sleep(1.0)
    
    async def _invoke_subscription_callback(self, subscription: Subscription, events: List[Event]):
        """Invoke subscription callback with events"""
        try:
            callback = subscription.callback
            
            # Process each event in the batch
            for event in events:
                try:
                    if inspect.iscoroutinefunction(callback):
                        # Async callback
                        await callback(event)
                    else:
                        # Sync callback - run in thread pool to avoid blocking
                        loop = asyncio.get_event_loop()
                        if callback and asyncio.iscoroutinefunction(callback):
                            await callback(event)
                        elif callback:
                            with ThreadPoolExecutor(max_workers=1) as executor:
                                await loop.run_in_executor(executor, callback, event)
                    
                    subscription.total_events_processed += 1
                    self.total_events_delivered += 1
                    
                except Exception as e:
                    logger.error(f"Callback error for subscription {subscription.id[:8]}: {e}")
                    subscription.error_count += 1
                    subscription.last_error = str(e)
                    self.total_delivery_failures += 1
                    
                    # Disable subscription if too many failures
                    if subscription.error_count >= self.max_delivery_failures_per_subscription:
                        logger.error(f"Disabling subscription {subscription.id[:8]} due to excessive errors")
                        subscription.is_active = False
                        break
                        
        except Exception as e:
            logger.error(f"Subscription callback invocation failed: {e}")
            subscription.error_count += 1
            self.total_delivery_failures += 1
    
    def _check_rate_limit(self, source: Optional[str]) -> bool:
        """Check if source is within rate limits"""
        if not source or source not in self._rate_limits:
            return True
        
        limit_info = self._rate_limits[source]
        current_time = time.time()
        
        # Clean old events outside time window
        time_window = limit_info["time_window"]
        cutoff_time = current_time - time_window
        
        while limit_info["events"] and limit_info["events"][0] < cutoff_time:
            limit_info["events"].popleft()
        
        # Check if under limit
        if len(limit_info["events"]) < limit_info["max_events"]:
            limit_info["events"].append(current_time)
            return True
        
        return False

# Global instance
event_bus = AsyncEventBus()

# Event publishing helpers
def emit_system_event(event_type: EventType, data: Optional[Dict] = None, **kwargs):
    """Convenience function for emitting system events"""
    return event_bus.publish(event_type, data, source="system", **kwargs)

def emit_ui_event(event_type: EventType, data: Optional[Dict] = None, **kwargs):
    """Convenience function for emitting UI events"""
    return event_bus.publish(event_type, data, source="ui", **kwargs)

def emit_ai_event(event_type: EventType, data: Optional[Dict] = None, **kwargs):
    """Convenience function for emitting AI events"""
    return event_bus.publish(event_type, data, source="ai", **kwargs)

if __name__ == "__main__":
    # Test the event bus
    async def test_event_bus():
        print("🧪 Testing Async Event Bus")
        print("=" * 50)
        
        # Start event bus
        await event_bus.start()
        
        # Test subscriber
        received_events = []
        
        async def test_subscriber(event: Event):
            print(f"📥 Received: {event.type.value} - {event.data}")
            received_events.append(event)
        
        # Subscribe to AI events
        sub_id = event_bus.subscribe(  # noqa: F841
            [EventType.AI_QUERY, EventType.AI_RESPONSE],
            test_subscriber,
            priority_filter=[EventPriority.HIGH, EventPriority.NORMAL]
        )
        
        # Publish some test events
        print("\n📤 Publishing events...")
        
        event_bus.publish(EventType.AI_QUERY, {
            "query": "What's the weather?",
            "user": "test_user"
        }, priority=EventPriority.HIGH, source="test")
        
        event_bus.publish(EventType.AI_RESPONSE, {
            "response": "It's sunny!",
            "confidence": 0.9
        }, priority=EventPriority.NORMAL, source="ai_module")
        
        event_bus.publish(EventType.SYSTEM_STARTUP, {
            "version": "5.0",
            "modules": ["ai", "ui", "vision"]
        }, priority=EventPriority.CRITICAL, source="boot_manager")
        
        # Wait for events to be processed
        await asyncio.sleep(2)
        
        # Show stats
        print("\n📊 Event Bus Stats:")
        stats = event_bus.get_bus_stats()
        for key, value in stats.items():
            print(f"{key}: {value}")
        
        print(f"\n📥 Received {len(received_events)} events")
        
        # Query historical events
        print("\n🔍 Querying historical events...")
        historical = event_bus.query_events(limit=5)
        for event in historical:
            print(f"  {event.timestamp.strftime('%H:%M:%S')} - {event.type.value}")
        
        # Stop event bus
        await event_bus.stop()
        
        print("✅ Test completed")
    
    asyncio.run(test_event_bus())