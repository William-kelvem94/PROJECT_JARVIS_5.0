#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS 5.0 Evolution Layer - Demo & Integration Example
=======================================================
Demonstrates the self-healing capabilities of JARVIS 5.0

This script shows how to:
1. Start the evolution layer
2. Trigger a system observation
3. View knowledge base statistics
4. Stop the system gracefully
"""

import asyncio
import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.evolution import evolution_manager, knowledge_db

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def demo_evolution_layer():
    """
    Demonstrates the JARVIS Evolution Layer in action.
    """
    print("\n" + "="*70)
    print("  JARVIS 5.0 - Evolution Layer Demo")
    print("  Self-Organizing, Self-Healing, Self-Developing System")
    print("="*70 + "\n")

    try:
        # 1. Initialize and start the evolution layer
        print("📋 Step 1: Initializing Evolution Layer...")
        print("-" * 70)
        # Note: Using 60 seconds for demo (faster than production default of 300s)
        await evolution_manager.start(
            observer_interval=60,  # Check every 60 seconds (demo mode)
            auto_heal=True,        # Enable auto-healing
            initial_scan=True      # Run initial scan
        )
        print("\n✅ Evolution Layer started successfully!\n")

        # 2. Wait for initial scan to complete
        print("⏳ Waiting for initial system scan to complete...")
        await asyncio.sleep(2)

        # 3. Display system status
        print("\n📊 Step 2: System Status")
        print("-" * 70)
        status = evolution_manager.get_status()
        print(f"  • Running: {status['running']}")
        print(f"  • Auto-heal enabled: {status['auto_heal_enabled']}")
        print(f"  • Observer interval: {status['observer_interval']}s")
        print(f"  • Uptime: {status['uptime_seconds']:.1f}s")
        print(f"\n  Components Status:")
        for component, running in status['components'].items():
            print(f"    - {component}: {'✓' if running else '✗'}")

        # 4. Display knowledge base statistics
        print("\n📚 Step 3: Knowledge Base Statistics")
        print("-" * 70)
        kb_stats = status.get('knowledge_stats')
        if kb_stats:
            print(f"  • Total problems recorded: {kb_stats['total_problems']}")
            print(f"  • Total solutions attempted: {kb_stats['total_solutions']}")
            print(f"  • Success rate: {kb_stats['success_rate']}%")
            
            if kb_stats['top_affected_modules']:
                print(f"\n  Top affected modules:")
                for mod in kb_stats['top_affected_modules']:
                    print(f"    - {mod['module']}: {mod['count']} issues")
        else:
            print("  No statistics available yet (fresh database)")

        # 5. Trigger a manual maintenance cycle
        print("\n🔧 Step 4: Triggering Manual Maintenance Cycle")
        print("-" * 70)
        print("  Forcing a system observation and diagnostic...")
        await evolution_manager.trigger_maintenance()
        await asyncio.sleep(2)
        print("  ✓ Maintenance cycle completed")

        # 6. Demonstrate auto-heal toggle
        print("\n⚙️  Step 5: Auto-Heal Control Demo")
        print("-" * 70)
        print("  Current state: ENABLED")
        evolution_manager.disable_auto_heal()
        print("  → Auto-healing DISABLED (observation only mode)")
        await asyncio.sleep(1)
        evolution_manager.enable_auto_heal()
        print("  → Auto-healing RE-ENABLED")

        # 7. Keep running for a bit to show monitoring
        print("\n👀 Step 6: Continuous Monitoring")
        print("-" * 70)
        print("  System is now monitoring itself continuously...")
        print("  (Running for 10 seconds to demonstrate)")
        for i in range(10, 0, -1):
            print(f"  ⏱  {i} seconds remaining...", end='\r')
            await asyncio.sleep(1)
        print("\n  ✓ Monitoring demonstration complete")

    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        logger.error(f"Error during demo: {e}", exc_info=True)
    finally:
        # 8. Graceful shutdown
        print("\n🛑 Step 7: Graceful Shutdown")
        print("-" * 70)
        await evolution_manager.stop()
        print("  ✓ All components stopped")

    print("\n" + "="*70)
    print("  Demo completed successfully!")
    print("  The Evolution Layer is ready for production use.")
    print("="*70 + "\n")


async def simple_integration_example():
    """
    Simple example showing how to integrate evolution layer in main.py
    """
    print("\n--- Simple Integration Example ---\n")
    print("To integrate into your main JARVIS system, add this to main.py:\n")
    
    integration_code = """
# In main.py, after other imports:
from src.evolution import evolution_manager

async def main():
    # ... your existing initialization code ...
    
    # Start the evolution layer
    await evolution_manager.start(
        observer_interval=300,  # 5 minutes
        auto_heal=True,
        initial_scan=True
    )
    
    # ... rest of your main loop ...
    
    try:
        # Your main application loop
        while True:
            await asyncio.sleep(1)
    finally:
        # Cleanup
        await evolution_manager.stop()
"""
    
    print(integration_code)
    print("-" * 70 + "\n")


def show_usage():
    """Show usage information"""
    print("\nJARVIS 5.0 Evolution Layer - Usage")
    print("="*70)
    print("\nAvailable Components:")
    print("  • evolution_manager  - Main controller")
    print("  • self_observer      - System monitoring")
    print("  • auto_healer        - Problem diagnosis")
    print("  • safe_executor      - Safe code correction")
    print("  • knowledge_db       - Learning database")
    
    print("\nKey Features:")
    print("  ✓ Automatic system health monitoring")
    print("  ✓ AI-powered problem diagnosis (via Ollama)")
    print("  ✓ Safe code correction with rollback")
    print("  ✓ Learning from past solutions")
    print("  ✓ Human supervision and override")
    
    print("\nSafety Features:")
    print("  ✓ Automatic backups before any change")
    print("  ✓ Syntax validation before applying fixes")
    print("  ✓ Rollback on failure")
    print("  ✓ Protected core system files")
    
    print("\nEvent Bus Integration:")
    print("  • SYSTEM_OBSERVER_REPORT     - Published after each scan")
    print("  • SYSTEM_DIAGNOSTIC_PLAN     - Published with healing plan")
    print("  • SYSTEM_CORRECTION_SUCCEEDED - Published on successful fix")
    print("  • SYSTEM_CORRECTION_FAILED    - Published on failed fix")
    print("="*70 + "\n")


if __name__ == '__main__':
    # Show usage info
    show_usage()
    
    # Show integration example
    asyncio.run(simple_integration_example())
    
    # Run the full demo
    print("\nStarting full demonstration...\n")
    asyncio.run(demo_evolution_layer())
