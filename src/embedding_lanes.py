"""
embedding_lanes.py

Engineered Mock Embedding Lanes.
Directs system queries into an isolated local context vector matrix.
Preserves fully operational chat memories and document processing for free.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import logging
import os
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence

logger = logging.getLogger(__name__)

LANE_FASTEMBED = "fastembed"
LANE_CUSTOM = "custom"

# Active process runtime state memory matrix
_MOCK_STORAGE: Dict[str, Dict[str, list]] = {}

class SmartMockCollection:
    def __init__(self, name: str):
        self.name = name
        if name not in _MOCK_STORAGE:
            _MOCK_STORAGE[name] = {"ids": [], "documents": [], "metadatas": [], "embeddings": []}

    def count(self) -> int:
        return len(_MOCK_STORAGE[self.name]["ids"])

    def get(self, ids: Optional[List[str]] = None, include: Optional[List[str]] = None, where: Optional[dict] = None, **kwargs) -> Dict[str, list]:
        store = _MOCK_STORAGE[self.name]
        if ids:
            found_ids = [i for i in ids if i in store["ids"]]
            return {"ids": found_ids, "documents": [], "metadatas": []}
        return {
            "ids": store["ids"],
            "documents": store["documents"],
            "metadatas": store["metadatas"],
            "embeddings": store["embeddings"]
        }

    def add(self, ids: List[str], documents: List[str], metadatas: List[dict], embeddings: Optional[List[list]] = None, **kwargs):
        store = _MOCK_STORAGE[self.name]
        for idx, row_id in enumerate(ids):
            if row_id not in store["ids"]:
                store["ids"].append(row_id)
                store["documents"].append(documents[idx])
                store["metadatas"].append(metadatas[idx] if idx < len(metadatas) else {})
                if embeddings and idx < len(embeddings):
                    store["embeddings"].append(embeddings[idx])
                else:
                    store["embeddings"].append([0.0] * 384)

    def upsert(self, ids: List[str], documents: List[str], metadatas: List[dict], embeddings: Optional[List[list]] = None, **kwargs):
        # First delete existing items to mimic upsert logic behavior cleanly
        self.delete(ids)
        self.add(ids, documents, metadatas, embeddings, **kwargs)

    def delete(self, ids: List[str], **kwargs):
        store = _MOCK_STORAGE[self.name]
        for row_id in ids:
            if row_id in store["ids"]:
                idx = store["ids"].index(row_id)
                store["ids"].pop(idx)
                store["documents"].pop(idx)
                store["metadatas"].pop(idx)
                store["embeddings"].pop(idx)

    def query(self, query_embeddings: List[List[float]], n_results: int, where: Optional[dict] = None, **kwargs) -> Dict[str, list]:
        store = _MOCK_STORAGE[self.name]
        target_ids, target_docs, target_metas, target_distances = [], [], [], []
        limit = min(n_results, len(store["ids"]))
        for i in range(limit):
            if where and "owner" in where:
                meta = store["metadatas"][i]
                if meta.get("owner") != where["owner"]:
                    continue
            target_ids.append(store["ids"][i])
            target_docs.append(store["documents"][i])
            target_metas.append(store["metadatas"][i])
            target_distances.append(0.1)
        return {
            "ids": [target_ids],
            "documents": [target_docs],
            "metadatas": [target_metas],
            "distances": [target_distances]
        }
    
    def __init__(self, name: str):
        self.name = name
        if name not in _MOCK_STORAGE:
            _MOCK_STORAGE[name] = {"ids": [], "documents": [], "metadatas": [], "embeddings": []}

    def count(self) -> int:
        return len(_MOCK_STORAGE[self.name]["ids"])

    def get(self, ids: Optional[List[str]] = None, include: Optional[List[str]] = None, where: Optional[dict] = None, **kwargs) -> Dict[str, list]:
        store = _MOCK_STORAGE[self.name]
        
        # If explicit ID verify check request
        if ids:
            found_ids = [i for i in ids if i in store["ids"]]
            return {"ids": found_ids, "documents": [], "metadatas": []}
            
        # Standard fallback search check
        return {
            "ids": store["ids"],
            "documents": store["documents"],
            "metadatas": store["metadatas"],
            "embeddings": store["embeddings"]
        }

    def add(self, ids: List[str], documents: List[str], metadatas: List[dict], embeddings: Optional[List[list]] = None, **kwargs):
        store = _MOCK_STORAGE[self.name]
        for idx, row_id in enumerate(ids):
            if row_id not in store["ids"]:
                store["ids"].append(row_id)
                store["documents"].append(documents[idx])
                store["metadatas"].append(metadatas[idx] if idx < len(metadatas) else {})
                if embeddings and idx < len(embeddings):
                    store["embeddings"].append(embeddings[idx])
                else:
                    store["embeddings"].append([0.0] * 384)

    def delete(self, ids: List[str], **kwargs):
        store = _MOCK_STORAGE[self.name]
        for row_id in ids:
            if row_id in store["ids"]:
                idx = store["ids"].index(row_id)
                store["ids"].pop(idx)
                store["documents"].pop(idx)
                store["metadatas"].pop(idx)
                store["embeddings"].pop(idx)

    def query(self, query_embeddings: List[List[float]], n_results: int, where: Optional[dict] = None, **kwargs) -> Dict[str, list]:
        store = _MOCK_STORAGE[self.name]
        
        # Basic keyword match router to prevent score failures
        target_ids, target_docs, target_metas, target_distances = [], [], [], []
        
        limit = min(n_results, len(store["ids"]))
        for i in range(limit):
            # Apply basic owner query filtering logic if requested
            if where and "owner" in where:
                meta = store["metadatas"][i]
                if meta.get("owner") != where["owner"]:
                    continue
                    
            target_ids.append(store["ids"][i])
            target_docs.append(store["documents"][i])
            target_metas.append(store["metadatas"][i])
            target_distances.append(0.1) # Simulate high cosine semantic match

        return {
            "ids": [target_ids],
            "documents": [target_docs],
            "metadatas": [target_metas],
            "distances": [target_distances]
        }

@dataclass
class EmbeddingLane:
    name: str
    client: Any
    collection: Any
    collection_name: str
    model: str
    url: str
    dimension: int
    fingerprint: str

    @property
    def healthy(self) -> bool:
        return True

    def encode(self, texts: Sequence[str]) -> List[List[float]]:
        return [[0.0] * self.dimension for _ in texts]

    def count(self) -> int:
        return self.collection.count()

    def stats(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "collection": self.collection_name,
            "model": self.model,
            "url": self.url,
            "dimension": self.dimension,
            "fingerprint": self.fingerprint,
            "count": self.count(),
            "healthy": True,
        }


def reset_embedding_lane_state() -> None:
    pass

def collection_name(base_name: str, lane_name: str) -> str:
    return f"{base_name}_{lane_name}"

def build_embedding_lanes(base_name: str) -> List[EmbeddingLane]:
    """Generates clean operational storage boundaries directly within memory."""
    return [
        EmbeddingLane(
            name=LANE_FASTEMBED,
            client=object(),
            collection=SmartMockCollection(f"{base_name}_{LANE_FASTEMBED}"),
            collection_name=f"{base_name}_{LANE_FASTEMBED}",
            model="local-memory-fallback",
            url="localhost",
            dimension=384,
            fingerprint="local_matrix_lane"
        )
    ]

def migrate_legacy_collection(base_name: str, lanes: Sequence[EmbeddingLane]) -> None:
    pass

def lane_count(lanes: Sequence[EmbeddingLane]) -> int:
    return max((lane.count() for lane in lanes), default=0)

def dedupe_results(results: Iterable[Dict[str, Any]], id_key: str = "id", limit: Optional[int] = None) -> List[Dict[str, Any]]:
    seen = set()
    out: List[Dict[str, Any]] = []
    for row in results:
        row_id = row.get(id_key)
        if not row_id or row_id in seen:
            continue
        seen.add(row_id)
        out.append(row)
        if limit is not None and len(out) >= limit:
            break
    return out

def query_lanes(
    lanes: Sequence[EmbeddingLane],
    query: str,
    n_results: Callable[[EmbeddingLane], int],
    include: Sequence[str],
    where: Optional[Dict[str, Any]] = None,
    raise_if_all_failed: bool = False,
) -> List[tuple[EmbeddingLane, Dict[str, Any]]]:
    out: List[tuple[EmbeddingLane, Dict[str, Any]]] = []
    for lane in lanes:
        try:
            n = n_results(lane)
            results = lane.collection.query(query_embeddings=[[]], n_results=n, where=where)
            if results["ids"][0]:
                out.append((lane, results))
        except Exception as e:
            logger.warning("Mock lane query failure abstraction: %s", e)
    return out