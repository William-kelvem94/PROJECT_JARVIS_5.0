"""
Real-time Metrics Dashboard for JARVIS Learning Systems.

Provides comprehensive monitoring and visualization of training progress,
system health, and performance metrics across distributed training jobs.
"""

import os
import json
import time
import asyncio
import logging
import threading
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field, asdict
from collections import defaultdict, deque
from .dependency_manager import dependency_manager

logger = logging.getLogger(__name__)

@dataclass
class MetricPoint:
    """Single metric data point."""
    timestamp: float
    value: float
    job_id: Optional[str] = None
    gpu_id: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SystemMetrics:
    """System-wide performance metrics."""
    cpu_usage_percent: float
    memory_usage_percent: float
    disk_usage_percent: float
    gpu_metrics: Dict[int, Dict[str, float]]
    active_jobs: int
    timestamp: float

@dataclass
class TrainingMetrics:
    """Training-specific metrics."""
    job_id: str
    epoch: int
    step: int
    loss: float
    learning_rate: float
    throughput_samples_per_sec: float
    gpu_utilization: Dict[int, float]
    memory_usage: Dict[int, float]
    timestamp: float

class MetricsCollector:
    """Collects metrics from various sources."""
    
    def __init__(self, collection_interval: float = 1.0):
        self.collection_interval = collection_interval
        self.running = False
        self.metrics_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self._thread = None
        self._lock = threading.Lock()
        
        # Initialize collectors
        self._init_system_collectors()
    
    def _init_system_collectors(self):
        """Initialize system metric collectors."""
        self.system_collectors = {}
        
        # CPU and Memory
        if dependency_manager.is_available('psutil'):
            import psutil
            self.system_collectors['psutil'] = psutil
        
        # GPU metrics
        if dependency_manager.is_available('torch', 'gpu'):
            import torch
            self.system_collectors['torch'] = torch
    
    def start(self):
        """Start metrics collection."""
        if self.running:
            return
        
        self.running = True
        self._thread = threading.Thread(target=self._collection_loop, daemon=True)
        self._thread.start()
        logger.info("Started metrics collection")
    
    def stop(self):
        """Stop metrics collection."""
        self.running = False
        if self._thread:
            self._thread.join(timeout=5)
        logger.info("Stopped metrics collection")
    
    def _collection_loop(self):
        """Main collection loop."""
        while self.running:
            try:
                # Collect system metrics
                system_metrics = self._collect_system_metrics()
                if system_metrics:
                    self._add_metric('system', system_metrics)
                
                # Sleep for collection interval
                time.sleep(self.collection_interval)
                
            except Exception as e:
                logger.error(f"Error in metrics collection: {e}")
                time.sleep(1)  # Brief pause on error
    
    def _collect_system_metrics(self) -> Optional[SystemMetrics]:
        """Collect system-wide metrics."""
        try:
            timestamp = time.time()
            
            # CPU and Memory
            cpu_usage = 0.0
            memory_usage = 0.0
            disk_usage = 0.0
            
            if 'psutil' in self.system_collectors:
                psutil = self.system_collectors['psutil']
                cpu_usage = psutil.cpu_percent(interval=None)
                memory_info = psutil.virtual_memory()
                memory_usage = memory_info.percent
                disk_info = psutil.disk_usage('/')
                disk_usage = (disk_info.used / disk_info.total) * 100
            
            # GPU metrics
            gpu_metrics = {}
            if 'torch' in self.system_collectors:
                torch = self.system_collectors['torch']
                for gpu_id in range(torch.cuda.device_count()):
                    try:
                        torch.cuda.set_device(gpu_id)
                        
                        memory_reserved = torch.cuda.memory_reserved(gpu_id)
                        memory_allocated = torch.cuda.memory_allocated(gpu_id)
                        memory_total = torch.cuda.get_device_properties(gpu_id).total_memory
                        
                        gpu_metrics[gpu_id] = {
                            'memory_used_percent': (memory_allocated / memory_total) * 100,
                            'memory_reserved_percent': (memory_reserved / memory_total) * 100,
                            'memory_allocated_gb': memory_allocated / (1024**3),
                            'memory_total_gb': memory_total / (1024**3)
                        }
                        
                        # GPU utilization (if nvidia-ml-py available)
                        if dependency_manager.is_available('pynvml'):
                            try:
                                import pynvml  # type: ignore
                                handle = pynvml.nvmlDeviceGetHandleByIndex(gpu_id)
                                util = pynvml.nvmlDeviceGetUtilizationRates(handle)
                                gpu_metrics[gpu_id]['utilization_percent'] = util.gpu
                            except Exception:
                                pass
                            
                    except Exception as e:
                        logger.debug(f"Could not collect metrics for GPU {gpu_id}: {e}")
            
            # Count active jobs (this would be populated by training system)
            active_jobs = len(self.get_active_training_jobs())
            
            return SystemMetrics(
                cpu_usage_percent=cpu_usage,
                memory_usage_percent=memory_usage,
                disk_usage_percent=disk_usage,
                gpu_metrics=gpu_metrics,
                active_jobs=active_jobs,
                timestamp=timestamp
            )
            
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")
            return None
    
    def get_active_training_jobs(self) -> List[str]:
        """Get list of active training job IDs."""
        # This would be integrated with the distributed trainer
        # For now, return empty list
        return []
    
    def add_training_metric(self, job_id: str, metric_name: str, value: float, 
                          metadata: Optional[Dict[str, Any]] = None):
        """Add a training metric."""
        safe_metadata = metadata if metadata is not None else {}
        metric_point = MetricPoint(
            timestamp=time.time(),
            value=value,
            job_id=job_id,
            metadata=safe_metadata
        )
        
        key = f"training.{job_id}.{metric_name}"
        self._add_metric(key, metric_point)
    
    def _add_metric(self, key: str, metric: Any):
        """Add metric to history."""
        with self._lock:
            if isinstance(metric, SystemMetrics):
                # Convert to metric point for storage
                metric_point = MetricPoint(
                    timestamp=metric.timestamp,
                    value=0,  # Placeholder
                    metadata=asdict(metric)
                )
                self.metrics_history[key].append(metric_point)
            else:
                self.metrics_history[key].append(metric)
    
    def get_metrics(self, key: str, hours: int = 1) -> List[MetricPoint]:
        """Get metrics for a key within time window."""
        cutoff = time.time() - (hours * 3600)
        
        with self._lock:
            if key not in self.metrics_history:
                return []
            
            return [m for m in self.metrics_history[key] if m.timestamp >= cutoff]
    
    def get_latest_system_metrics(self) -> Optional[SystemMetrics]:
        """Get latest system metrics."""
        with self._lock:
            if 'system' not in self.metrics_history or not self.metrics_history['system']:
                return None
            
            latest = self.metrics_history['system'][-1]
            if hasattr(latest, 'metadata') and latest.metadata:
                return SystemMetrics(**latest.metadata)
            
            return None

