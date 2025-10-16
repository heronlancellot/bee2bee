"""
Dual embedding system: NLP + Code-specific embeddings.
"""
from typing import List, Literal, Optional, Tuple
import inflection
import re


class DualEmbedder:
    """
    Generate two types of embeddings:
    1. NLP embeddings (textified code for natural language queries)
    2. Code embeddings (raw code for code-to-code similarity)
    """

    def __init__(
        self,
        provider: Literal["local", "openai"] = "local",
        nlp_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        code_model: str = "jinaai/jina-embeddings-v2-base-code",
        openai_api_key: Optional[str] = None,
    ):
        self.provider = provider

        if provider == "local":
            from sentence_transformers import SentenceTransformer

            print(f"Loading NLP model: {nlp_model}...")
            self.nlp_model = SentenceTransformer(nlp_model)

            print(f"Loading Code model: {code_model}...")
            self.code_model = SentenceTransformer(code_model)

        elif provider == "openai":
            if not openai_api_key:
                raise ValueError("OpenAI API key required when provider='openai'")

            from openai import OpenAI

            self.openai_client = OpenAI(api_key=openai_api_key)
            self.openai_model = nlp_model  # e.g., "text-embedding-3-small"

    def embed_batch(self, chunks: List[dict]) -> List[Tuple[List[float], List[float]]]:
        """
        Generate dual embeddings for a batch of chunks.

        Args:
            chunks: List of dicts with 'code' and metadata

        Returns:
            List of (nlp_embedding, code_embedding) tuples
        """
        # Textify for NLP
        textified = [self._textify(chunk) for chunk in chunks]

        # Raw code for code embeddings
        raw_codes = [chunk["code"] for chunk in chunks]

        if self.provider == "local":
            nlp_embeddings = self.nlp_model.encode(textified, show_progress_bar=False)
            code_embeddings = self.code_model.encode(raw_codes, show_progress_bar=False)

            # Convert to lists
            nlp_embeddings = [emb.tolist() for emb in nlp_embeddings]
            code_embeddings = [emb.tolist() for emb in code_embeddings]

        elif self.provider == "openai":
            nlp_embeddings = self._openai_embed_batch(textified)
            code_embeddings = self._openai_embed_batch(raw_codes)

        return list(zip(nlp_embeddings, code_embeddings))

    def embed_query(self, query: str) -> Tuple[List[float], List[float]]:
        """
        Embed a search query with both models.

        Returns:
            (nlp_embedding, code_embedding)
        """
        if self.provider == "local":
            nlp_emb = self.nlp_model.encode([query], show_progress_bar=False)[0].tolist()
            code_emb = self.code_model.encode([query], show_progress_bar=False)[0].tolist()
        elif self.provider == "openai":
            nlp_emb = self._openai_embed([query])[0]
            code_emb = nlp_emb  # Use same for now

        return nlp_emb, code_emb

    def _textify(self, chunk: dict) -> str:
        """
        Convert code chunk to natural language representation.

        Based on Qdrant's approach:
        - Humanize camelCase/snake_case names
        - Include docstring
        - Describe signature
        - Add context (module, file, struct)
        """
        # Extract fields
        name = chunk.get("name", "unknown")
        chunk_type = chunk.get("chunk_type", "function")
        signature = chunk.get("signature", "")
        docstring = chunk.get("docstring", "")
        file_name = chunk.get("file_path", "").split("/")[-1]
        module = chunk.get("module", "")

        # Humanize names (camelCase → camel case)
        name = inflection.humanize(inflection.underscore(name))
        signature = inflection.humanize(inflection.underscore(signature))

        # Build text
        parts = [f"{chunk_type} {name}"]

        if docstring:
            parts.append(f"that does {docstring}")

        if signature:
            parts.append(f"defined as {signature}")

        parts.append(f"in file {file_name}")

        if module:
            parts.append(f"module {module}")

        text = " ".join(parts)

        # Remove special characters
        text = re.sub(r"[^\w\s]", " ", text)

        # Collapse whitespace
        text = " ".join(text.split())

        return text

    def _openai_embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using OpenAI API."""
        response = self.openai_client.embeddings.create(input=texts, model=self.openai_model)

        return [item.embedding for item in response.data]

    def _openai_embed(self, texts: List[str]) -> List[List[float]]:
        """Single embed call."""
        return self._openai_embed_batch(texts)

    def get_dimensions(self) -> Tuple[int, int]:
        """
        Get embedding dimensions for both models.

        Returns:
            (nlp_dim, code_dim)
        """
        if self.provider == "local":
            nlp_dim = self.nlp_model.get_sentence_embedding_dimension()
            code_dim = self.code_model.get_sentence_embedding_dimension()
        else:
            # OpenAI text-embedding-3-small
            nlp_dim = 1536
            code_dim = 1536

        return nlp_dim, code_dim
