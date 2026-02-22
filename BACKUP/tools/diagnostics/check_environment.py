import importlib

deps_to_test = [
    "numpy",
    "torch",
    "torchvision",
    "onnxruntime",
    "face_recognition",
    "cv2",
    "PyQt6",
    "chromadb",
    "transformers",
]

print("Testing dependencies...")
for dep in deps_to_test:
    try:
        mod = importlib.import_module(dep)
        version = getattr(mod, "__version__", "unknown")
        print(f"✅ {dep}: {version}")
    except ImportError as e:
        print(f"❌ {dep}: ImportError - {e}")
    except Exception as e:
        print(f"⚠️  {dep}: Error - {e}")

print("Done.")
