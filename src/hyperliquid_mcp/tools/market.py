"""Market data tools — prices, orderbook, candles, metadata."""
import time
from typing import Any
from ..client import HyperliquidClient


def get_all_mids(client: HyperliquidClient) -> dict:
    mids = client.info.all_mids()
    return {"mids": dict(sorted(mids.items())), "count": len(mids)}


def get_orderbook(client: HyperliquidClient, coin: str, depth: int = 10) -> dict:
    coin = coin.upper()
    l2 = client.info.l2_snapshot(coin)
    levels = l2.get("levels", [[], []])
    bids = levels[0][:depth]
    asks = levels[1][:depth]
    mid = spread = None
    if bids and asks:
        best_bid = float(bids[0]["px"])
        best_ask = float(asks[0]["px"])
        spread = round(best_ask - best_bid, 6)
        mid = round((best_bid + best_ask) / 2, 6)
    return {
        "coin": coin,
        "bids": [{"price": float(b["px"]), "size": float(b["sz"])} for b in bids],
        "asks": [{"price": float(a["px"]), "size": float(a["sz"])} for a in asks],
        "mid": mid,
        "spread": spread,
    }


def get_meta(client: HyperliquidClient) -> dict:
    meta = client.info.meta()
    universe = meta.get("universe", [])
    return {
        "markets": [
            {
                "name": m["name"],
                "sz_decimals": m.get("szDecimals"),
                "max_leverage": m.get("maxLeverage"),
                "only_isolated": m.get("onlyIsolated", False),
            }
            for m in universe
        ],
        "count": len(universe),
    }


def get_candles(client: HyperliquidClient, coin: str, interval: str = "1h", limit: int = 50) -> dict:
    coin = coin.upper()
    now_ms = int(time.time() * 1000)
    interval_ms_map = {
        "1m": 60_000, "3m": 180_000, "5m": 300_000,
        "15m": 900_000, "30m": 1_800_000,
        "1h": 3_600_000, "2h": 7_200_000, "4h": 14_400_000,
        "8h": 28_800_000, "12h": 43_200_000,
        "1d": 86_400_000, "3d": 259_200_000, "1w": 604_800_000,
    }
    interval_ms = interval_ms_map.get(interval, 3_600_000)
    start_ms = now_ms - interval_ms * limit
    candles = client.info.candles_snapshot(coin, interval, start_ms, now_ms)
    return {
        "coin": coin,
        "interval": interval,
        "candles": [
            {
                "time": c["t"],
                "open": float(c["o"]),
                "high": float(c["h"]),
                "low": float(c["l"]),
                "close": float(c["c"]),
                "volume": float(c["v"]),
            }
            for c in candles
        ],
        "count": len(candles),
    }