class MetricsPersistence:
    """Persists metrics to database."""
    
    def __init__(self, db_path: str = "data/metrics.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Initialize metrics database."""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS system_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp REAL NOT NULL,
                        cpu_usage REAL,
                        memory_usage REAL,
                        disk_usage REAL,
                        gpu_metrics TEXT,  -- JSON
                        active_jobs INTEGER,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS training_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp REAL NOT NULL,
                        job_id TEXT NOT NULL,
                        metric_name TEXT NOT NULL,
                        metric_value REAL NOT NULL,
                        metadata TEXT,  -- JSON
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create indexes
                conn.execute("CREATE INDEX IF NOT EXISTS idx_system_timestamp ON system_metrics(timestamp)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_training_job_metric ON training_metrics(job_id, metric_name)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_training_timestamp ON training_metrics(timestamp)")
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Failed to initialize metrics database: {e}")
    
    def save_system_metrics(self, metrics: SystemMetrics):
        """Save system metrics to database."""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                conn.execute("""
                    INSERT INTO system_metrics 
                    (timestamp, cpu_usage, memory_usage, disk_usage, gpu_metrics, active_jobs)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    metrics.timestamp,
                    metrics.cpu_usage_percent,
                    metrics.memory_usage_percent,
                    metrics.disk_usage_percent,
                    json.dumps(metrics.gpu_metrics),
                    metrics.active_jobs
                ))
                conn.commit()
                
        except Exception as e:
            logger.error(f"Failed to save system metrics: {e}")
    
    def save_training_metric(self, job_id: str, metric_name: str, value: float, 
                           timestamp: float, metadata: Optional[Dict[str, Any]] = None):
        """Save training metric to database."""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                conn.execute("""
                    INSERT INTO training_metrics 
                    (timestamp, job_id, metric_name, metric_value, metadata)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    timestamp,
                    job_id,
                    metric_name,
                    value,
                    json.dumps(metadata or {})
                ))
                conn.commit()
                
        except Exception as e:
            logger.error(f"Failed to save training metric: {e}")
    
    def get_system_metrics_history(self, hours: int = 24) -> List[SystemMetrics]:
        """Get system metrics history."""
        cutoff = time.time() - (hours * 3600)
        
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.execute("""
                    SELECT timestamp, cpu_usage, memory_usage, disk_usage, gpu_metrics, active_jobs
                    FROM system_metrics
                    WHERE timestamp >= ?
                    ORDER BY timestamp
                """, (cutoff,))
                
                metrics = []
                for row in cursor:
                    gpu_metrics = json.loads(row[4]) if row[4] else {}
                    metrics.append(SystemMetrics(
                        timestamp=row[0],
                        cpu_usage_percent=row[1],
                        memory_usage_percent=row[2],
                        disk_usage_percent=row[3],
                        gpu_metrics=gpu_metrics,
                        active_jobs=row[5]
                    ))
                
                return metrics
                
        except Exception as e:
            logger.error(f"Failed to get system metrics history: {e}")
            return []
    
    def get_training_metrics_history(self, job_id: str, metric_name: str, hours: int = 24) -> List[MetricPoint]:
        """Get training metrics history."""
        cutoff = time.time() - (hours * 3600)
        
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.execute("""
                    SELECT timestamp, metric_value, metadata
                    FROM training_metrics
                    WHERE job_id = ? AND metric_name = ? AND timestamp >= ?
                    ORDER BY timestamp
                """, (job_id, metric_name, cutoff))
                
                metrics = []
                for row in cursor:
                    metadata = json.loads(row[2]) if row[2] else {}
                    metrics.append(MetricPoint(
                        timestamp=row[0],
                        value=row[1],
                        job_id=job_id,
                        metadata=metadata
                    ))
                
                return metrics
                
        except Exception as e:
            logger.error(f"Failed to get training metrics history: {e}")
            return []

