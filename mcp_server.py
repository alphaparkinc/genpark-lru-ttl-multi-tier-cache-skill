"""MCP Stdio Server for LRU TTL Multi-Tier Cache.
100% Python Standard Library.
"""
import sys
import json
from client import LRUTTLCache

cache = LRUTTLCache()

def handle_rpc(line):
    try:
        req = json.loads(line)
    except Exception:
        return
    req_id = req.get("id")
    method = req.get("method")
    params = req.get("params", {})

    if method == "initialize":
        res = {
            "protocolVersion": "2024-11-05",
            "serverInfo": {"name": "genpark-lru-ttl-multi-tier-cache-skill", "version": "1.0.1"},
            "capabilities": {"tools": {}}
        }
        send_response(req_id, res)
    elif method == "tools/list":
        tools = [
            {
                "name": "set",
                "description": "Store value in cache with optional per-key TTL",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "key": {"type": "string"},
                        "value": {},
                        "ttl_seconds": {"type": "number"}
                    },
                    "required": ["key", "value"]
                }
            },
            {
                "name": "get",
                "description": "Retrieve value from cache updating LRU order and checking expiration",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "key": {"type": "string"}
                    },
                    "required": ["key"]
                }
            },
            {
                "name": "evict",
                "description": "Explicitly remove a cached entry",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "key": {"type": "string"}
                    },
                    "required": ["key"]
                }
            },
            {
                "name": "get_stats",
                "description": "Retrieve cache hit ratio, eviction counts, and size telemetry",
                "inputSchema": {"type": "object"}
            },
            {
                "name": "clear",
                "description": "Purge all entries from cache",
                "inputSchema": {"type": "object"}
            }
        ]
        send_response(req_id, {"tools": tools})
    elif method == "tools/call":
        name = params.get("name")
        args = params.get("arguments", {})
        if name == "set":
            out = cache.set(args.get("key"), args.get("value"), args.get("ttl_seconds"))
        elif name == "get":
            out = cache.get(args.get("key", ""))
        elif name == "evict":
            out = {"key": args.get("key"), "evicted": cache.evict(args.get("key", ""))}
        elif name == "get_stats":
            out = cache.get_stats()
        elif name == "clear":
            cache.clear()
            out = {"status": "cleared"}
        else:
            send_error(req_id, -32601, f"Unknown tool: {name}")
            return
        send_response(req_id, {"content": [{"type": "text", "text": json.dumps(out, indent=2)}]})

def send_response(req_id, result):
    sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": req_id, "result": result}) + "\n")
    sys.stdout.flush()

def send_error(req_id, code, message):
    sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}) + "\n")
    sys.stdout.flush()

def main():
    for line in sys.stdin:
        if line.strip():
            handle_rpc(line.strip())

if __name__ == "__main__":
    main()
