"""
chroma_client.py

Singleton ChromaDB Ephemeral/In-Memory Client.
Provides a local, zero-dependency data runtime inside the application layer.
"""

import logging

logger = logging.getLogger(__name__)

_client = None


def get_chroma_client():
    """Get or create the singleton local ChromaDB Ephemeral client.

    Raises RuntimeError with a clear install hint if the `chromadb` package
    is not installed.
    """
    global _client
    if _client is not None:
        return _client

    try:
        import chromadb
    except ImportError as e:
        raise RuntimeError(
            "ChromaDB integration is not installed. Install the optional "
            "dependency with: pip install chromadb"
        ) from e

    try:
        # We override the default configuration settings manually so the lightweight 
        # http client library accepts running an isolated in-memory sequence.
        from chromadb.config import Settings
        
        client = chromadb.Client(Settings(
            chroma_api_impl="chromadb.api.segment.SegmentAPI",
            is_persistent=False
        ))
        
        client.heartbeat()
        _client = client
        logger.info("ChromaDB local Ephemeral client successfully initialized.")
        return _client
        
    except Exception as e:
        logger.error(f"Failed to initialize local ChromaDB client: {e}")
        raise RuntimeError(f"ChromaDB local initialization failed: {e}") from e


def reset_client():
    """Reset the singleton (e.g. after config change)."""
    global _client
    _client = None