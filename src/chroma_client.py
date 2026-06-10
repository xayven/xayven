"""
chroma_client.py

Singleton ChromaDB Persistent client.
Runs an embedded instance of ChromaDB locally inside the application layer
to eliminate the need for an external server cluster (100% Free on Render).
"""

import os
import logging
from src.constants import CHROMA_DIR

logger = logging.getLogger(__name__)

_client = None


def get_chroma_client():
    """Get or create the singleton local ChromaDB Persistent client.

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
        # Instead of connecting to an external server via HttpClient, 
        # we boot up a local database instance saved under your app's CHROMA_DIR.
        client = chromadb.PersistentClient(path=CHROMA_DIR)
        
        # Verify health check
        client.heartbeat()
        _client = client
        logger.info(f"ChromaDB local persistent client successfully initialized at: {CHROMA_DIR}")
        return _client
        
    except Exception as e:
        logger.error(f"Failed to initialize local ChromaDB client: {e}")
        raise RuntimeError(f"ChromaDB local initialization failed: {e}") from e


def reset_client():
    """Reset the singleton (e.g. after config change)."""
    global _client
    _client = None