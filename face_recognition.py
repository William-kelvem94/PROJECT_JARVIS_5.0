"""Lightweight stub of `face_recognition` to satisfy static analysis in dev environments.
Replace with real `face_recognition` package for production use.
"""

from typing import List, Tuple, Any

def load_image_file(path: str) -> Any:
    """Return a placeholder image object. Real implementation required for face ops."""
    return None

def face_locations(image: Any) -> List[Tuple[int,int,int,int]]:
    return []

def face_encodings(image: Any, known_face_locations=None) -> List[bytes]:
    return []

def compare_faces(known_encodings, face_encoding_to_check, tolerance=0.6):
    return [False for _ in known_encodings]

# Minimal constants
api_version = 'stub'
