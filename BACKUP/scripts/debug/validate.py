#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS Implementation Validator (Wrapper)
========================================
Now uses install_system engine for unified validation.
"""

import sys
from install_system import JarvisAutoSystem


def main():
    system = JarvisAutoSystem()
    results = system.validate_system()

    print("\n" + "=" * 70)
    print("JARVIS VALIDATION RESULTS")
    print("=" * 70)

    for item, status in results.items():
        color = "\033[92m" if status == "OK" else "\033[91m"
        print(f"  {item}: {color}{status}\033[0m")

    print("=" * 70)
    return 0 if all(v == "OK" for v in results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