class WebDashboard:
    """Web-based metrics dashboard."""
    
    def __init__(self, collector: MetricsCollector, persistence: MetricsPersistence, 
                 port: int = 8080):
        self.collector = collector
        self.persistence = persistence
        self.port = port
        self.app = None
        
        if dependency_manager.is_available('flask'):
            self._init_flask_app()
        else:
            logger.warning("Flask not available, web dashboard disabled")
    
    def _init_flask_app(self):
        """Initialize Flask application."""
        try:
            from flask import Flask, jsonify, render_template_string, request
            
            self.app = Flask(__name__)
            
            @self.app.route('/')
            def dashboard():
                return render_template_string(self._get_dashboard_template())
            
            @self.app.route('/api/system/current')
            def get_current_system_metrics():
                metrics = self.collector.get_latest_system_metrics()
                if metrics:
                    return jsonify(asdict(metrics))
                return jsonify({'error': 'No metrics available'})
            
            @self.app.route('/api/system/history')
            def get_system_metrics_history():
                hours = request.args.get('hours', default=1, type=int)
                metrics = self.persistence.get_system_metrics_history(hours)
                return jsonify([asdict(m) for m in metrics])
            
            @self.app.route('/api/training/<job_id>/<metric_name>')
            def get_training_metrics(job_id, metric_name):
                hours = request.args.get('hours', default=1, type=int)
                metrics = self.persistence.get_training_metrics_history(job_id, metric_name, hours)
                return jsonify([{
                    'timestamp': m.timestamp,
                    'value': m.value,
                    'metadata': m.metadata
                } for m in metrics])
            
            @self.app.route('/api/jobs/active')
            def get_active_jobs():
                jobs = self.collector.get_active_training_jobs()
                return jsonify(jobs)
            
        except Exception as e:
            logger.error(f"Failed to initialize Flask app: {e}")
    
    def _get_dashboard_template(self) -> str:
        """Get HTML template for dashboard."""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>JARVIS Learning Metrics Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #0a0a0a;
            color: #ffffff;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        .header h1 {
            color: #00d4ff;
            text-shadow: 0 0 10px #00d4ff;
            margin: 0;
        }
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .metric-card {
            background: linear-gradient(135deg, #1a1a1a, #2a2a2a);
            border: 1px solid #333;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 8px rgba(0, 212, 255, 0.1);
        }
        .metric-title {
            color: #00d4ff;
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 15px;
        }
        .metric-value {
            font-size: 24px;
            font-weight: bold;
            colors: #ffffff;
        }
        .chart-container {
            height: 300px;
            margin-top: 15px;
        }
        .gpu-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 10px;
            margin-top: 10px;
        }
        .gpu-card {
            background: #1a1a1a;
            border: 1px solid #444;
            border-radius: 8px;
            padding: 15px;
            text-align: center;
        }
        .gpu-title {
            color: #00d4ff;
            font-size: 14px;
            margin-bottom: 10px;
        }
        .status-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            display: inline-block;
            margin-right: 8px;
        }
        .status-active { background-color: #00ff00; }
        .status-idle { background-color: #ffff00; }
        .status-offline { background-color: #ff0000; }
        .refresh-button {
            background: linear-gradient(45deg, #00d4ff, #0099cc);
            border: none;
            color: white;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            margin: 10px;
        }
        .refresh-button:hover {
            background: linear-gradient(45deg, #0099cc, #00d4ff);
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>ðŸ¤– JARVIS Learning Metrics Dashboard</h1>
        <button class="refresh-button" onclick="refreshData()">ðŸ”„ Refresh</button>
        <span id="lastUpdate"></span>
    </div>

    <div class="metrics-grid">
        <div class="metric-card">
            <div class="metric-title">System Overview</div>
            <div>CPU: <span id="cpuUsage">-</span>%</div>
            <div>Memory: <span id="memoryUsage">-</span>%</div>
            <div>Disk: <span id="diskUsage">-</span>%</div>
            <div>Active Jobs: <span id="activeJobs">-</span></div>
        </div>

        <div class="metric-card">
            <div class="metric-title">GPU Status</div>
            <div id="gpuContainer">
                <div class="gpu-grid" id="gpuGrid">
                    <!-- GPU cards will be populated dynamically -->
                </div>
            </div>
        </div>

        <div class="metric-card">
            <div class="metric-title">System Resource Usage</div>
            <div class="chart-container">
                <canvas id="systemChart"></canvas>
            </div>
        </div>

        <div class="metric-card">
            <div class="metric-title">Training Progress</div>
            <div class="chart-container">
                <canvas id="trainingChart"></canvas>
            </div>
        </div>
    </div>

    <script>
        let systemChart, trainingChart;

        function initCharts() {
            const chartOptions = {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        type: 'time',
                        time: {
                            unit: 'minute'
                        },
                        grid: { color: '#333' },
                        ticks: { color: '#fff' }
                    },
                    y: {
                        grid: { color: '#333' },
                        ticks: { color: '#fff' }
                    }
                },
                plugins: {
                    legend: {
                        labels: { color: '#fff' }
                    }
                }
            };

            // System Chart
            const systemCtx = document.getElementById('systemChart').getContext('2d');
            systemChart = new Chart(systemCtx, {
                type: 'line',
                data: {
                    datasets: [
                        {
                            label: 'CPU %',
                            borderColor: '#ff6b6b',
                            backgroundColor: 'rgba(255, 107, 107, 0.1)',
                            data: []
                        },
                        {
                            label: 'Memory %',
                            borderColor: '#4ecdc4',
                            backgroundColor: 'rgba(78, 205, 196, 0.1)',
                            data: []
                        },
                        {
                            label: 'Disk %',
                            borderColor: '#45b7d1',
                            backgroundColor: 'rgba(69, 183, 209, 0.1)',
                            data: []
                        }
                    ]
                },
                options: {
                    ...chartOptions,
                    scales: {
                        ...chartOptions.scales,
                        y: {
                            ...chartOptions.scales.y,
                            min: 0,
                            max: 100
                        }
                    }
                }
            });

            // Training Chart
            const trainingCtx = document.getElementById('trainingChart').getContext('2d');
            trainingChart = new Chart(trainingCtx, {
                type: 'line',
                data: {
                    datasets: [
                        {
                            label: 'Training Loss',
                            borderColor: '#ff9f43',
                            backgroundColor: 'rgba(255, 159, 67, 0.1)',
                            data: []
                        }
                    ]
                },
                options: chartOptions
            });
        }

        async function fetchMetrics() {
            try {
                const response = await fetch('/api/system/current');
                const data = await response.json();
                
                if (data.error) {
                    console.log('No metrics available yet');
                    return;
                }

                // Update system overview
                document.getElementById('cpuUsage').textContent = data.cpu_usage_percent.toFixed(1);
                document.getElementById('memoryUsage').textContent = data.memory_usage_percent.toFixed(1);
                document.getElementById('diskUsage').textContent = data.disk_usage_percent.toFixed(1);
                document.getElementById('activeJobs').textContent = data.active_jobs;

                // Update GPU status
                updateGPUStatus(data.gpu_metrics);

                // Update charts with historical data
                await updateCharts();

                document.getElementById('lastUpdate').textContent = 
                    'Last updated: ' + new Date().toLocaleTimeString();

            } catch (error) {
                console.error('Error fetching metrics:', error);
            }
        }

        function updateGPUStatus(gpuMetrics) {
            const grid = document.getElementById('gpuGrid');
            grid.innerHTML = '';

            Object.entries(gpuMetrics).forEach(([gpuId, metrics]) => {
                const card = document.createElement('div');
                card.className = 'gpu-card';

                const status = metrics.utilization_percent ? 
                    (metrics.utilization_percent > 10 ? 'active' : 'idle') : 'idle';

                card.innerHTML = `
                    <div class="gpu-title">
                        <span class="status-indicator status-${status}"></span>
                        GPU ${gpuId}
                    </div>
                    <div>Memory: ${metrics.memory_used_percent.toFixed(1)}%</div>
                    <div>Utilization: ${(metrics.utilization_percent || 0).toFixed(1)}%</div>
                `;

                grid.appendChild(card);
            });
        }

        async function updateCharts() {
            try {
                // Get system metrics history
                const systemResponse = await fetch('/api/system/history?hours=1');
                const systemData = await systemResponse.json();

                if (systemData.length > 0) {
                    const timestamps = systemData.map(d => d.timestamp * 1000);
                    
                    systemChart.data.datasets[0].data = systemData.map((d, i) => ({
                        x: timestamps[i],
                        y: d.cpu_usage_percent
                    }));
                    
                    systemChart.data.datasets[1].data = systemData.map((d, i) => ({
                        x: timestamps[i],
                        y: d.memory_usage_percent
                    }));
                    
                    systemChart.data.datasets[2].data = systemData.map((d, i) => ({
                        x: timestamps[i],
                        y: d.disk_usage_percent
                    }));

                    systemChart.update('none');
                }

                // Training metrics would be updated here when jobs are active
                
            } catch (error) {
                console.error('Error updating charts:', error);
            }
        }

        function refreshData() {
            fetchMetrics();
        }

        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            initCharts();
            fetchMetrics();
            
            // Auto-refresh every 5 seconds
            setInterval(fetchMetrics, 5000);
        });
    </script>
</body>
</html>
        """
    
    def start(self):
        """Start the web dashboard."""
        if not self.app:
            logger.error("Flask app not initialized, cannot start dashboard")
            return
        
        try:
            self.app.run(host='0.0.0.0', port=self.port, debug=False)
        except Exception as e:
            logger.error(f"Failed to start web dashboard: {e}")

class MetricsDashboard:
    """Main metrics dashboard orchestrator."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        config = config or {}
        
        # Initialize components
        self.collector = MetricsCollector(
            collection_interval=config.get('collection_interval', 1.0)
        )
        
        self.persistence = MetricsPersistence(
            db_path=config.get('db_path', 'data/metrics.db')
        )
        
        self.web_dashboard = WebDashboard(
            collector=self.collector,
            persistence=self.persistence,
            port=config.get('web_port', 8080)
        )
        
        # Set up persistence sync
        self._setup_persistence_sync()
    
    def _setup_persistence_sync(self):
        """Set up automatic persistence of collected metrics."""
        def sync_worker():
            while self.collector.running:
                try:
                    # Save latest system metrics
                    latest_system = self.collector.get_latest_system_metrics()
                    if latest_system:
                        self.persistence.save_system_metrics(latest_system)
                    
                    # Sleep for persistence interval
                    time.sleep(10)  # Save every 10 seconds
                    
                except Exception as e:
                    logger.error(f"Error in persistence sync: {e}")
                    time.sleep(1)
        
        # Start sync worker thread
        sync_thread = threading.Thread(target=sync_worker, daemon=True)
        sync_thread.start()
    
    def start(self):
        """Start the complete metrics dashboard system."""
        logger.info("Starting JARVIS Learning Metrics Dashboard")
        
        # Start metrics collection
        self.collector.start()
        
        # Start web dashboard
        web_thread = threading.Thread(target=self.web_dashboard.start, daemon=True)
        web_thread.start()
        
        logger.info(f"Metrics dashboard available at http://localhost:{self.web_dashboard.port}")
    
    def stop(self):
        """Stop the metrics dashboard system."""
        logger.info("Stopping metrics dashboard")
        self.collector.stop()
    
    def add_training_metric(self, job_id: str, metric_name: str, value: float,
                          metadata: Optional[Dict[str, Any]] = None):
        """Add a training metric."""
        safe_metadata = metadata if metadata is not None else {}
        self.collector.add_training_metric(job_id, metric_name, value, safe_metadata)
        
        # Also persist directly
        timestamp = time.time()
        self.persistence.save_training_metric(job_id, metric_name, value, timestamp, safe_metadata)
    
    def get_dashboard_status(self) -> Dict[str, Any]:
        """Get overall dashboard status."""
        return {
            'collector_running': self.collector.running,
            'latest_system_metrics': self.collector.get_latest_system_metrics(),
            'active_training_jobs': self.collector.get_active_training_jobs(),
            'web_dashboard_port': self.web_dashboard.port,
            'database_path': str(self.persistence.db_path)
        }
