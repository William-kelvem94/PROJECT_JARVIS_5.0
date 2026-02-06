"""
Test script for VisionEnhancer (Phase 4)
Tests YOLO UI detection and OCR capabilities
"""

import cv2
import numpy as np
from pathlib import Path
from src.core.vision_enhancer import vision_enhancer

print("=" * 70)
print("👁️ JARVIS VISION ENHANCEMENT - VisionEnhancer Test")
print("=" * 70)

# Test 1: Stats
print("\n1️⃣ VISION STATS:")
stats = vision_enhancer.get_stats()
for key, value in stats.items():
    print(f"   {key}: {value}")

# Test 2: Create test image with text
print("\n2️⃣ CRIANDO IMAGEM DE TESTE:")
test_dir = Path("data/test_images")
test_dir.mkdir(parents=True, exist_ok=True)

# Criar imagem simples com texto
img = np.ones((600, 800, 3), dtype=np.uint8) * 255

# Adicionar texto
cv2.putText(img, "JARVIS Vision Test", (50, 100), 
            cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 3)
cv2.putText(img, "Click Here", (300, 300), 
            cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 2)
cv2.putText(img, "Settings", (300, 400), 
            cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 2)

# Desenhar retângulos (simular botões)
cv2.rectangle(img, (280, 250), (480, 330), (0, 0, 255), 2)
cv2.rectangle(img, (280, 350), (450, 430), (0, 0, 0), 2)

test_image_path = test_dir / "test_screen.png"
cv2.imwrite(str(test_image_path), img)
print(f"   ✅ Imagem criada: {test_image_path}")

# Test 3: Analyze screen
print("\n3️⃣ ANALISANDO TELA:")
analysis = vision_enhancer.analyze_screen(
    str(test_image_path),
    detect_ui=True,
    extract_text=True
)

print(f"   UI Elements: {len(analysis['ui_elements'])}")
print(f"   Text Regions: {len(analysis['text_regions'])}")
print(f"   Clickable Areas: {len(analysis['clickable_areas'])}")
print(f"   Summary: {analysis['summary']}")

# Test 4: Text extraction details
if analysis['text_regions']:
    print("\n4️⃣ TEXTO DETECTADO:")
    for i, region in enumerate(analysis['text_regions'][:5], 1):
        print(f"   {i}. '{region['text']}' @ ({region['center']['x']}, {region['center']['y']})")
        print(f"      Confidence: {region['confidence']:.2f}")

# Test 5: Find element by text
print("\n5️⃣ BUSCAR ELEMENTO POR TEXTO:")
target = "Click Here"
element = vision_enhancer.find_element_by_text(str(test_image_path), target)
if element:
    print(f"   ✅ Encontrado '{target}'")
    print(f"      Posição: ({element['center']['x']}, {element['center']['y']})")
else:
    print(f"   ❌ '{target}' não encontrado")

print("\n" + "=" * 70)
print("✅ TESTE COMPLETO!")
print("=" * 70)
print("\n💡 NOTA: YOLO pode não detectar elementos em imagem sintética.")
print("   Para melhor resultado, use screenshot real de aplicação.")
