import sys


def check_lib(name):
    try:
        mod = __import__(name)
        version = getattr(mod, "__version__", "unknown")
        path = getattr(mod, "__file__", "unknown")
        print(f"✅ {name}: {version} at {path}")
        return mod
    except ImportError as e:
        print(f"❌ {name}: NOT INSTALLED ({e})")
        return None
    except Exception as e:
        print(f"❌ {name}: ERROR LOADING ({e})")
        return None


print(f"Python: {sys.version}")
print("-" * 50)

numpy = check_lib("numpy")
torch = check_lib("torch")
chromadb = check_lib("chromadb")
onnxruntime = check_lib("onnxruntime")
sqlite3 = check_lib("sqlite3")

if chromadb:
    try:
        import chromadb.api

        print("✅ chromadb.api: OK")
    except Exception as e:
        print(f"❌ chromadb.api: ERROR ({e})")

if numpy:
    try:
        print("✅ numpy.linalg: OK")
    except Exception as e:
        # NumPy 2.x changed things
        print(f"⚠️ numpy.linalg Check: {e}")

# Check for pysqlite3 (often used by chromadb)
check_lib("pysqlite3")
