"""Integration test — real Hyperliquid API via MCP stdio protocol."""
import json
import os
import subprocess
import sys

ENV = {
    **os.environ,
    "PYTHONPATH": str(os.path.dirname(os.path.dirname(__file__)) + "/src"),
    "HL_WALLET_ADDRESS": "0x0000000000000000000000000000000000000001",
}

VENV_PYTHON = os.path.join(os.path.dirname(__file__), "..", ".venv", "bin", "python")


def start_server():
    return subprocess.Popen(
        [VENV_PYTHON, "-m", "hyperliquid_mcp"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=ENV,
    )


def rpc(proc, msg):
    proc.stdin.write(json.dumps(msg) + "\n")
    proc.stdin.flush()
    line = proc.stdout.readline()
    return json.loads(line) if line.strip() else None


def call_tool(proc, tool_id, name, args):
    r = rpc(proc, {"jsonrpc": "2.0", "id": tool_id, "method": "tools/call", "params": {"name": name, "arguments": args}})
    assert r is not None, f"No response for {name}"
    assert "error" not in r, f"Error calling {name}: {r.get('error')}"
    text = r["result"]["content"][0]["text"]
    return json.loads(text)


def main():
    proc = start_server()

    # Handshake
    r = rpc(proc, {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
        "protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "integration-test", "version": "1.0"}
    }})
    assert r["result"]["serverInfo"]["name"] == "hyperliquid"
    print(f"[OK] initialize — server={r['result']['serverInfo']}")

    proc.stdin.write(json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}) + "\n")
    proc.stdin.flush()

    # tools/list
    r = rpc(proc, {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
    tools = r["result"]["tools"]
    assert len(tools) == 13
    print(f"[OK] tools/list — {len(tools)} tools registered")

    # hl_get_all_mids
    d = call_tool(proc, 3, "hl_get_all_mids", {})
    assert d["count"] > 100
    assert "BTC" in d["mids"]
    assert "ETH" in d["mids"]
    print(f"[OK] hl_get_all_mids — {d['count']} assets | BTC={d['mids']['BTC']} ETH={d['mids']['ETH']}")

    # hl_get_orderbook
    d = call_tool(proc, 4, "hl_get_orderbook", {"coin": "BTC", "depth": 5})
    assert d["coin"] == "BTC"
    assert len(d["bids"]) == 5
    assert len(d["asks"]) == 5
    assert d["mid"] > 0
    assert d["spread"] > 0
    print(f"[OK] hl_get_orderbook — mid={d['mid']} spread={d['spread']}")

    # hl_get_candles
    d = call_tool(proc, 5,     "hl_get_candles", {"coin": "ETH", "interval": "1h", "limit": 5})
    assert d["coin"] == "ETH"
    assert d["count"] > 0
    assert d["candles"][0]["open"] > 0
    print(f"[OK] hl_get_candles — {d['count']} candles, last close={d['candles'][-1]['close']}")

    # hl_get_meta
    d = call_tool(proc, 6, "hl_get_meta", {})
    assert d["count"] > 100
    names = [m["name"] for m in d["markets"]]
    assert "BTC" in names
    assert "ETH" in names
    print(f"[OK] hl_get_meta — {d['count']} markets")

    # hl_get_funding_history
    d = call_tool(proc, 7, "hl_get_funding_history", {"coin": "BTC", "days": 1})
    assert d["coin"] == "BTC"
    assert d["count"] > 0
    assert "avg_funding_rate" in d
    assert "annualized_pct" in d
    print(f"[OK] hl_get_funding_history — {d['count']} records, avg={d['avg_funding_rate']}, annualized={d['annualized_pct']}%")

    # hl_get_user_state
    d = call_tool(proc, 8, "hl_get_user_state", {})
    assert "account_value" in d
    assert "positions" in d
    print(f"[OK] hl_get_user_state — equity={d['account_value']} positions={d['positions_count']}")

    # hl_get_open_orders
    d = call_tool(proc, 9, "hl_get_open_orders", {})
    assert "orders" in d
    assert "count" in d
    print(f"[OK] hl_get_open_orders — {d['count']} open orders")

    # hl_get_fills
    d = call_tool(proc, 10, "hl_get_fills", {"limit": 10})
    assert "fills" in d
    assert "count" in d
    print(f"[OK] hl_get_fills — {d['count']} fills")

    proc.terminate()
    print()
    print("ALL INTEGRATION TESTS PASSED")


if __name__ == "__main__":
    main()
