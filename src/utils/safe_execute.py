# -*- coding: utf-8 -*-
"""
Safe Execution Utilities for JARVIS 5.0
========================================

Provides decorators and context managers for standardized error handling
across the entire codebase. Eliminates scattered try/except blocks and
bare except clauses.

Usage:
    @safe_execute(default={}, log_error=True)
    def risky_operation():
        ...

    with safe_context("operation_name", default=None):
        ...
"""

import logging
import functools
import traceback
from typing import Any, Callable, Optional, TypeVar, Type
from contextlib import contextmanager

logger = logging.getLogger("JARVIS-SAFE-EXEC")

T = TypeVar("T")


def safe_execute(
    default: Any = None,
    log_error: bool = True,
    log_level: int = logging.ERROR,
    reraise: bool = False,
    exceptions: tuple = (Exception,),
    on_error: Optional[Callable] = None,
):
    """
    Decorator for safe function execution with standardized error handling.

    Args:
        default: Default return value on error
        log_error: Whether to log the error
        log_level: Logging level for errors (default: ERROR)
        reraise: Whether to re-raise the exception after handling
        exceptions: Tuple of exception types to catch
        on_error: Optional callback function called with (exception, func_name)

    Returns:
        Decorated function with safe error handling

    Examples:
        @safe_execute(default={}, log_error=True)
        def load_config():
            return json.load(open("config.json"))

        @safe_execute(default=False, on_error=lambda e, n: metrics.record_error(n))
        def process_data(data):
            return transform(data)
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except exceptions as e:
                if log_error:
                    # Get the class name if it's a method
                    func_name = func.__qualname__
                    logger.log(
                        log_level,
                        f"Error in {func_name}: {type(e).__name__}: {e}",
                    )
                    if log_level >= logging.DEBUG:
                        logger.debug(traceback.format_exc())

                if on_error:
                    try:
                        on_error(e, func.__qualname__)
                    except Exception:
                        pass

                if reraise:
                    raise

                return default

        return wrapper

    return decorator


def safe_execute_async(
    default: Any = None,
    log_error: bool = True,
    log_level: int = logging.ERROR,
    exceptions: tuple = (Exception,),
):
    """
    Async version of safe_execute decorator.

    Args:
        default: Default return value on error
        log_error: Whether to log the error
        log_level: Logging level for errors
        exceptions: Tuple of exception types to catch
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except exceptions as e:
                if log_error:
                    func_name = func.__qualname__
                    logger.log(
                        log_level,
                        f"Error in {func_name}: {type(e).__name__}: {e}",
                    )
                return default

        return wrapper

    return decorator


@contextmanager
def safe_context(
    operation_name: str,
    default: Any = None,
    log_error: bool = True,
    log_level: int = logging.ERROR,
    reraise: bool = False,
):
    """
    Context manager for safe execution blocks.

    Args:
        operation_name: Descriptive name for the operation
        default: Not used (context managers don't return), kept for API consistency
        log_error: Whether to log errors
        log_level: Logging level for errors
        reraise: Whether to re-raise exceptions

    Usage:
        with safe_context("loading models"):
            model = load_heavy_model()
    """
    try:
        yield
    except Exception as e:
        if log_error:
            logger.log(
                log_level,
                f"Error in '{operation_name}': {type(e).__name__}: {e}",
            )
        if reraise:
            raise


def safe_import(module_name: str, fallback: Any = None, log: bool = True) -> Any:
    """
    Safely import a module with fallback.

    Args:
        module_name: Full module path to import
        fallback: Value to return if import fails
        log: Whether to log import failures

    Returns:
        Imported module or fallback value

    Example:
        torch = safe_import("torch")
        if torch:
            device = torch.device("cuda")
    """
    try:
        import importlib

        return importlib.import_module(module_name)
    except ImportError as e:
        if log:
            logger.debug(f"Optional module '{module_name}' not available: {e}")
        return fallback
    except Exception as e:
        if log:
            logger.warning(f"Error importing '{module_name}': {e}")
        return fallback


class SafeInitializer:
    """
    Utility class for safely initializing multiple components.
    Tracks success/failure status for each component.

    Usage:
        init = SafeInitializer()

        with init.component("database"):
            self.db = DatabaseConnection()

        with init.component("cache"):
            self.cache = CacheLayer()

        print(init.summary())  # {'database': True, 'cache': False, ...}
    """

    def __init__(self):
        self._results: dict = {}

    @contextmanager
    def component(self, name: str):
        """Initialize a named component safely."""
        try:
            yield
            self._results[name] = True
        except Exception as e:
            self._results[name] = False
            logger.error(f"Failed to initialize component '{name}': {e}")

    @property
    def all_success(self) -> bool:
        """Check if all components initialized successfully."""
        return all(self._results.values())

    @property
    def summary(self) -> dict:
        """Get initialization summary."""
        return self._results.copy()

    def get_failed(self) -> list:
        """Get list of failed component names."""
        return [name for name, status in self._results.items() if not status]
