# JARVIS 5.0 Evolution Layer - Quick Start

## 🚀 What is This?

The **Evolution Layer** makes JARVIS self-healing, self-organizing, and self-improving. It continuously monitors the system, detects problems, and fixes them automatically.

## ⚡ Quick Start

### 1. Install Dependencies

```bash
pip install psutil aiofiles requests
```

### 2. Try the Demo

```bash
python demo_evolution.py
```

### 3. Add to Your Code

```python
from src.evolution import evolution_manager

async def main():
    # Start self-healing system
    await evolution_manager.start(
        observer_interval=300,  # Check every 5 minutes
        auto_heal=True,
        initial_scan=True
    )
    
    # Your code here...
    
    # Stop gracefully
    await evolution_manager.stop()
```

## 🧩 What It Does

### Self-Observer
✓ Monitors CPU, RAM, GPU  
✓ Scans code for issues  
✓ Checks system health  
✓ Reports every 5 minutes

### Auto-Healer
✓ Identifies problems  
✓ Consults AI (Ollama) for solutions  
✓ Learns from past fixes  
✓ Prioritizes actions

### Safe Executor
✓ Creates automatic backups  
✓ Tests changes before applying  
✓ Rolls back on failure  
✓ Records results

### Knowledge Database
✓ Stores problems and solutions  
✓ Tracks success rates  
✓ Improves over time  
✓ SQLite-based

## 📊 Check Status

```python
# Get current status
status = evolution_manager.get_status()
print(f"Running: {status['running']}")
print(f"Auto-heal: {status['auto_heal_enabled']}")

# Get statistics
from src.evolution import knowledge_db
stats = knowledge_db.get_statistics()
print(f"Success rate: {stats['success_rate']}%")
```

## 🎮 Control

```python
# Trigger manual maintenance
await evolution_manager.trigger_maintenance()

# Disable auto-healing (observation only)
evolution_manager.disable_auto_heal()

# Re-enable auto-healing
evolution_manager.enable_auto_heal()
```

## 🔒 Safety Features

- ✓ Automatic backups before any change
- ✓ Syntax validation
- ✓ Automatic rollback on failure
- ✓ Protected core files
- ✓ Limit of 3 attempts per problem

## 📁 Files

```
src/evolution/
├── evolution_manager.py   # Main coordinator
├── self_observer.py       # System monitoring
├── auto_healer.py         # Problem diagnosis
├── safe_executor.py       # Safe corrections
└── knowledge_db.py        # Learning database

tests/unit/
└── test_evolution_layer.py  # 21 tests (all passing)

demo_evolution.py          # Interactive demo
docs/EVOLUTION_LAYER.md    # Full documentation
```

## 🧪 Run Tests

```bash
# All tests
pytest tests/unit/test_evolution_layer.py -v

# Specific component
pytest tests/unit/test_evolution_layer.py::TestSelfObserver -v
```

## 📡 Event Bus Integration

The system publishes events:
- `SYSTEM_OBSERVER_REPORT` - After each scan
- `SYSTEM_DIAGNOSTIC_PLAN` - Healing plan ready
- `SYSTEM_CORRECTION_SUCCEEDED` - Fix applied
- `SYSTEM_CORRECTION_FAILED` - Fix failed

## 🐛 Troubleshooting

**LLM not responding?**
```bash
# Check Ollama
curl http://localhost:11434/api/tags

# Start Ollama if needed
ollama serve
```

**Database locked?**  
Only run one instance per process.

**Auto-heal not working?**  
Check: `evolution_manager.auto_heal_enabled` and Ollama config.

## 📚 Learn More

- Full documentation: `docs/EVOLUTION_LAYER.md`
- Problem statement: See the PR description
- Tests: `tests/unit/test_evolution_layer.py`

## 🎯 Examples

### Example 1: Basic Usage

```python
import asyncio
from src.evolution import evolution_manager

async def main():
    await evolution_manager.start()
    await asyncio.sleep(60)  # Run for 1 minute
    await evolution_manager.stop()

asyncio.run(main())
```

### Example 2: Get Statistics

```python
from src.evolution import knowledge_db

stats = knowledge_db.get_statistics()
print(f"Problems: {stats['total_problems']}")
print(f"Solutions: {stats['total_solutions']}")
print(f"Success: {stats['success_rate']}%")
```

### Example 3: Manual Trigger

```python
async def force_scan():
    await evolution_manager.trigger_maintenance()
    print("Scan complete!")
```

## ✅ Status

**All 21 tests passing** ✓  
**Demo working** ✓  
**Documentation complete** ✓  
**Ready for integration** ✓

---

**Need help?** Check `docs/EVOLUTION_LAYER.md` for detailed documentation.
