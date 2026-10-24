"""LRU TTL Multi-Tier Cache.
100% Python Standard Library.
"""
import time
from typing import Dict, Any, List, Optional, Tuple

class LRUTTLCache:
    """In-memory LRU cache with per-key TTL expiration and hit/miss telemetry."""
    def __init__(self, capacity: int = 1000, default_ttl_seconds: Optional[float] = None):
        self.capacity = capacity
        self.default_ttl = default_ttl_seconds
        self.data: Dict[str, Tuple[Any, Optional[float]]] = {}
        self.lru_order: List[str] = []
        self.stats = {"hits": 0, "misses": 0, "evictions": 0, "stale_removals": 0}

    def set(self, key: str, value: Any, ttl_seconds: Optional[float] = None) -> Dict[str, Any]:
        now = time.time()
        effective_ttl = ttl_seconds if ttl_seconds is not None else self.default_ttl
        expire_at = (now + effective_ttl) if effective_ttl is not None else None

        if key in self.data:
            self.lru_order.remove(key)
        elif len(self.data) >= self.capacity:
            lru_key = self.lru_order.pop(0)
            del self.data[lru_key]
            self.stats["evictions"] += 1

        self.data[key] = (value, expire_at)
        self.lru_order.append(key)

        return {"status": "stored", "key": key, "has_ttl": expire_at is not None}

    def get(self, key: str) -> Dict[str, Any]:
        now = time.time()
        if key not in self.data:
            self.stats["misses"] += 1
            return {"found": False, "key": key, "value": None}

        val, expire_at = self.data[key]
        if expire_at is not None and now >= expire_at:
            del self.data[key]
            self.lru_order.remove(key)
            self.stats["misses"] += 1
            self.stats["stale_removals"] += 1
            return {"found": False, "key": key, "value": None, "expired": True}

        self.lru_order.remove(key)
        self.lru_order.append(key)
        self.stats["hits"] += 1
        return {"found": True, "key": key, "value": val}

    def evict(self, key: str) -> bool:
        if key in self.data:
            del self.data[key]
            self.lru_order.remove(key)
            self.stats["evictions"] += 1
            return True
        return False

    def get_stats(self) -> Dict[str, Any]:
        total_requests = self.stats["hits"] + self.stats["misses"]
        hit_ratio = (self.stats["hits"] / total_requests) if total_requests > 0 else 0.0
        return {
            "capacity": self.capacity,
            "current_size": len(self.data),
            "hits": self.stats["hits"],
            "misses": self.stats["misses"],
            "evictions": self.stats["evictions"],
            "stale_removals": self.stats["stale_removals"],
            "hit_ratio": round(hit_ratio, 4)
        }

    def clear(self) -> None:
        self.data.clear()
        self.lru_order.clear()
