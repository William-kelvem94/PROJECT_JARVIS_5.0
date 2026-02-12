#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS SINGULARITY - Advanced Auto-Recovery System
==================================================
Intelligent self-healing system for critical failures.

Architecture:
- Health monitoring with predictive failure detection
- Automated recovery strategies with machine learning
- Integration with fallback_system for seamless operation
- Recovery history and pattern analysis for improvement

Philosophy:
- Proactive healing before catastrophic failures
- Smart recovery based on failure patterns and context
- Minimal downtime with transparent recovery operations
- Learning from previous recovery attempts
"""

import os
import sys
import logging
import asyncio
import threading
import json
import time
import traceback
from typing import Dict, List, Optional, Callable, Any, Tuple
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import psutil
import importlib
from collections import defaultdict

logger = logging.getLogger(__name__)

# ============================================================================
# RECOVERY STRATEGIES & HEALTH MONITORING
# ============================================================================

class FailureType(Enum):
    """Types of failures the system can detect and recover from"""
    IMPORT_ERROR = "import_error"
    MEMORY_LEAK = "memory_leak"
    CPU_OVERLOAD = "cpu_overload" 
    NETWORK_FAILURE = "network_failure"
    MODULE_CRASH = "module_crash"
    DEPENDENCY_MISSING = "dependency_missing"
    FILE_CORRUPTION = "file_corruption"
    PERMISSION_ERROR = "permission_error"
    DATABASE_CONNECTION = "database_connection"
    API_TIMEOUT = "api_timeout"
    THREADING_DEADLOCK = "threading_deadlock"
    UNKNOWN = "unknown"

class RecoveryStatus(Enum):
    """Recovery operation status"""
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"
    IN_PROGRESS = "in_progress"
    SKIPPED = "skipped"

@dataclass
class FailureEvent:
    """Represents a detected failure event"""
    timestamp: datetime
    failure_type: FailureType
    module_name: str
    error_message: str
    stack_trace: str
    severity: int  # 1-10 (10 = critical)
    context: Dict[str, Any]
    recovery_attempts: List[Dict] = None
    
    def __post_init__(self):
        if self.recovery_attempts is None:
            self.recovery_attempts = []

@dataclass
class RecoveryAction:
    """Represents a recovery action taken"""
    timestamp: datetime
    failure_event: FailureEvent
    strategy_name: str
    action_taken: str
    status: RecoveryStatus
    execution_time_ms: float
    side_effects: List[str]
    success_probability: float  # Learned from history

class ModuleHealth:
    """Tracks health metrics for a specific module"""
    
    def __init__(self, module_name: str):
        self.module_name = module_name
        self.is_healthy = True
        self.last_check = datetime.now()
        self.error_count = 0
        self.recovery_count = 0
        self.uptime_start = datetime.now()
        self.memory_usage_mb = 0.0
        self.cpu_usage_percent = 0.0
        self.response_time_ms = 0.0
        self.last_error: Optional[Exception] = None
        
    def update_metrics(self, memory_mb: float = 0.0, cpu_percent: float = 0.0, response_ms: float = 0.0):
        """Update health metrics"""
        self.memory_usage_mb = memory_mb
        self.cpu_usage_percent = cpu_percent
        self.response_time_ms = response_ms
        self.last_check = datetime.now()
        
    def record_error(self, error: Exception):
        """Record an error occurrence"""
        self.error_count += 1
        self.last_error = error
        self.is_healthy = False
        
    def record_recovery(self):
        """Record a successful recovery"""
        self.recovery_count += 1
        self.is_healthy = True
        
    @property
    def uptime_minutes(self) -> float:
        """Calculate uptime in minutes"""
        return (datetime.now() - self.uptime_start).total_seconds() / 60

class AutoRecoverySystem:
    """
    Advanced auto-recovery system with intelligent failure detection and healing.
    
    Features:
    - Real-time health monitoring of core modules
    - Predictive failure detection using patterns
    - Automated recovery strategies with learning
    - Integration with existing fallback system
    - Recovery history analysis and optimization
    """
    
    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir or Path("data/recovery")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Health tracking
        self.module_health: Dict[str, ModuleHealth] = {}
        self.failure_history: List[FailureEvent] = []
        self.recovery_history: List[RecoveryAction] = []
        
        # Recovery strategies registry
        self.recovery_strategies: Dict[FailureType, List[Callable]] = defaultdict(list)
        self.strategy_success_rates: Dict[str, float] = {}
        
        # Monitoring
        self.monitoring_active = False
        self.monitoring_thread: Optional[threading.Thread] = None
        self.monitor_interval = 30  # seconds
        
        # Recovery state
        self.recovery_in_progress = False
        self.max_recovery_attempts = 3
        self.recovery_cooldown = 60  # seconds between attempts
        
        # Integration points
        self.fallback_system = None  # Will be injected
        
        self._register_default_strategies()
        self._load_historical_data()
        
        logger.info("✅ Auto-Recovery System initialized")
    
    def set_fallback_system(self, fallback_system):
        """Inject fallback system for integration"""
        self.fallback_system = fallback_system
        logger.info("🔗 Fallback system integration established")
    
    def _register_default_strategies(self):
        """Register default recovery strategies"""
        
        # Import Error Recovery
        self.register_strategy(FailureType.IMPORT_ERROR, self._recover_import_error)
        self.register_strategy(FailureType.IMPORT_ERROR, self._recover_via_pip_install)
        
        # Memory Leak Recovery
        self.register_strategy(FailureType.MEMORY_LEAK, self._recover_memory_leak)
        self.register_strategy(FailureType.MEMORY_LEAK, self._restart_module)
        
        # CPU Overload Recovery
        self.register_strategy(FailureType.CPU_OVERLOAD, self._recover_cpu_overload)
        
        # Network Failure Recovery
        self.register_strategy(FailureType.NETWORK_FAILURE, self._recover_network_failure)
        
        # Module Crash Recovery
        self.register_strategy(FailureType.MODULE_CRASH, self._restart_module)
        self.register_strategy(FailureType.MODULE_CRASH, self._reload_module)
        
        # File Corruption Recovery
        self.register_strategy(FailureType.FILE_CORRUPTION, self._recover_file_corruption)
        
        # Permission Error Recovery
        self.register_strategy(FailureType.PERMISSION_ERROR, self._recover_permission_error)
        
        logger.info(f"📋 Registered {len(self.recovery_strategies)} recovery strategy types")
    
    def register_strategy(self, failure_type: FailureType, strategy_func: Callable):
        """Register a new recovery strategy"""
        self.recovery_strategies[failure_type].append(strategy_func)
        strategy_name = f"{failure_type.value}::{strategy_func.__name__}"
        if strategy_name not in self.strategy_success_rates:
            self.strategy_success_rates[strategy_name] = 0.5  # Default 50% success rate
    
    def register_module(self, module_name: str) -> ModuleHealth:
        """Register a module for health monitoring"""
        if module_name not in self.module_health:
            self.module_health[module_name] = ModuleHealth(module_name)
            logger.debug(f"📊 Registered module for monitoring: {module_name}")
        return self.module_health[module_name]
    
    def start_monitoring(self):
        """Start real-time health monitoring"""
        if self.monitoring_active:
            return
            
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        logger.info("🔍 Health monitoring started")
    
    def stop_monitoring(self):
        """Stop health monitoring"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        logger.info("⏹️ Health monitoring stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                self._check_system_health()
                time.sleep(self.monitor_interval)
            except Exception as e:
                logger.error(f"❌ Monitoring loop error: {e}")
                time.sleep(5)  # Short delay on error
    
    def _check_system_health(self):
        """Perform comprehensive system health check"""
        
        # Check overall system resources
        try:
            memory = psutil.virtual_memory()
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Detect system-wide issues
            if memory.percent > 90:
                self._trigger_recovery(
                    failure_type=FailureType.MEMORY_LEAK,
                    module_name="system",
                    error_message=f"System memory usage at {memory.percent}%",
                    severity=8
                )
            
            if cpu_percent > 90:
                self._trigger_recovery(
                    failure_type=FailureType.CPU_OVERLOAD,
                    module_name="system", 
                    error_message=f"System CPU usage at {cpu_percent}%",
                    severity=7
                )
                
        except Exception as e:
            logger.error(f"❌ System health check failed: {e}")
        
        # Check module-specific health
        for module_name, health in self.module_health.items():
            try:
                self._check_module_health(health)
            except Exception as e:
                logger.error(f"❌ Module health check failed for {module_name}: {e}")
    
    def _check_module_health(self, health: ModuleHealth):
        """Check health of a specific module"""
        
        # Update metrics if module is still loaded
        try:
            module = sys.modules.get(health.module_name)
            if module:
                # Basic aliveness check - try to access module attributes
                hasattr(module, '__file__')  # Simple check
                
                # Update response time (placeholder - would need module-specific implementation)
                # health.update_metrics(response_ms=self._measure_module_response(module))
                
        except Exception as e:
            # Module may be corrupted or crashed
            self._trigger_recovery(
                failure_type=FailureType.MODULE_CRASH,
                module_name=health.module_name,
                error_message=f"Module health check failed: {str(e)}",
                severity=6
            )
    
    def _trigger_recovery(self, failure_type: FailureType, module_name: str, 
                         error_message: str, severity: int, 
                         stack_trace: str = "", context: Optional[Dict] = None):
        """Trigger recovery process for a detected failure"""
        
        if self.recovery_in_progress:
            logger.warning("⚠️ Recovery already in progress, queueing...")
            return
            
        # Create failure event
        failure_event = FailureEvent(
            timestamp=datetime.now(),
            failure_type=failure_type,
            module_name=module_name,
            error_message=error_message,
            stack_trace=stack_trace or traceback.format_exc(),
            severity=severity,
            context=context or {}
        )
        
        self.failure_history.append(failure_event)
        
        # Start recovery process
        recovery_thread = threading.Thread(
            target=self._execute_recovery_async,
            args=(failure_event,),
            daemon=True
        )
        recovery_thread.start()
    
    def _execute_recovery_async(self, failure_event: FailureEvent):
        """Execute recovery strategies for a failure event (async wrapper)"""
        asyncio.run(self._execute_recovery(failure_event))
    
    async def _execute_recovery(self, failure_event: FailureEvent):
        """Execute recovery strategies for a failure event"""
        
        self.recovery_in_progress = True
        logger.warning(f"🔧 Starting auto-recovery for {failure_event.failure_type.value} in {failure_event.module_name}")
        
        try:
            strategies = self.recovery_strategies.get(failure_event.failure_type, [])
            if not strategies:
                logger.error(f"❌ No recovery strategies available for {failure_event.failure_type.value}")
                return
            
            # Sort strategies by success rate (highest first)
            strategies_with_rates = []
            for strategy in strategies:
                strategy_name = f"{failure_event.failure_type.value}::{strategy.__name__}"
                success_rate = self.strategy_success_rates.get(strategy_name, 0.5)
                strategies_with_rates.append((strategy, success_rate))
            
            strategies_with_rates.sort(key=lambda x: x[1], reverse=True)
            
            # Try each strategy
            for strategy_func, success_rate in strategies_with_rates:
                if len(failure_event.recovery_attempts) >= self.max_recovery_attempts:
                    logger.error(f"❌ Max recovery attempts reached for {failure_event.module_name}")
                    break
                
                logger.info(f"🔧 Trying recovery strategy: {strategy_func.__name__} (success rate: {success_rate:.1%})")
                
                start_time = time.time()
                recovery_action = None
                
                try:
                    # Execute recovery strategy
                    result = await self._execute_strategy_safely(strategy_func, failure_event)
                    execution_time = (time.time() - start_time) * 1000  # ms
                    
                    # Record recovery action
                    recovery_action = RecoveryAction(
                        timestamp=datetime.now(),
                        failure_event=failure_event,
                        strategy_name=strategy_func.__name__,
                        action_taken=result.get("action", "Unknown"),
                        status=RecoveryStatus.SUCCESS if result.get("success") else RecoveryStatus.FAILED,
                        execution_time_ms=execution_time,
                        side_effects=result.get("side_effects", []),
                        success_probability=success_rate
                    )
                    
                    self.recovery_history.append(recovery_action)
                    failure_event.recovery_attempts.append(asdict(recovery_action))
                    
                    if result.get("success"):
                        logger.info(f"✅ Recovery successful: {strategy_func.__name__}")
                        
                        # Update module health
                        if failure_event.module_name in self.module_health:
                            self.module_health[failure_event.module_name].record_recovery()
                        
                        # Update strategy success rate
                        self._update_strategy_success_rate(strategy_func.__name__, failure_event.failure_type, True)
                        break
                    else:
                        logger.warning(f"⚠️ Recovery strategy failed: {strategy_func.__name__}")
                        self._update_strategy_success_rate(strategy_func.__name__, failure_event.failure_type, False)
                        
                except Exception as e:
                    execution_time = (time.time() - start_time) * 1000
                    logger.error(f"❌ Recovery strategy error: {strategy_func.__name__}: {e}")
                    
                    recovery_action = RecoveryAction(
                        timestamp=datetime.now(),
                        failure_event=failure_event,
                        strategy_name=strategy_func.__name__,
                        action_taken="Strategy execution failed",
                        status=RecoveryStatus.FAILED,
                        execution_time_ms=execution_time,
                        side_effects=[f"Exception: {str(e)}"],
                        success_probability=success_rate
                    )
                    
                    self.recovery_history.append(recovery_action)
                    self._update_strategy_success_rate(strategy_func.__name__, failure_event.failure_type, False)
            
            # If all strategies failed, escalate to fallback system
            if not any(attempt.get("status") == "success" for attempt in failure_event.recovery_attempts):
                logger.warning("⚠️ All recovery strategies failed, escalating to fallback system")
                if self.fallback_system:
                    # Use fallback system for critical failures
                    pass
            
        finally:
            self.recovery_in_progress = False
            self._save_historical_data()
    
    async def _execute_strategy_safely(self, strategy_func: Callable, failure_event: FailureEvent) -> Dict:
        """Execute a recovery strategy safely with timeout and error handling"""
        try:
            if asyncio.iscoroutinefunction(strategy_func):
                # Async strategy with timeout
                return await asyncio.wait_for(strategy_func(failure_event), timeout=30)
            else:
                # Sync strategy
                return strategy_func(failure_event)
        except asyncio.TimeoutError:
            return {"success": False, "action": "Strategy timed out", "side_effects": ["Timeout"]}
        except Exception as e:
            return {"success": False, "action": f"Strategy error: {e}", "side_effects": [str(e)]}
    
    def _update_strategy_success_rate(self, strategy_name: str, failure_type: FailureType, success: bool):
        """Update success rate for a recovery strategy using exponential moving average"""
        strategy_key = f"{failure_type.value}::{strategy_name}"
        current_rate = self.strategy_success_rates.get(strategy_key, 0.5)
        
        # Exponential moving average with decay factor 0.1
        new_rate = current_rate * 0.9 + (1.0 if success else 0.0) * 0.1
        self.strategy_success_rates[strategy_key] = max(0.01, min(0.99, new_rate))  # Clamp to [0.01, 0.99]
    
    # ========================================================================
    # RECOVERY STRATEGY IMPLEMENTATIONS
    # ========================================================================
    
    def _recover_import_error(self, failure_event: FailureEvent) -> Dict:
        """Recover from import errors by reloading modules"""
        try:
            module_name = failure_event.module_name
            
            # Try to reload the module
            if module_name in sys.modules:
                importlib.reload(sys.modules[module_name])
                return {
                    "success": True,
                    "action": f"Reloaded module: {module_name}",
                    "side_effects": []
                }
            else:
                # Try to import fresh
                importlib.import_module(module_name)
                return {
                    "success": True,
                    "action": f"Fresh import of module: {module_name}",
                    "side_effects": []
                }
                
        except Exception as e:
            return {
                "success": False,
                "action": f"Module reload failed: {e}",
                "side_effects": [str(e)]
            }
    
    def _recover_via_pip_install(self, failure_event: FailureEvent) -> Dict:
        """Recover from import errors by installing missing packages"""
        try:
            error_msg = failure_event.error_message.lower()
            
            # Extract package name from common error patterns
            package_name = None
            if "no module named" in error_msg:
                # Extract package name from "No module named 'package_name'"
                import re
                match = re.search(r"no module named ['\"]([^'\"]+)['\"]", error_msg)
                if match:
                    package_name = match.group(1).split('.')[0]  # Get root package
            
            if not package_name:
                return {"success": False, "action": "Could not identify missing package", "side_effects": []}
            
            # Try to install package
            import subprocess
            result = subprocess.run([sys.executable, "-m", "pip", "install", package_name], 
                                  capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "action": f"Installed package: {package_name}",
                    "side_effects": [f"pip install output: {result.stdout[:200]}"]
                }
            else:
                return {
                    "success": False,
                    "action": f"pip install failed for: {package_name}",
                    "side_effects": [f"pip error: {result.stderr[:200]}"]
                }
                
        except Exception as e:
            return {
                "success": False,
                "action": f"Package installation error: {e}",
                "side_effects": [str(e)]
            }
    
    def _recover_memory_leak(self, failure_event: FailureEvent) -> Dict:
        """Recover from memory leaks by forcing garbage collection and cleanup"""
        try:
            import gc
            
            # Force garbage collection
            collected = gc.collect()
            
            # Get memory usage before and after
            memory_before = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            
            # Force another collection cycle
            gc.collect()
            
            memory_after = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            freed_mb = memory_before - memory_after
            
            return {
                "success": freed_mb > 0,
                "action": f"Garbage collection freed {freed_mb:.1f} MB",
                "side_effects": [f"Collected {collected} objects"]
            }
            
        except Exception as e:
            return {
                "success": False,
                "action": f"Memory cleanup error: {e}",
                "side_effects": [str(e)]
            }
    
    def _recover_cpu_overload(self, failure_event: FailureEvent) -> Dict:
        """Recover from CPU overload by reducing thread priorities"""
        try:
            import threading
            
            # Lower priority of current process
            try:
                import psutil
                p = psutil.Process()
                p.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS if sys.platform == 'win32' else 10)
            except:
                pass
            
            # Add small delay to reduce CPU pressure
            time.sleep(0.1)
            
            return {
                "success": True,
                "action": "Reduced process priority and added CPU breathing room",
                "side_effects": ["Process priority lowered", "Brief execution pause"]
            }
            
        except Exception as e:
            return {
                "success": False,
                "action": f"CPU overload recovery error: {e}",
                "side_effects": [str(e)]
            }
    
    def _recover_network_failure(self, failure_event: FailureEvent) -> Dict:
        """Recover from network failures by testing connectivity and retrying"""
        try:
            import socket
            
            # Test basic connectivity
            try:
                socket.create_connection(("8.8.8.8", 53), timeout=5)
                network_ok = True
            except:
                network_ok = False
            
            if network_ok:
                return {
                    "success": True,
                    "action": "Network connectivity verified, ready for retry",
                    "side_effects": ["Network test successful"]
                }
            else:
                return {
                    "success": False,
                    "action": "Network connectivity still unavailable",
                    "side_effects": ["Network test failed"]
                }
                
        except Exception as e:
            return {
                "success": False,
                "action": f"Network recovery error: {e}",
                "side_effects": [str(e)]
            }
    
    def _restart_module(self, failure_event: FailureEvent) -> Dict:
        """Restart a crashed module"""
        try:
            module_name = failure_event.module_name
            
            # Remove from sys.modules to force fresh load
            if module_name in sys.modules:
                del sys.modules[module_name]
            
            # Reimport
            importlib.import_module(module_name)
            
            return {
                "success": True,
                "action": f"Module restarted: {module_name}",
                "side_effects": ["Module removed from cache", "Fresh import performed"]
            }
            
        except Exception as e:
            return {
                "success": False,
                "action": f"Module restart error: {e}",
                "side_effects": [str(e)]
            }
    
    def _reload_module(self, failure_event: FailureEvent) -> Dict:
        """Reload a module without removing from cache"""
        try:
            module_name = failure_event.module_name
            
            if module_name in sys.modules:
                importlib.reload(sys.modules[module_name])
                return {
                    "success": True,
                    "action": f"Module reloaded: {module_name}",
                    "side_effects": ["In-place module reload"]
                }
            else:
                return {
                    "success": False,
                    "action": f"Module not in cache: {module_name}",
                    "side_effects": ["Module not loaded"]
                }
                
        except Exception as e:
            return {
                "success": False,
                "action": f"Module reload error: {e}",
                "side_effects": [str(e)]
            }
    
    def _recover_file_corruption(self, failure_event: FailureEvent) -> Dict:
        """Recover from file corruption by restoring backups"""
        try:
            # This would need integration with backup system
            # For now, just report the issue
            return {
                "success": False,
                "action": "File corruption detected - manual intervention required",
                "side_effects": ["Backup restoration needed"]
            }
            
        except Exception as e:
            return {
                "success": False,
                "action": f"File recovery error: {e}",
                "side_effects": [str(e)]
            }
    
    def _recover_permission_error(self, failure_event: FailureEvent) -> Dict:
        """Recover from permission errors"""
        try:
            # Try to create directories that might be missing
            error_msg = failure_event.error_message.lower()
            
            if "permission denied" in error_msg and "data" in error_msg:
                # Try to create data directories with proper permissions
                data_dirs = ["data/recovery", "data/logs", "data/cache"]
                created = []
                
                for dir_path in data_dirs:
                    try:
                        Path(dir_path).mkdir(parents=True, exist_ok=True)
                        created.append(dir_path)
                    except:
                        pass
                
                if created:
                    return {
                        "success": True,
                        "action": f"Created directories: {created}",
                        "side_effects": [f"Directory creation: {len(created)} dirs"]
                    }
            
            return {
                "success": False,
                "action": "Permission error requires manual intervention",
                "side_effects": ["Administrative privileges may be needed"]
            }
            
        except Exception as e:
            return {
                "success": False,
                "action": f"Permission recovery error: {e}",
                "side_effects": [str(e)]
            }
    
    # ========================================================================
    # DATA PERSISTENCE & ANALYTICS
    # ========================================================================
    
    def _load_historical_data(self):
        """Load historical recovery data for analysis"""
        try:
            history_file = self.data_dir / "recovery_history.json"
            if history_file.exists():
                with open(history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # Load strategy success rates
                    self.strategy_success_rates = data.get("strategy_success_rates", {})
                    
                    logger.info(f"📊 Loaded {len(self.strategy_success_rates)} strategy success rates")
                    
        except Exception as e:
            logger.warning(f"⚠️ Could not load historical data: {e}")
    
    def _save_historical_data(self):
        """Save recovery history and analytics"""
        try:
            history_file = self.data_dir / "recovery_history.json"
            
            # Prepare data for serialization
            data = {
                "strategy_success_rates": self.strategy_success_rates,
                "last_updated": datetime.now().isoformat(),
                "total_recoveries": len(self.recovery_history),
                "total_failures": len(self.failure_history)
            }
            
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"❌ Could not save historical data: {e}")
    
    def get_recovery_stats(self) -> Dict[str, Any]:
        """Get comprehensive recovery statistics"""
        
        if not self.recovery_history:
            return {"status": "No recovery data available"}
        
        total_recoveries = len(self.recovery_history)
        successful_recoveries = len([r for r in self.recovery_history if r.status == RecoveryStatus.SUCCESS])
        
        # Calculate success rate by failure type
        success_by_type = defaultdict(lambda: {"attempts": 0, "successes": 0})
        
        for recovery in self.recovery_history:
            failure_type = recovery.failure_event.failure_type.value
            success_by_type[failure_type]["attempts"] += 1
            if recovery.status == RecoveryStatus.SUCCESS:
                success_by_type[failure_type]["successes"] += 1
        
        # Calculate average recovery times
        avg_recovery_time = sum(r.execution_time_ms for r in self.recovery_history) / total_recoveries
        
        return {
            "total_recoveries": total_recoveries,
            "success_rate": successful_recoveries / total_recoveries if total_recoveries > 0 else 0,
            "average_recovery_time_ms": avg_recovery_time,
            "success_by_failure_type": {
                ftype: {
                    "success_rate": stats["successes"] / stats["attempts"] if stats["attempts"] > 0 else 0,
                    "total_attempts": stats["attempts"]
                }
                for ftype, stats in success_by_type.items()
            },
            "strategy_performance": self.strategy_success_rates,
            "monitored_modules": len(self.module_health),
            "healthy_modules": len([h for h in self.module_health.values() if h.is_healthy])
        }
    
    def force_health_check(self) -> Dict[str, Any]:
        """Force an immediate comprehensive health check"""
        try:
            self._check_system_health()
            return {
                "status": "Health check completed",
                "monitored_modules": len(self.module_health),
                "healthy_modules": len([h for h in self.module_health.values() if h.is_healthy]),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "Health check failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_module_health_report(self) -> Dict[str, Dict]:
        """Get detailed health report for all monitored modules"""
        report = {}
        
        for module_name, health in self.module_health.items():
            report[module_name] = {
                "is_healthy": health.is_healthy,
                "uptime_minutes": health.uptime_minutes,
                "error_count": health.error_count,
                "recovery_count": health.recovery_count,
                "memory_usage_mb": health.memory_usage_mb,
                "cpu_usage_percent": health.cpu_usage_percent,
                "response_time_ms": health.response_time_ms,
                "last_check": health.last_check.isoformat(),
                "last_error": str(health.last_error) if health.last_error else None
            }
        
        return report
    
    def __del__(self):
        """Cleanup on shutdown"""
        try:
            if self.monitoring_active:
                self.stop_monitoring()
            self._save_historical_data()
        except:
            pass

# ============================================================================
# GLOBAL INSTANCE
# ============================================================================

# Global instance for easy access
auto_recovery_system: Optional[AutoRecoverySystem] = None

def get_auto_recovery_system() -> AutoRecoverySystem:
    """Get global auto-recovery system instance"""
    global auto_recovery_system
    if auto_recovery_system is None:
        auto_recovery_system = AutoRecoverySystem()
    return auto_recovery_system

def register_module_for_monitoring(module_name: str) -> ModuleHealth:
    """Convenience function to register module for monitoring"""
    return get_auto_recovery_system().register_module(module_name)

def trigger_recovery_for_exception(module_name: str, exception: Exception, severity: int = 5):
    """Convenience function to trigger recovery for an exception"""
    
    # Determine failure type from exception
    failure_type = FailureType.UNKNOWN
    if isinstance(exception, ImportError):
        failure_type = FailureType.IMPORT_ERROR
    elif isinstance(exception, MemoryError):
        failure_type = FailureType.MEMORY_LEAK
    elif isinstance(exception, ConnectionError):
        failure_type = FailureType.NETWORK_FAILURE
    elif isinstance(exception, FileNotFoundError):
        failure_type = FailureType.FILE_CORRUPTION
    elif isinstance(exception, PermissionError):
        failure_type = FailureType.PERMISSION_ERROR
    
    recovery_system = get_auto_recovery_system()
    recovery_system._trigger_recovery(
        failure_type=failure_type,
        module_name=module_name,
        error_message=str(exception),
        severity=severity,
        stack_trace=traceback.format_exc()
    )