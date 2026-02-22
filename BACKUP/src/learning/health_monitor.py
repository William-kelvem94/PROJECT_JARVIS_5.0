# -*- coding: utf-8 -*-
"""
Health Monitor for JARVIS 5.0 Learning Systems
================================================

Monitors the health and performance of all learning subsystems.
Provides real-time health checks, automatic alerting, and recovery suggestions.

Extracted from the monolithic LearningEngine to follow Single Responsibility.
"""

import logging
import time
import threading
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field

logger = logging.getLogger("JARVIS-HEALTH-MONITOR")


@dataclass
class ComponentHealth:
    """Health status of a single component."""

    name: str
    healthy: bool = True
    last_check: float = 0.0
    last_error: Optional[str] = None
    consecutive_failures: int = 0
    uptime_seconds: float = 0.0
    metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HealthReport:
    """Aggregated health report for the entire learning system."""

    timestamp: float = 0.0
    overall_healthy: bool = True
    total_score: float = 1.0
    components: Dict[str, ComponentHealth] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    critical_issues: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary."""
        return {
            "timestamp": self.timestamp,
            "overall_healthy": self.overall_healthy,
            "total_score": self.total_score,
            "components": {
                name: {
                    "healthy": c.healthy,
                    "last_check": c.last_check,
                    "last_error": c.last_error,
                    "consecutive_failures": c.consecutive_failures,
                    "uptime_seconds": c.uptime_seconds,
                    "metrics": c.metrics,
                }
                for name, c in self.components.items()
            },
            "warnings": self.warnings,
            "critical_issues": self.critical_issues,
        }


class HealthMonitor:
    """
    Monitors health of all learning subsystems.

    Features:
    - Periodic health checks for each registered component
    - Automatic alerting when components fail
    - Recovery suggestions based on failure patterns
    - Health score calculation (0.0 - 1.0)
    """

    # Constants
    MAX_CONSECUTIVE_FAILURES = 5
    HEALTH_CHECK_INTERVAL = 60  # seconds

    def __init__(self, check_interval: float = 60.0):
        """
        Initialize the Health Monitor.

        Args:
            check_interval: Seconds between health check cycles
        """
        self.check_interval = check_interval
        self._components: Dict[str, ComponentHealth] = {}
        self._health_checks: Dict[str, callable] = {}
        self._lock = threading.Lock()
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._start_time = time.time()

        logger.info(
            f"HealthMonitor initialized (check_interval={check_interval}s)"
        )

    def register_component(
        self,
        name: str,
        health_check: Optional[callable] = None,
    ):
        """
        Register a component for health monitoring.

        Args:
            name: Component name (e.g., 'scalable_database')
            health_check: Optional callable that returns True if healthy.
                         If None, component is assumed healthy until marked otherwise.
        """
        with self._lock:
            self._components[name] = ComponentHealth(
                name=name,
                healthy=True,
                last_check=time.time(),
            )
            if health_check:
                self._health_checks[name] = health_check

        logger.debug(f"Registered component for monitoring: {name}")

    def mark_healthy(self, name: str, metrics: Optional[Dict[str, Any]] = None):
        """Mark a component as healthy."""
        with self._lock:
            comp = self._components.get(name)
            if comp:
                comp.healthy = True
                comp.last_check = time.time()
                comp.consecutive_failures = 0
                comp.last_error = None
                if metrics:
                    comp.metrics.update(metrics)

    def mark_unhealthy(self, name: str, error: str):
        """Mark a component as unhealthy."""
        with self._lock:
            comp = self._components.get(name)
            if comp:
                comp.healthy = False
                comp.last_check = time.time()
                comp.last_error = error
                comp.consecutive_failures += 1

                if comp.consecutive_failures >= self.MAX_CONSECUTIVE_FAILURES:
                    logger.critical(
                        f"Component '{name}' has failed {comp.consecutive_failures} "
                        f"consecutive times: {error}"
                    )
                else:
                    logger.warning(f"Component '{name}' unhealthy: {error}")

    def run_health_check(self) -> HealthReport:
        """
        Run health checks on all registered components.

        Returns:
            HealthReport with aggregated health status
        """
        report = HealthReport(timestamp=time.time())

        with self._lock:
            components_copy = dict(self._components)

        for name, comp in components_copy.items():
            # Run health check if available
            check_fn = self._health_checks.get(name)
            if check_fn:
                try:
                    is_healthy = check_fn()
                    if is_healthy:
                        self.mark_healthy(name)
                    else:
                        self.mark_unhealthy(name, "Health check returned False")
                except Exception as e:
                    self.mark_unhealthy(name, str(e))

            # Update uptime
            comp.uptime_seconds = time.time() - self._start_time

        # Build report
        with self._lock:
            report.components = dict(self._components)

            healthy_count = sum(
                1 for c in self._components.values() if c.healthy
            )
            total_count = len(self._components) or 1

            report.total_score = healthy_count / total_count
            report.overall_healthy = report.total_score >= 0.8

            # Generate warnings
            for name, comp in self._components.items():
                if not comp.healthy:
                    if comp.consecutive_failures >= self.MAX_CONSECUTIVE_FAILURES:
                        report.critical_issues.append(
                            f"CRITICAL: '{name}' has failed "
                            f"{comp.consecutive_failures} times: {comp.last_error}"
                        )
                    else:
                        report.warnings.append(
                            f"WARNING: '{name}' is unhealthy: {comp.last_error}"
                        )

        return report

    def get_component_status(self, name: str) -> Optional[Dict[str, Any]]:
        """Get detailed status of a specific component."""
        with self._lock:
            comp = self._components.get(name)
            if not comp:
                return None

            return {
                "name": comp.name,
                "healthy": comp.healthy,
                "last_check": comp.last_check,
                "last_error": comp.last_error,
                "consecutive_failures": comp.consecutive_failures,
                "uptime_seconds": comp.uptime_seconds,
                "metrics": comp.metrics,
            }

    def get_recovery_suggestions(self) -> List[str]:
        """
        Generate recovery suggestions based on current health status.

        Returns:
            List of actionable recovery suggestions
        """
        suggestions = []

        with self._lock:
            for name, comp in self._components.items():
                if not comp.healthy:
                    error = comp.last_error or ""
                    error_lower = error.lower()

                    if "memory" in error_lower or "oom" in error_lower:
                        suggestions.append(
                            f"[{name}] Memory issue detected. Consider reducing "
                            f"batch sizes or enabling gradient checkpointing."
                        )
                    elif "connection" in error_lower or "timeout" in error_lower:
                        suggestions.append(
                            f"[{name}] Connection issue. Verify network "
                            f"and service availability."
                        )
                    elif "import" in error_lower or "module" in error_lower:
                        suggestions.append(
                            f"[{name}] Missing dependency. Run "
                            f"'pip install -r requirements.txt'."
                        )
                    elif "permission" in error_lower or "access" in error_lower:
                        suggestions.append(
                            f"[{name}] Permission issue. Check file "
                            f"and directory permissions."
                        )
                    else:
                        suggestions.append(
                            f"[{name}] Component failed with: {error}. "
                            f"Check logs for details."
                        )

        return suggestions

    def start(self):
        """Start background health monitoring."""
        if self._running:
            return

        self._running = True
        self._thread = threading.Thread(
            target=self._monitor_loop,
            daemon=True,
            name="HealthMonitorLoop",
        )
        self._thread.start()
        logger.info("Health monitor background loop started")

    def stop(self):
        """Stop background health monitoring."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        logger.info("Health monitor stopped")

    def _monitor_loop(self):
        """Background monitoring loop."""
        while self._running:
            try:
                report = self.run_health_check()

                if not report.overall_healthy:
                    logger.warning(
                        f"System health degraded: "
                        f"score={report.total_score:.0%}, "
                        f"issues={len(report.critical_issues) + len(report.warnings)}"
                    )

                    for issue in report.critical_issues:
                        logger.critical(issue)

            except Exception as e:
                logger.error(f"Error in health monitor loop: {e}")

            time.sleep(self.check_interval)

    def monitor_system(self) -> Dict[str, Any]:
        """
        Run a full system health check and return summary.

        This is the original interface method, kept for backwards compatibility.

        Returns:
            Dictionary with health check results
        """
        report = self.run_health_check()
        return report.to_dict()
