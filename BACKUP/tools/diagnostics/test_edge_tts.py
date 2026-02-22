import asyncio
import edge_tts
from pathlib import Path


async def test_edge():
    text = "Olá, eu sou o JARVIS. Como posso ajudar?"
    path = Path("test_edge.wav")
    try:
        communicate = edge_tts.Communicate(text, "pt-BR-FranciscaNeural")
        await communicate.save(str(path))
        print(f"Success! File saved to {path}")
    except Exception as e:
        print(f"Failed: {e}")


if __name__ == "__main__":
    asyncio.run(test_edge())
