"""
JARVIS 5.0 - Vision-Language Model (VQA)
=========================================
Sprint 3: Multimodal BÃ¡sico
Vision Question Answering using Gemini Vision API

USAGE: from src.core.vision_language_model import VisionQA
"""

import sys
import os
from pathlib import Path
import logging
from typing import Optional, List, Dict

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add project root
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from PIL import Image

    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    logger.warning("PIL not available")

try:
    import google.generativeai as genai

    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    logger.warning("Google GenAI not available")


class VisionQA:
    """
    Vision Question Answering system using Gemini Vision

    Capabilities:
    - analyze_screenshot: Answer questions about images
    - describe_scene: Generate detailed scene descriptions
    - compare_images: Find differences between two images
    - detect_objects: List objects in image
    - read_text: OCR functionality
    """

    def __init__(self, api_key: Optional[str] = None, model="gemini-2.0-flash-exp"):
        """
        Args:
            api_key: Google API key (or from environment)
            model: Gemini model to use
        """
        self.model_name = model
        self.model = None

        if not GENAI_AVAILABLE:
            logger.error("Google GenAI not available")
            return

        # Get API key
        if api_key:
            self.api_key = api_key
        else:
            self.api_key = os.getenv("GEMINI_API_KEY")

        if not self.api_key:
            logger.warning(
                "âš ï¸ No Gemini API key provided - Vision QA will operate in LOCAL mode only."
            )
            return  # Local reasoning handled in analyze_screenshot() fallback

        # Configure GenAI
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(model)
            logger.info(f"âœ… Vision QA initialized ({model})")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {e}")

    def _load_image(self, image_path: str) -> Optional[Image.Image]:
        """Load image from path"""
        if not PIL_AVAILABLE:
            return None

        try:
            return Image.open(image_path)
        except Exception as e:
            logger.error(f"Failed to load image: {e}")
            return None

    def analyze_screenshot(self, image_path: str, question: str) -> Optional[str]:
        """
        Answer question about an image (uses Gemini if available, otherwise local VisionSystem)
        """
        # Try Gemini if model is loaded and key is present
        if self.model and self.api_key:
            try:
                image = self._load_image(image_path)
                if image:
                    response = self.model.generate_content([question, image])
                    return response.text.strip()
            except Exception as e:
                logger.warning(f"VQA Gemini error: {e}. Falling back to Local Vision.")

        # FALLBACK: Local Vision Intelligence
        try:
            from src.core.vision.vision_system import vision_system
            from src.core.intelligence.local_brain import local_brain

            # 1. Get OCR and Object detection data
            ocr_text = vision_system.extract_text_cached(image_path)
            # YOLO results (simplified for LLM)
            objects = vision_system.detect_ui_elements(image_path)
            obj_list = [f"{obj['label']} at {obj['box']}" for obj in objects[:10]]

            # 2. Ask local brain to reason about the data
            prompt = f"""Use the following image data to answer the question.
Question: {question}

OCR Text found: {ocr_text[:1000]}
Objects detected: {', '.join(obj_list)}

Answer JSON-style or as a direct natural response as JARVIS."""

            return local_brain.generate_response(
                prompt,
                system_prompt="You are JARVIS. Use provided vision data to help the user.",
            )

        except Exception as e:
            logger.error(f"Local VQA fallback failed: {e}")
            return "William, desculpe, meu sistema de visÃ£o local falhou ao analisar esta imagem."

    def describe_scene(
        self, image_path: str, detail_level: str = "normal"
    ) -> Optional[str]:
        """
        Generate detailed scene description

        Args:
            image_path: Path to image
            detail_level: 'brief', 'normal', or 'detailed'

        Returns:
            Scene description
        """
        if not self.model:
            return None

        # Craft prompt based on detail level
        prompts = {
            "brief": "Describe this image in one sentence.",
            "normal": "Describe what you see in this image in detail.",
            "detailed": "Provide a comprehensive description of this image, including objects, colors, layout, text, and any notable features.",
        }

        prompt = prompts.get(detail_level, prompts["normal"])

        image = self._load_image(image_path)
        if not image:
            return None

        try:
            response = self.model.generate_content([prompt, image])
            return response.text.strip()
        except Exception as e:
            logger.error(f"Scene description error: {e}")
            return None

    def compare_images(self, image1_path: str, image2_path: str) -> Optional[str]:
        """
        Compare two images and find differences

        Args:
            image1_path: First image
            image2_path: Second image

        Returns:
            Comparison text describing differences
        """
        if not self.model:
            return None

        image1 = self._load_image(image1_path)
        image2 = self._load_image(image2_path)

        if not image1 or not image2:
            return None

        prompt = "Compare these two images and describe any differences you find. Be specific about what changed."

        try:
            response = self.model.generate_content([prompt, image1, image2])
            return response.text.strip()
        except Exception as e:
            logger.error(f"Image comparison error: {e}")
            return None

    def detect_objects(self, image_path: str) -> Optional[List[str]]:
        """
        Detect and list objects in image

        Args:
            image_path: Path to image

        Returns:
            List of detected objects
        """
        if not self.model:
            return None

        image = self._load_image(image_path)
        if not image:
            return None

        prompt = "List all objects, UI elements, and notable features you see in this image. Provide a comma-separated list."

        try:
            response = self.model.generate_content([prompt, image])
            text = response.text.strip()

            # Parse comma-separated list
            objects = [obj.strip() for obj in text.split(",")]
            return objects
        except Exception as e:
            logger.error(f"Object detection error: {e}")
            return None

    def read_text(self, image_path: str) -> Optional[str]:
        """
        Extract text from image (OCR)

        Args:
            image_path: Path to image

        Returns:
            Extracted text
        """
        if not self.model:
            return None

        image = self._load_image(image_path)
        if not image:
            return None

        prompt = "Extract and transcribe all text visible in this image. Include text from buttons, labels, menus, and any other textual content."

        try:
            response = self.model.generate_content([prompt, image])
            return response.text.strip()
        except Exception as e:
            logger.error(f"Text extraction error: {e}")
            return None

    def identify_ui_element(self, image_path: str, query: str) -> Optional[str]:
        """
        Identify specific UI element location or properties

        Args:
            image_path: Path to screenshot
            query: What to find (e.g., "Where is the Save button?")

        Returns:
            Description of element location/properties
        """
        if not self.model:
            return None

        image = self._load_image(image_path)
        if not image:
            return None

        prompt = f"In this UI screenshot: {query} Describe its location and appearance."

        try:
            response = self.model.generate_content([prompt, image])
            return response.text.strip()
        except Exception as e:
            logger.error(f"UI identification error: {e}")
            return None

    def analyze_chart(self, image_path: str) -> Optional[Dict[str, str]]:
        """
        Analyze chart/graph in image

        Args:
            image_path: Path to chart image

        Returns:
            Dict with chart analysis
        """
        if not self.model:
            return None

        image = self._load_image(image_path)
        if not image:
            return None

        prompt = """Analyze this chart/graph and provide:
1. Type of chart (bar, line, pie, etc)
2. Main trend or insight
3. Key data points
4. Axes labels if present
Format as: Type: ..., Trend: ..., Data: ..., Axes: ..."""

        try:
            response = self.model.generate_content([prompt, image])
            text = response.text.strip()

            # Parse response
            analysis = {}
            for line in text.split("\n"):
                if ":" in line:
                    key, value = line.split(":", 1)
                    analysis[key.strip().lower()] = value.strip()

            return analysis
        except Exception as e:
            logger.error(f"Chart analysis error: {e}")
            return None


