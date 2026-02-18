import time
import psutil
from datetime import datetime

try:
    from src.core.infrastructure.watchdog import watchdog_system
except Exception:
    watchdog_system = None

PRINT_INTERVAL = 2.0
TOP_N = 8


def fmt_seconds(dt):
    try:
        return f"{(datetime.now() - dt).total_seconds():.1f}s"
    except Exception:
        return "-"


while True:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    vm = psutil.virtual_memory()
    swap = psutil.swap_memory()
    print(
        f"\n[{now}] MEM={vm.percent}% (avail={vm.available//1024//1024}MB) SWAP={swap.percent}%"
    )

    # Top processes by RSS
    procs = []
    for p in psutil.process_iter(
        ["pid", "name", "username", "memory_info", "cpu_percent"]
    ):
        try:
            info = p.info
            rss = info["memory_info"].rss if info.get("memory_info") else 0
            procs.append(
                (rss, info["pid"], info.get("name", ""), info.get("cpu_percent", 0.0))
            )
        except Exception:
            continue
    procs.sort(reverse=True)
    print("Top processes by RSS:")
    for rss, pid, name, cpu in procs[:TOP_N]:
        print(f"  PID {pid:6} {name[:25]:25} RSS={rss//1024//1024:6}MB CPU={cpu:5.1f}%")

    # Watchdog components
    if watchdog_system is not None:
        try:
            comps = getattr(watchdog_system, "_components", {})
            if comps:
                print("\nWatchdog components:")
                for cname, comp in comps.items():
                    hb_age = fmt_seconds(comp.last_heartbeat)
                    print(
                        f"  {cname:30} status={comp.status.value:8} last_hb={hb_age} mem={comp.memory_usage_mb:.1f}MB cpu={comp.cpu_usage_percent:.1f}%"
                    )
            else:
                print("\nWatchdog components: (none registered)")
        except Exception as e:
            print("\nWatchdog components: error", e)
    else:
        print("\nWatchdog: not available")

    print("\n---")
    time.sleep(PRINT_INTERVAL)
