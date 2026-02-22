#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste do Sistema de Logging Melhorado JARVIS
===========================================
Testa o novo sistema unificado de logging com prevenção de duplicatas
"""

from src.core.config.blackbox_logger import blackbox_logger
from src.utils.jarvis_logger import get_component_logger, setup_jarvis_logging
import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_unified_logging():
    """Test the unified logging system"""
    print("🧪 Testing JARVIS Unified Logging System")
    print("=" * 50)

    # Setup logging in temp directory
    import tempfile

    with tempfile.TemporaryDirectory() as temp_dir:
        log_dir = Path(temp_dir) / "logs"

        # Setup unified logging
        logger_system = setup_jarvis_logging(log_dir)

        # Get component loggers
        ai_logger = get_component_logger("ai_agent")
        vision_logger = get_component_logger("vision_system")
        core_logger = get_component_logger("core")

        print("📝 Testing normal logging...")

        # Test normal logging
        ai_logger.info("🤖 AI Agent initialized successfully")
        vision_logger.info("👁️ Vision system online")
        core_logger.warning("⚠️ System running in development mode")

        # Test error logging
        ai_logger.error(
            "❌ Failed to process user request",
            extra={
                "context": {"user_id": "test_user", "request": "invalid"},
                "error_code": "E001",
            },
        )

        print("🔄 Testing duplicate prevention...")

        # Test duplicate prevention
        for i in range(10):
            ai_logger.warning("💀 Watchdog: MainUI is DEAD (No heartbeat detected)")
            time.sleep(0.1)  # Small delay to test timing

        print("⏱️ Testing rapid duplicate messages...")

        # Test rapid duplicates (should be filtered)
        for i in range(5):
            vision_logger.error("🚨 Camera feed lost - attempting reconnection")

        print("📊 Testing structured logging...")

        # Test structured logging
        core_logger.info(
            "🔧 System maintenance completed",
            extra={
                "context": {
                    "operation": "cleanup",
                    "files_removed": 15,
                    "space_freed_mb": 234.5,
                }
            },
        )

        # Test blackbox integration
        print("📦 Testing Blackbox Logger integration...")
        blackbox_logger.info("🎯 Blackbox test message", component="test")
        blackbox_logger.log_event("system_test", {"status": "completed"}, "test")

        print("✅ Logging system test completed!")
        print(f"📁 Logs saved to: {log_dir}")

        # Show some log files
        log_files = list(log_dir.glob("*.log"))
        if log_files:
            print(f"📄 Generated log files: {len(log_files)}")
            for log_file in log_files[:3]:  # Show first 3
                size = log_file.stat().st_size
                print(f"  - {log_file.name}: {size} bytes")


if __name__ == "__main__":
    test_unified_logging()
