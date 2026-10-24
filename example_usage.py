"""Example usage for GenPark LRU TTL Multi-Tier Cache."""
from client import LRUTTLCache

def main():
    cache = LRUTTLCache(capacity=3, default_ttl_seconds=60.0)
    print("Populating cache with prompt responses...")
    cache.set("query:weather", {"temp": 22, "condition": "sunny"})
    cache.set("query:stock", {"symbol": "AAPL", "price": 230})
    cache.set("query:crypto", {"symbol": "BTC", "price": 95000})

    print("Accessing 'query:weather' (Hit):", cache.get("query:weather"))

    print("
Adding 4th item to trigger LRU eviction...")
    cache.set("query:news", {"headline": "AI Milestones"})

    print("Checking 'query:stock' (should be evicted as oldest unaccessed):", cache.get("query:stock"))
    print("
Telemetry Stats:", cache.get_stats())

if __name__ == "__main__":
    main()
