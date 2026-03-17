"""Trading tools — place/cancel orders, close positions, set leverage."""
from ..client import HyperliquidClient


def place_order(
    client: HyperliquidClient,
    coin: str,
    is_buy: bool,
    size: float,
    price: float = None,
    order_type: str = "limit",
    reduce_only: bool = False,
) -> dict:
    """
    Place an order. order_type: 'limit' or 'market'.
    Price required for limit; auto-slipped for market.
    """
    coin = coin.upper()
    ex = client.exchange

    if order_type == "market":
        order_type_obj = {"market": {}}
        if price is None:
            mids = client.info.all_mids()
            mid = float(mids.get(coin, 0))
            price = round(mid * (1.02 if is_buy else 0.98), 6)
    else:
        if price is None:
            raise ValueError("Price is required for limit orders")
        order_type_obj = {"limit": {"tif": "Gtc"}}

    result = ex.order(coin, is_buy, size, price, order_type_obj, reduce_only=reduce_only)
    return {"success": result.get("status") == "ok", "raw": result}


def cancel_order(client: HyperliquidClient, coin: str, oid: int) -> dict:
    """Cancel a specific order by order ID."""
    coin = coin.upper()
    result = client.exchange.cancel(coin, oid)
    return {"success": result.get("status") == "ok", "raw": result}


def cancel_all_orders(client: HyperliquidClient, coin: str = None) -> dict:
    """Cancel all open orders, optionally filtered by coin."""
    open_orders = client.info.open_orders(client.address) or []
    if coin:
        coin = coin.upper()
        open_orders = [o for o in open_orders if o.get("coin") == coin]

    results = []
    for o in open_orders:
        r = client.exchange.cancel(o["coin"], o["oid"])
        results.append({"oid": o["oid"], "coin": o["coin"], "result": r.get("status")})

    return {
        "cancelled": len([r for r in results if r["result"] == "ok"]),
        "total": len(results),
        "details": results,
    }


def close_position(client: HyperliquidClient, coin: str) -> dict:
    """Close the entire position for a specific coin using a market order."""
    coin = coin.upper()
    state = client.info.user_state(client.address)
    for pos in state.get("assetPositions", []):
        p = pos.get("position", {})
        if p.get("coin") == coin:
            size = float(p.get("szi", 0) or 0)
            if size == 0:
                return {"success": False, "message": f"No open position for {coin}"}
            is_buy = size < 0  # close short → buy; close long → sell
            return place_order(client, coin, is_buy, abs(size), order_type="market", reduce_only=True)
    return {"success": False, "message": f"No position found for {coin}"}


def set_leverage(client: HyperliquidClient, coin: str, leverage: int, is_cross: bool = True) -> dict:
    """Set leverage for a specific coin."""
    coin = coin.upper()
    result = client.exchange.update_leverage(leverage, coin, is_cross)
    return {"success": result.get("status") == "ok", "raw": result}