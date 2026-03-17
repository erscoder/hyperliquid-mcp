"""Account tools — positions, equity, open orders, trade history."""
from ..client import HyperliquidClient


def _require_address(client: HyperliquidClient) -> str:
    addr = client.address
    if not addr:
        raise ValueError(
            "Wallet address required. Set HL_WALLET_ADDRESS (read-only) "
            "or HL_PRIVATE_KEY (trading) in your env."
        )
    return addr


def get_user_state(client: HyperliquidClient) -> dict:
    addr = _require_address(client)
    state = client.info.user_state(addr)
    ms = state.get("marginSummary", {})
    positions = []
    for pos in state.get("assetPositions", []):
        p = pos.get("position", {})
        size = float(p.get("szi", 0) or 0)
        if size == 0:
            continue
        positions.append({
            "coin": p.get("coin"),
            "side": "long" if size > 0 else "short",
            "size": abs(size),
            "entry_price": float(p.get("entryPx") or 0),
            "leverage": (p.get("leverage") or {}).get("value"),
            "unrealized_pnl": float(p.get("unrealizedPnl") or 0),
            "liquidation_price": p.get("liquidationPx"),
            "margin_used": float(p.get("marginUsed") or 0),
        })
    return {
        "address": addr,
        "account_value": float(ms.get("accountValue") or 0),
        "total_margin_used": float(ms.get("totalMarginUsed") or 0),
        "total_notional": float(ms.get("totalNtlPos") or 0),
        "withdrawable": float(state.get("withdrawable") or 0),
        "positions": positions,
        "positions_count": len(positions),
    }


def get_open_orders(client: HyperliquidClient) -> dict:
    addr = _require_address(client)
    orders = client.info.open_orders(addr)
    return {
        "address": addr,
        "orders": [
            {
                "oid": o.get("oid"),
                "coin": o.get("coin"),
                "side": o.get("side"),
                "limit_px": float(o.get("limitPx") or 0),
                "sz": float(o.get("sz") or 0),
                "orig_sz": float(o.get("origSz") or 0),
                "order_type": o.get("orderType"),
                "timestamp": o.get("timestamp"),
            }
            for o in orders
        ],
        "count": len(orders),
    }


def get_fills(client: HyperliquidClient, limit: int = 50) -> dict:
    addr = _require_address(client)
    fills = (client.info.user_fills(addr) or [])[:limit]
    return {
        "address": addr,
        "fills": [
            {
                "coin": f.get("coin"),
                "side": f.get("side"),
                "price": float(f.get("px") or 0),
                "size": float(f.get("sz") or 0),
                "fee": float(f.get("fee") or 0),
                "pnl": float(f.get("closedPnl") or 0),
                "timestamp": f.get("time"),
                "order_id": f.get("oid"),
            }
            for f in fills
        ],
        "count": len(fills),
    }
