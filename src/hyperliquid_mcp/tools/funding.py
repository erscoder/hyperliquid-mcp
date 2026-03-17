"""Funding rate tools."""
import time
from ..client import HyperliquidClient


def get_funding_history(client: HyperliquidClient, coin: str, days: int = 7) -> dict:
    """Get funding rate history for a specific asset."""
    coin = coin.upper()
    now_ms = int(time.time() * 1000)
    start_ms = now_ms - days * 86_400_000
    records = client.info.funding_history(coin, start_ms, now_ms) or []
    rates = [
        {
            "time": r.get("time"),
            "funding_rate": float(r.get("fundingRate") or 0),
            "premium": float(r.get("premium") or 0),
        }
        for r in records
    ]
    avg_rate = sum(r["funding_rate"] for r in rates) / len(rates) if rates else 0
    return {
        "coin": coin,
        "days": days,
        "records": rates,
        "count": len(rates),
        "avg_funding_rate": round(avg_rate, 8),
        "annualized_pct": round(avg_rate * 3 * 365 * 100, 4),
    }
