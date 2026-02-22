import os
import shutil
import site
import subprocess
import sys


def clean_and_reinstall_torch():
    # 1. Inspect site-packages
    site_packages = site.getsitepackages()[0]
    print(f"Inspecting {site_packages}...")

    # 2. Remove garbage directories (starting with ~)
    count = 0
    try:
        for item in os.listdir(site_packages):
            if item.startswith("~"):
                path = os.path.join(site_packages, item)
                print(f"Removing garbage: {item}")
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
                count += 1
    except Exception as e:
        print(f"Error cleaning garbage: {e}")

    print(f"Removed {count} garbage items.")

    # 3. Force uninstall torch
    print("Uninstalling torch...")
    subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "uninstall",
            "-y",
            "torch",
            "torchaudio",
            "torchvision",
        ],
        check=False,
    )

    # 4. Install correct version
    print("Installing Torch 2.4.1+cpu...")
    try:
        subprocess.run(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "torch==2.4.1",
                "torchaudio==2.4.1",
                "--index-url",
                "https://download.pytorch.org/whl/cpu",
            ],
            check=True,
        )
        print("Installation successful!")
    except subprocess.CalledProcessError:
        print("Installation failed.")


if __name__ == "__main__":
    clean_and_reinstall_torch()
