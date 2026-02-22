#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS 5.0 - Unified Logging System
====================================
Sistema unificado de logging com organização inteligente e prevenção de duplicatas.

Features:
- Logs organizados por componente
- Prevenção de duplicatas
- Rotações automáticas
- Formatação consistente
- Integração com Blackbox Logger
"""

import logging
import sys
import threading
from pathlib import Path
from typing import Dict, Optional, Any
from datetime import datetime
from logging.handlers import RotatingFileHandler


class JARVISFormatter(logging.Formatter):
    """Custom formatter for JARVIS logs"""

    def __init__(self):
        super().__init__()
        self._component_colors = {
            "CORE": "\033[1;31m",  # Red
            "AI": "\033[1;34m",  # Blue
            "VISION": "\033[1;32m",  # Green
            "AUDIO": "\033[1;33m",  # Yellow
            "MEMORY": "\033[1;35m",  # Magenta
            "NETWORK": "\033[1;36m",  # Cyan
            "SYSTEM": "\033[1;37m",  # White
        }
        self._reset = "\033[0m"

    def format(self, record):
        # Add timestamp
        timestamp = datetime.fromtimestamp(record.created).strftime("%H:%M:%S")

        # Extract component from logger name
        component = "SYSTEM"
        if "." in record.name:
            parts = record.name.split(".")
            if len(parts) >= 2 and parts[0] == "jarvis":
                component = parts[1].upper()

        # Format level
        level_str = f"[{record.levelname}]"

        # Format message
        message = record.getMessage()

        # Add context if available
        if "context" in record.__dict__ and record.__dict__["context"]:
            message += f" | {record.__dict__['context']}"

        # Colorize for console
        if component in self._component_colors:
            component_colored = (
                f"{self._component_colors[component]}{component}{self._reset}"
            )
        else:
            component_colored = component

        return f"[{timestamp}] {level_str} {component_colored}: {message}"


class DuplicateFilter(logging.Filter):
    """Filter to prevent duplicate log messages"""

    def __init__(self):
        super().__init__()
        self._last_messages = {}
        self._lock = threading.Lock()

    def filter(self, record):
        # Create unique key from message and level
        key = (record.levelno, record.getMessage())

        with self._lock:
            # Check if this exact message was logged recently
            current_time = record.created
            if key in self._last_messages:
                last_time = self._last_messages[key]
                # If same message within 1 second, filter it out
                if current_time - last_time < 1.0:
                    return False

            # Update last seen time
            self._last_messages[key] = current_time

            # Clean old entries (keep only last 1000)
            if len(self._last_messages) > 1000:
                # Remove oldest entries
                sorted_items = sorted(self._last_messages.items(), key=lambda x: x[1])
                self._last_messages = dict(sorted_items[-500:])  # Keep newest 500

        return True


class GlobalDuplicateFilter(logging.Filter):
    """Global filter to prevent duplicate messages across all loggers"""

    _instance = None
    _last_messages = {}
    _component_states = {}  # Track component health states
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def filter(self, record):
        message = record.getMessage()

        # Special handling for watchdog messages
        if "Watchdog:" in message and record.name == "jarvis.watchdog":
            return self._filter_watchdog_message(record, message)

        # Standard duplicate filtering for other messages
        key = (record.levelno, record.getMessage(), record.name)

        with self._lock:
            current_time = record.created
            if key in self._last_messages:
                last_time = self._last_messages[key]
                # If same message within 1 second, filter it out
                if current_time - last_time < 1.0:
                    return False

            # Update last seen time
            self._last_messages[key] = current_time

            # Cleanup old entries (keep only last 2 minutes of history)
            cutoff = current_time - 120  # 2 minutes
            self._last_messages = {
                k: v for k, v in self._last_messages.items() if v > cutoff
            }

        return True

    def _filter_watchdog_message(self, record, message):
        """Smart filtering for watchdog messages to reduce noise"""
        import re

        # Extract component name and status from message
        # Format: "💀 Watchdog: ComponentName is DEAD (No heartbeat for X.Xs)"
        # Or: "⚠️ Watchdog: ComponentName is SLOW (Delayed X.Xs)"

        dead_match = re.search(r"Watchdog:\s*(\w+)\s*is\s*DEAD", message)
        slow_match = re.search(r"Watchdog:\s*(\w+)\s*is\s*SLOW", message)

        component = None
        state = None

        if dead_match:
            component = dead_match.group(1)
            state = "DEAD"
        elif slow_match:
            component = slow_match.group(1)
            state = "SLOW"

        if component and state:
            return self._should_show_component_state(record, component, state)

        # If we can't parse it, use standard filtering
        return True

    def _should_show_component_state(self, record, component, state):
        """Decide whether to show a component state change"""
        key = f"{component}_{state}"
        current_time = record.created

        with self._lock:
            if key not in self._component_states:
                # First time seeing this state, always show
                self._component_states[key] = {
                    "first_seen": current_time,
                    "last_shown": current_time,
                    "show_count": 1,
                }
                return True

            state_info = self._component_states[key]

            # For DEAD states, show every 30 seconds max
            if state == "DEAD":
                if current_time - state_info["last_shown"] > 30.0:
                    state_info["last_shown"] = current_time
                    state_info["show_count"] += 1
                    return True
                else:
                    return False

            # For SLOW states, show every 60 seconds max
            elif state == "SLOW":
                if current_time - state_info["last_shown"] > 60.0:
                    state_info["last_shown"] = current_time
                    state_info["show_count"] += 1
                    return True
                else:
                    return False

            # For other states, show normally
            return True


class JARVISLogger:
    """Unified logger for JARVIS system"""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.loggers = {}
        self.handlers = {}
        self.filters = {}
        self._initialized = True

    def setup_component_logger(
        self,
        component: str,
        log_dir: Path,
        level: int = logging.INFO,
        max_bytes: int = 10 * 1024 * 1024,
        backup_count: int = 5,
    ) -> logging.Logger:
        """
        Setup a component-specific logger

        Args:
            component: Component name (e.g., 'ai_agent', 'vision_system')
            log_dir: Directory for log files
            level: Logging level
            max_bytes: Max file size before rotation
            backup_count: Number of backup files to keep

        Returns:
            Configured logger
        """
        logger_name = f"jarvis.{component}"

        # Return existing logger if already configured
        if logger_name in self.loggers:
            return self.loggers[logger_name]

        # Create logger
        logger = logging.getLogger(logger_name)
        logger.setLevel(level)

        # Clear existing handlers
        logger.handlers.clear()

        # Create formatters
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        console_formatter = JARVISFormatter()

        # File handler with rotation
        log_file = log_dir / f"component_{component}.log"
        log_file.parent.mkdir(parents=True, exist_ok=True)

        file_handler = RotatingFileHandler(
            filename=str(log_file),
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(file_formatter)

        # Console handler (only for warnings and above)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.WARNING)
        console_handler.setFormatter(console_formatter)

        # Add duplicate filter
        global_filter = GlobalDuplicateFilter()
        file_handler.addFilter(global_filter)
        console_handler.addFilter(global_filter)

        # Add handlers to logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        # Store references
        self.loggers[logger_name] = logger
        self.handlers[logger_name] = [file_handler, console_handler]
        self.filters[logger_name] = global_filter

        return logger

    def get_logger(self, component: str) -> logging.Logger:
        """Get logger for a component"""
        logger_name = f"jarvis.{component}"
        return logging.getLogger(logger_name)

    def log_event(
        self,
        component: str,
        level: str,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        error_code: Optional[str] = None,
    ):
        """Log an event with structured data"""
        logger = self.get_logger(component)
        log_method = getattr(logger, level.lower(), logger.info)

        # Create log record with extra context
        extra = {}
        if context:
            extra["context"] = context
        if error_code:
            extra["error_code"] = error_code

        log_method(message, extra=extra)

    def shutdown(self):
        """Shutdown all loggers"""
        for logger in self.loggers.values():
            for handler in logger.handlers:
                handler.close()
        self.loggers.clear()
        self.handlers.clear()
        self.filters.clear()


# Global instance
jarvis_logger = JARVISLogger()


def get_component_logger(component: str) -> logging.Logger:
    """Convenience function to get a component logger"""
    return jarvis_logger.get_logger(component)


def apply_global_duplicate_filter(logger: logging.Logger):
    """Apply global duplicate filter to an existing logger"""
    global_filter = GlobalDuplicateFilter()

    # Remove existing duplicate filters
    for handler in logger.handlers:
        handler.filters[:] = [
            f
            for f in handler.filters
            if not isinstance(f, (DuplicateFilter, GlobalDuplicateFilter))
        ]
        # Add global filter
        handler.addFilter(global_filter)


def setup_jarvis_logging(log_dir: Path):
    """Setup complete JARVIS logging system"""
    # Setup component loggers
    components = [
        "core",
        "ai_agent",
        "vision_system",
        "audio_system",
        "memory_manager",
        "network_mesh",
        "evolution_engine",
        "system_monitor",
        "performance_optimizer",
        "watchdog",
    ]

    for component in components:
        jarvis_logger.setup_component_logger(component, log_dir)

    # Setup main JARVIS logger
    main_logger = jarvis_logger.setup_component_logger("main", log_dir)
    main_logger.info("🎯 JARVIS Unified Logging System initialized")

    return jarvis_logger


if __name__ == "__main__":
    # Test the logging system
    from pathlib import Path
    import tempfile

    with tempfile.TemporaryDirectory() as temp_dir:
        log_dir = Path(temp_dir) / "logs"

        # Setup logging
        logger_system = setup_jarvis_logging(log_dir)

        # Test logging
        ai_logger = get_component_logger("ai_agent")
        ai_logger.info("AI Agent initialized")
        ai_logger.warning(
            "Low confidence in response", extra={"context": {"confidence": 0.65}}
        )
        ai_logger.error("Failed to process request", extra={"error_code": "E001"})

        vision_logger = get_component_logger("vision_system")
        vision_logger.info("Vision system online")
        vision_logger.debug("Processing frame at 30 FPS")

        # Test duplicate prevention
        for i in range(5):
            ai_logger.warning("Test duplicate message")

        print("✅ JARVIS Logging System test completed")
