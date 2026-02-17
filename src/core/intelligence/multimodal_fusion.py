"""
JARVIS 5.0 - Multimodal Fusion System
======================================
Sprint 3: Multimodal BÃ¡sico
Late fusion de contextos: texto + imagem + Ã¡udio

USAGE: from src.core.multimodal_fusion import MultimodalFusion
"""

import sys
from pathlib import Path
try:
    import numpy as np

    NUMPY_AVAILABLE = True
except (ImportError, OSError):
    NUMPY_AVAILABLE = False

    class MockNumpy:
        ndarray = type("ndarray", (), {})

    np = MockNumpy()
import logging
from typing import Optional, Dict, List, Tuple

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add project root
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from sentence_transformers import SentenceTransformer

    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logger.warning("sentence-transformers not available")


class MultimodalFusion:
    """
    Late fusion multimodal system

    Combines embeddings from:
    - Text: Jina Embeddings v3 (1024-dim)
    - Vision: Gemini Vision output â†’ embed as text
    - Audio: Emotion scores as weights

    Fusion strategy: Weighted average
    - Text: 50%
    - Image: 35%
    - Audio: 15%
    """

    def __init__(
        self, embedding_model="paraphrase-multilingual-MiniLM-L12-v2", embedding_dim=384
    ):
        """
        Args:
            embedding_model: Model for text embeddings
            embedding_dim: Embedding dimension
        """
        self.embedding_dim = embedding_dim
        self.embedding_model = None

        # Default weights
        self.weights = {"text": 0.50, "image": 0.35, "audio": 0.15}

        # Load embedding model
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                logger.info(f"Loading Multimodal Fusion model: {embedding_model}")
                self.embedding_model = SentenceTransformer(embedding_model)
                logger.info(f"âœ… Multimodal Fusion initialized ({embedding_model})")
            except Exception as e:
                logger.warning(f"Failed to load primary model {embedding_model}: {e}")
                try:
                    alt_model = "jinaai/jina-embeddings-v3"
                    self.embedding_model = SentenceTransformer(
                        alt_model, trust_remote_code=True
                    )
                    self.embedding_dim = 1024
                    logger.info(
                        f"âœ… Multimodal Fusion loaded with fallback: {alt_model}"
                    )
                except Exception as e2:
                    logger.error(f"âŒ All multimodal embedding models failed: {e2}")
        else:
            logger.error("sentence-transformers not available")

    def embed_text(self, text: str) -> Optional[np.ndarray]:
        """
        Embed text using Jina v3

        Args:
            text: Input text

        Returns:
            Embedding vector (1024-dim)
        """
        if not self.embedding_model:
            return None

        try:
            embedding = self.embedding_model.encode(text, normalize_embeddings=True)
            return embedding
        except Exception as e:
            logger.error(f"Text embedding error: {e}")
            return None

    def embed_image_description(self, image_description: str) -> Optional[np.ndarray]:
        """
        Embed image via text description

        Args:
            image_description: Text description from Gemini Vision

        Returns:
            Embedding vector (1024-dim)
        """
        # Same as text embedding
        return self.embed_text(image_description)

    def normalize_audio_emotion(self, emotion_scores: Dict[str, float]) -> np.ndarray:
        """
        Convert emotion scores to embedding weight modifier

        Args:
            emotion_scores: Dict of emotion -> confidence

        Returns:
            Weight modifier (1-dim, normalized 0-1)
        """
        # Use max confidence as weight
        if not emotion_scores:
            return np.array([0.5])  # Neutral

        max_confidence = max(emotion_scores.values())
        return np.array([max_confidence])

    def fuse_contexts(
        self,
        text: Optional[str] = None,
        image_description: Optional[str] = None,
        audio_emotion: Optional[Dict[str, float]] = None,
        custom_weights: Optional[Dict[str, float]] = None,
    ) -> Optional[np.ndarray]:
        """
        Fuse multimodal contexts into single embedding

        Args:
            text: Text input
            image_description: Image description from VQA
            audio_emotion: Emotion scores from audio
            custom_weights: Override default weights

        Returns:
            Fused embedding (1024-dim)
        """
        if not self.embedding_model:
            return None

        # Use custom weights if provided
        weights = custom_weights or self.weights

        # Collect embeddings
        embeddings = []
        active_weights = []

        # Text modality
        if text:
            text_emb = self.embed_text(text)
            if text_emb is not None:
                embeddings.append(text_emb)
                active_weights.append(weights["text"])

        # Image modality
        if image_description:
            image_emb = self.embed_image_description(image_description)
            if image_emb is not None:
                embeddings.append(image_emb)
                active_weights.append(weights["image"])

        # Audio modality (apply emotion as weight modifier)
        if audio_emotion:
            audio_weight_mod = self.normalize_audio_emotion(audio_emotion)[0]
            # Modulate existing weights by emotion
            active_weights = [
                w * (0.5 + 0.5 * audio_weight_mod) for w in active_weights
            ]

        if not embeddings:
            logger.warning("No valid embeddings to fuse")
            return None

        # Normalize weights
        total_weight = sum(active_weights)
        if total_weight == 0:
            return None

        normalized_weights = [w / total_weight for w in active_weights]

        # Weighted average fusion
        fused_embedding = np.zeros(self.embedding_dim)
        for emb, weight in zip(embeddings, normalized_weights):
            fused_embedding += emb * weight

        # Normalize final embedding
        norm = np.linalg.norm(fused_embedding)
        if norm > 0:
            fused_embedding /= norm

        logger.debug(
            f"Fused {len(embeddings)} modalities with weights {normalized_weights}"
        )

        return fused_embedding

    def similarity(self, emb1: np.ndarray, emb2: np.ndarray) -> float:
        """
        Cosine similarity between embeddings

        Args:
            emb1: First embedding
            emb2: Second embedding

        Returns:
            Similarity score (0-1)
        """
        return np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))

    def rank_by_similarity(
        self,
        query_embedding: np.ndarray,
        candidate_embeddings: List[np.ndarray],
        top_k: int = 5,
    ) -> List[Tuple[int, float]]:
        """
        Rank candidates by similarity to query

        Args:
            query_embedding: Query embedding
            candidate_embeddings: List of candidate embeddings
            top_k: Number of top results

        Returns:
            List of (index, similarity) tuples
        """
        similarities = []
        for idx, candidate_emb in enumerate(candidate_embeddings):
            sim = self.similarity(query_embedding, candidate_emb)
            similarities.append((idx, sim))

        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)

        return similarities[:top_k]

    def adaptive_fusion(
        self,
        text: Optional[str] = None,
        image_description: Optional[str] = None,
        audio_emotion: Optional[Dict[str, float]] = None,
        context: str = "general",
    ) -> Optional[np.ndarray]:
        """
        Adaptive fusion with context-specific weights

        Args:
            text: Text input
            image_description: Image description
            audio_emotion: Audio emotion scores
            context: Context type ('search', 'conversation', 'document', 'general')

        Returns:
            Fused embedding
        """
        # Context-specific weights
        context_weights = {
            "search": {"text": 0.70, "image": 0.20, "audio": 0.10},  # Prioritize text
            "conversation": {"text": 0.40, "image": 0.30, "audio": 0.30},  # Balanced
            "document": {"text": 0.80, "image": 0.15, "audio": 0.05},  # Heavy text
            "vision": {"text": 0.20, "image": 0.70, "audio": 0.10},  # Prioritize vision
            "general": {"text": 0.50, "image": 0.35, "audio": 0.15},  # Default
        }

        weights = context_weights.get(context, context_weights["general"])

        return self.fuse_contexts(
            text, image_description, audio_emotion, custom_weights=weights
        )