# Example usage
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Vision QA")
    parser.add_argument("--image", type=str, required=True, help="Path to image")
    parser.add_argument("--question", type=str, help="Question about image")
    parser.add_argument("--describe", action="store_true", help="Describe scene")
    parser.add_argument("--objects", action="store_true", help="Detect objects")
    parser.add_argument("--text", action="store_true", help="Extract text")
    parser.add_argument("--api-key", type=str, help="Gemini API key")

    args = parser.parse_args()

    # Create VQA
    vqa = VisionQA(api_key=args.api_key)

    if not vqa.model:
        print("âŒ Failed to initialize Vision QA")
        sys.exit(1)

    # Execute requested action
    if args.question:
        print(f"\nâ“ Question: {args.question}")
        answer = vqa.analyze_screenshot(args.image, args.question)
        print(f"ðŸ’¡ Answer: {answer}")

    elif args.describe:
        print("\nðŸ–¼ï¸  Describing scene...")
        description = vqa.describe_scene(args.image, detail_level="detailed")
        print(f"ðŸ“ Description:\n{description}")

    elif args.objects:
        print("\nðŸ” Detecting objects...")
        objects = vqa.detect_objects(args.image)
        if objects:
            print(f"ðŸ“¦ Found {len(objects)} objects:")
            for obj in objects:
                print(f"  - {obj}")

    elif args.text:
        print("\nðŸ“„ Extracting text...")
        text = vqa.read_text(args.image)
        print(f"ðŸ“ Text:\n{text}")

    else:
        print(
            "âŒ Please specify an action: --question, --describe, --objects, or --text"
        )
