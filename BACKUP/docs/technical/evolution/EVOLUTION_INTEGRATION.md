# JARVIS 5.0 - Evolution Layer Integration Guide

## ✅ Integration Status

The Evolution Layer has been **successfully integrated** into JARVIS 5.0's main system (main.py).

## 🚀 How It Works

### Automatic Integration

When you start JARVIS 5.0, the Evolution Layer automatically initializes during **Stage 3** (Neural Engines) if enabled.

**Default Behavior:**
- ✅ **Enabled by default** - The system starts with self-healing capabilities
- ✅ **Automatic startup** - No manual configuration needed
- ✅ **Graceful shutdown** - Properly stops when JARVIS shuts down

### Configuration

#### Enable/Disable Evolution Layer

Set the environment variable before starting JARVIS:

**Windows (PowerShell):**
```powershell
$env:JARVIS_EVOLUTION_ENABLED="true"
python main.py
```

**Windows (Command Prompt):**
```cmd
set JARVIS_EVOLUTION_ENABLED=true
python main.py
```

**Linux/Mac:**
```bash
export JARVIS_EVOLUTION_ENABLED=true
python main.py
```

**To Disable:**
```bash
export JARVIS_EVOLUTION_ENABLED=false
python main.py
```

## 📊 What Gets Activated

When the Evolution Layer starts, you'll see these log messages:

```
🧬 [EVOLUTION] Initializing Self-Healing System...
👁️ Self-Observer started
🧠 Auto-Healer operational
🛡️ Safe Executor operational
✅ [EVOLUTION] Self-Healing System operational
🧬 [EVOLUTION] Integration complete - System is self-aware
```

### Active Components

1. **Self Observer** - Monitors system health every 5 minutes
   - CPU, RAM, GPU metrics
   - Code quality analysis
   - Configuration validation
   - Health checks (Ollama, camera, etc.)

2. **Auto Healer** - Diagnoses problems automatically
   - Identifies issues from observations
   - Consults AI (Ollama) for solutions
   - Prioritizes fixes by impact

3. **Safe Executor** - Applies fixes safely
   - Creates automatic backups
   - Validates changes
   - Rolls back on failure

4. **Knowledge Database** - Learns from experience
   - Records problems and solutions
   - Tracks success rates
   - Improves over time

## 🎮 Runtime Control

### Access Evolution Manager

The Evolution Manager is available in the instances dictionary:

```python
# In JARVIS code
evolution_manager = instances.get("evolution_manager")

if evolution_manager:
    # Check status
    status = evolution_manager.get_status()
    print(f"Evolution Layer running: {status['running']}")
    
    # Trigger manual maintenance
    await evolution_manager.trigger_maintenance()
    
    # Disable auto-healing temporarily
    evolution_manager.disable_auto_heal()
    
    # Re-enable
    evolution_manager.enable_auto_heal()
```

## 📝 Log Messages

### Successful Startup
```
🧬 [EVOLUTION] Initializing Self-Healing System...
✅ [EVOLUTION] Self-Healing System operational
🧬 [EVOLUTION] Integration complete - System is self-aware
```

### Disabled
```
⚠️ [EVOLUTION] Self-Healing System disabled (set JARVIS_EVOLUTION_ENABLED=true to enable)
```

### Startup Error
```
❌ [EVOLUTION] Failed to start: <error details>
⚠️ [EVOLUTION] Could not initialize Evolution Layer: <error>
   System will continue without self-healing capabilities
```

### Shutdown
```
🧬 [EVOLUTION] Shutting down Self-Healing System...
✅ [EVOLUTION] Shutdown complete
```

## 🔧 Advanced Configuration

### Custom Parameters

To customize the Evolution Layer, modify the startup parameters in main.py (line ~1618):

```python
await evolution_manager.start(
    observer_interval=300,  # Seconds between health checks (default: 300 = 5 min)
    auto_heal=True,         # Enable/disable automatic fixes (default: True)
    initial_scan=True       # Run health check on startup (default: True)
)
```

