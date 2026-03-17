import json
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
load_dotenv()

from .client import HyperliquidClient
from .tools.market import get_all_mids, get_orderbook, get_meta, get_candles
from .tools.account import get_user_state, get_open_orders, get_fills
from .tools.funding import get_funding_history
from .tools.trading import place_order, cancel_order, cancel_all_orders, close_position, set_leverage

mcp = FastMCP("hyperliquid")
client = HyperliquidClient()


@mcp.tool()
def hl_get_all_mids() -> str:
    """Get mid prices for all assets on Hyperliquid."""
    return json.dumps(get_all_mids(client), indent=2)


@mcp.tool()
def hl_get_orderbook(coin: str, depth: int = 10) -> str:
    """
    Get L2 orderbook (bids/asks) for a specific asset.

    Args:
        coin: Asset symbol e.g. BTC, ETH, SOL
        depth: Number of price levels to return (default 10)
    """
    return json.dumps(get_orderbook(client, coin, depth), indent=2)


@mcp.tool()
def hl_get_meta() -> str:
    """Get metadata for all markets: max leverage, tick size, lot size."""
    return json.dumps(get_meta(client), indent=2)


@mcp.tool()
def hl_get_candles(coin: str, interval: str = "1h", limit: int = 50) -> str:
    """
    Get OHLCV candles for a specific asset.

    Args:
        coin: Asset symbol e.g. BTC, ETH, SOL
        interval: 1m, 5m, 15m, 30m, 1h, 4h, 8h, 1d (default 1h)
        limit: Number of candles to return (default 50)
    """
    return json.dumps(get_candles(client, coin, interval, limit), indent=2)


@mcp.tool()
def hl_get_user_state() -> str:
    """
    Get your Hyperliquid account: positions, equity, margin, unrealized PnL.
    Requires HL_WALLET_ADDRESS (read-only) or HL_PRIVATE_KEY (trading) in env.
    """
    return json.dumps(get_user_state(client), indent=2)


@mcp.tool()
def hl_get_open_orders() -> str:
    """
    Get all your open orders on Hyperliquid.
    Requires HL_WALLET_ADDRESS or HL_PRIVATE_KEY in env.
    """
    return json.dumps(get_open_orders(client), indent=2)


@mcp.tool()
def hl_get_fills(limit: int = 50) -> str:
    """
    Get your recent trade history (fills).
    Requires HL_WALLET_ADDRESS or HL_PRIVATE_KEY in env.

    Args:
        limit: Number of recent trades to return (default 50)
    """
    return json.dumps(get_fills(client, limit), indent=2)


@mcp.tool()
def hl_get_funding_history(coin: str, days: int = 7) -> str:
    """
    Get funding rate history for a specific asset.

    Args:
        coin: Asset symbol e.g. BTC, ETH, SOL
        days: Number of days of history (default 7)
    """
    return json.dumps(get_funding_history(client, coin, days), indent=2)

@mcp.tool()
def hl_place_order(coin: str, is_buy: bool, size: float, price: float = None, order_type: str = "limit", reduce_only: bool = False) -> str:
    """
    Place an order on Hyperliquid. Requires HL_PRIVATE_KEY in env.

    Args:
        coin: Asset symbol e.g. BTC, ETH, SOL
        is_buy: True for long/buy, False for short/sell
        size: Position size in coins
        price: Limit price (None for market order)
        order_type: limit or market (default limit)
        reduce_only: Only reduce existing position (default False)
    """
    return json.dumps(place_order(client, coin, is_buy, size, price, order_type, reduce_only), indent=2)


@mcp.tool()
def hl_cancel_order(coin: str, oid: int) -> str:
    """
    Cancel a specific order by order ID. Requires HL_PRIVATE_KEY in env.

    Args:
        coin: Asset symbol e.g. BTC
        oid: Order ID to cancel
    """
    return json.dumps(cancel_order(client, coin, oid), indent=2)


@mcp.tool()
def hl_cancel_all_orders(coin: str = None) -> str:
    """
    Cancel all open orders, optionally filtered by coin. Requires HL_PRIVATE_KEY in env.

    Args:
        coin: Optional asset symbol to filter (None cancels all)
    """
    return json.dumps(cancel_all_orders(client, coin), indent=2)


@mcp.tool()
def hl_close_position(coin: str) -> str:
    """
    Close the entire position for a specific asset using a market order. Requires HL_PRIVATE_KEY in env.

    Args:
        coin: Asset symbol e.g. BTC, ETH
    """
    return json.dumps(close_position(client, coin), indent=2)


@mcp.tool()
def hl_set_leverage(coin: str, leverage: int, is_cross: bool = True) -> str:
    """
    Set leverage for a specific asset. Requires HL_PRIVATE_KEY in env.

    Args:
        coin: Asset symbol e.g. BTC, ETH
        leverage: Leverage multiplier e.g. 5, 10, 20
        is_cross: True for cross margin, False for isolated (default True)
    """
    return json.dumps(set_leverage(client, coin, leverage, is_cross), indent=2)


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
