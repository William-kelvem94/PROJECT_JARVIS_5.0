import urllib.request
from pathlib import Path


def download_file(url, target_path):
    print(f"📥 Downloading {url}...")
    try:
        Path(target_path).parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(url, target_path)
        print(f"✅ Success: {target_path}")
        return True
    except Exception as e:
        print(f"❌ Failed to download {url}: {e}")
        return False


def main():
    models = {
        "models/yolov8n.pt": "https://github.com/ultralytics/assets/releases/download/v8.2.0/yolov8n.pt",
        "models/hand_landmarker.task": "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task",
    }

    # Note: Vosk is usually a zip, so we'd need extraction logic.
    # For now, we'll download the main ones.

    success_count = 0
    for path, url in models.items():
        if download_file(url, path):
            success_count += 1

    if success_count == len(models):
        print("\n✨ All critical models are now present.")
    else:
        print("\n⚠️ Some models could not be downloaded. Check your connection.")


if __name__ == "__main__":
    main()