# Example usage
if __name__ == "__main__":
    # Create fusion system
    fusion = MultimodalFusion()

    if not fusion.embedding_model:
        print("âŒ Failed to initialize multimodal fusion")
        sys.exit(1)

    print("\nðŸ”® Multimodal Fusion - Examples")
    print("=" * 70)

    # Example 1: Text only
    print("\n1ï¸âƒ£  Text only:")
    text_emb = fusion.fuse_contexts(text="Como estÃ¡ o clima hoje?")
    if text_emb is not None:
        print(f"   Embedding shape: {text_emb.shape}")
        print(f"   Norm: {np.linalg.norm(text_emb):.4f}")

    # Example 2: Text + Image
    print("\n2ï¸âƒ£  Text + Image description:")
    multimodal_emb = fusion.fuse_contexts(
        text="Mostre grÃ¡fico de vendas",
        image_description="A bar chart showing sales data with increasing trend from January to December",
    )
    if multimodal_emb is not None:
        print(f"   Embedding shape: {multimodal_emb.shape}")
        print(
            f"   Similarity to text-only: {fusion.similarity(text_emb, multimodal_emb):.4f}"
        )

    # Example 3: Text + Image + Audio
    print("\n3ï¸âƒ£  Text + Image + Audio emotion:")
    full_multimodal_emb = fusion.fuse_contexts(
        text="Preciso ajuda urgente",
        image_description="Error dialog box with red warning icon",
        audio_emotion={"neutral": 0.1, "angry": 0.7, "fear": 0.2},
    )
    if full_multimodal_emb is not None:
        print(f"   Embedding shape: {full_multimodal_emb.shape}")
        print(
            f"   Similarity to text-only: {fusion.similarity(text_emb, full_multimodal_emb):.4f}"
        )

    # Example 4: Adaptive fusion
    print("\n4ï¸âƒ£  Adaptive fusion (context: search):")
    search_emb = fusion.adaptive_fusion(
        text="Python tutorial",
        image_description="Screenshot of code editor",
        context="search",
    )
    if search_emb is not None:
        print(f"   Embedding shape: {search_emb.shape}")

    print("\nâœ… Multimodal fusion examples complete!")
