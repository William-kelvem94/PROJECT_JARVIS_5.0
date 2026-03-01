import livekit.agents
import pkgutil
import sys

def find_module(package, target):
    for loader, name, ispkg in pkgutil.walk_packages(package.__path__, package.__name__ + "."):
        if target in name:
            print(f"Found: {name}")

find_module(livekit.agents, "multimodal")
find_module(livekit.agents, "Assistant")