**Common Configurations:**

**More Frequent Monitoring:**
```python
observer_interval=60  # Check every minute
```

**Observation Only (No Auto-Fixes):**
```python
auto_heal=False  # Just monitor, don't fix
```

**Skip Initial Scan:**
```python
initial_scan=False  # Don't scan on startup
```

## 🧪 Testing the Integration

### 1. Check If It's Running

Look for the log messages when JARVIS starts:
```
🧬 [EVOLUTION] Initializing Self-Healing System...
```

### 2. Verify Components

Check the logs for component status:
```
👁️ Self-Observer started
🧠 Auto-Healer operational  
🛡️ Safe Executor operational
```

### 3. Monitor Activity

The Evolution Layer will log activity:
```
🔎 Starting system observation cycle...
✅ Observation cycle completed and reported
🤒 Detected X health issues
🔧 Executing fix: <description>
✅ Fix validated successfully
```

### 4. Check Database

After running for a while, check the knowledge database:
```
data/learning/knowledge.db
```

## 📁 File Locations

```
Project Structure:
├── main.py                          [✅ Evolution Layer integrated here]
├── src/evolution/
│   ├── evolution_manager.py         [Main coordinator]
│   ├── self_observer.py             [System monitoring]
│   ├── auto_healer.py               [Problem diagnosis]
│   ├── safe_executor.py             [Safe execution]
│   └── knowledge_db.py              [Learning database]
├── data/
│   ├── learning/
│   │   └── knowledge.db             [Created automatically]
│   └── backups/auto/                [Automatic backups]
├── docs/
│   ├── EVOLUTION_LAYER.md           [Full documentation]
│   └── EVOLUTION_QUICK_START.md     [Quick reference]
└── demo_evolution.py                [Standalone demo]
```

## 🐛 Troubleshooting

### Evolution Layer Doesn't Start

**Check:**
1. Environment variable: `echo $JARVIS_EVOLUTION_ENABLED`
2. Dependencies installed: `pip install psutil aiofiles requests`
3. Check logs for error messages

**Solution:**
```bash
pip install psutil aiofiles requests
export JARVIS_EVOLUTION_ENABLED=true
python main.py
```

### LLM Not Responding

**Problem:** Auto-healer can't generate fixes

**Check:**
```bash
curl http://localhost:11434/api/tags
```

**Solution:**
```bash
ollama serve
```

### Database Errors

**Problem:** SQLite errors about locked database

**Solution:**
- Only run one JARVIS instance at a time
- Check file permissions on `data/learning/`

## 🎯 Use Cases

### 1. Automatic Problem Detection

JARVIS detects and fixes issues like:
- Configuration errors
- Missing dependencies
- Code quality issues (bare excepts, local imports)
- Performance problems

### 2. Continuous Learning

- First time a problem occurs: AI generates solution
- Next time: Uses previous successful solution
- Improves success rate over time

### 3. Safe Experimentation

- All fixes are backed up automatically
- Changes are validated before applying
- Automatic rollback on failure

## 📚 Additional Resources

- **Full Documentation:** `docs/EVOLUTION_LAYER.md`
- **Quick Start:** `docs/EVOLUTION_QUICK_START.md`
- **Implementation Details:** `IMPLEMENTATION_SUMMARY.md`
- **Standalone Demo:** Run `python demo_evolution.py`

## 🔐 Security Notes

The Evolution Layer follows strict security rules:
- ✅ Core system files are protected from auto-modification
- ✅ All changes are backed up before execution
- ✅ Syntax validation before applying fixes
- ✅ Automatic rollback on failure
- ✅ Limited to 10 auto-corrections per day
- ✅ Maximum 3 attempts per problem

## 🎉 Success!

If you see this message, the Evolution Layer is working:

```
🧬 [EVOLUTION] Integration complete - System is self-aware
```

Your JARVIS system now has self-healing capabilities! 🚀

---

**Need help?** Check the full documentation in `docs/EVOLUTION_LAYER.md`
