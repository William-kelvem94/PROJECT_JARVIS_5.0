#!/usr/bin/env python3
"""
Script to generate a test face image for JARVIS Face Recognition
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

def create_test_face():
    """Create a simple test face image"""
    # Create a 400x400 image with a face-like pattern
    img = Image.new('RGB', (400, 400), color='peachpuff')
    draw = ImageDraw.Draw(img)
    
    # Draw face circle
    draw.ellipse([50, 50, 350, 350], fill='tan', outline='sienna', width=3)
    
    # Draw eyes
    draw.ellipse([120, 150, 170, 200], fill='darkslategray', outline='black', width=2)
    draw.ellipse([230, 150, 280, 200], fill='darkslategray', outline='black', width=2)
    
    # Draw pupils
    draw.ellipse([135, 165, 155, 185], fill='black')
    draw.ellipse([245, 165, 265, 185], fill='black')
    
    # Draw nose
    draw.polygon([(200, 210), (180, 250), (220, 250)], fill='rosybrown')
    
    # Draw mouth
    draw.arc([140, 260, 260, 320], start=0, end=180, fill='maroon', width=4)
    
    # Draw eyebrows
    draw.arc([110, 120, 180, 140], start=200, end=340, fill='darkslategray', width=3)
    draw.arc([220, 120, 290, 140], start=200, end=340, fill='darkslategray', width=3)
    
    # Save
    output_path = Path(__file__).parent.parent / "data" / "faces" / "test_user.jpg"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    img.save(output_path, quality=95)
    print(f"✅ Test face created: {output_path}")
    print("   This is a synthetic test image for Face Recognition validation")
    print("   For production, replace with actual user photos")
    return output_path

if __name__ == "__main__":
    create_test_face()
