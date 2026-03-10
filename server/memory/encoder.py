import numpy as np

HASH_BITS = 512
MODEL_NAME = "all-MiniLM-L6-v2"


class Encoder:
    """Encodes text to binary SimHash vectors using random projections.

    Embedding dim: 384 (all-MiniLM-L6-v2)
    Hash dim: 512 bits packed into 64 bytes
    Random projection matrix is seeded for reproducibility.
    """

    def __init__(self):
        self._model = None
        self._projections: np.ndarray | None = None

    def load(self):
        if self._model is not None:
            return
        from sentence_transformers import SentenceTransformer

        self._model = SentenceTransformer(MODEL_NAME)
        dim = self._model.get_sentence_embedding_dimension()
        rng = np.random.default_rng(42)
        self._projections = rng.standard_normal((HASH_BITS, dim)).astype(np.float32)

    def hash(self, text: str) -> np.ndarray:
        """Returns a 64-byte binary hash (512 bits) via SimHash."""
        self.load()
        emb = self._model.encode(text, normalize_embeddings=True).astype(np.float32)
        projected = self._projections @ emb  # (512,)
        bits = (projected > 0).astype(np.uint8)
        return np.packbits(bits)  # (64,) bytes


encoder = Encoder()
