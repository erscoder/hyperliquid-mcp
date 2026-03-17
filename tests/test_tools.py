"""Tests for hyperliquid-mcp tools."""
import pytest
from unittest.mock import MagicMock
from hyperliquid_mcp.client import HyperliquidClient
from hyperliquid_mcp.tools.market import get_all_mids, get_orderbook, get_meta, get_candles
from hyperliquid_mcp.tools.account import get_user_state, get_open_orders, get_fills
from hyperliquid_mcp.tools.funding import get_funding_history


@pytest.fixture
def mock_client():
    client = MagicMock()
    client.address = "0xTestAddress"
    client.info = MagicMock()
    return client


def test_get_all_mids(mock_client):
    mock_client.info.all_mids.return_value = {"BTC": "50000", "ETH": "3000", "SOL": "150"}
    result = get_all_mids(mock_client)
    assert result["count"] == 3
    assert "BTC" in result["mids"]


def test_get_orderbook(mock_client):
    mock_client.info.l2_snapshot.return_value = {
        "levels": [
            [{"px": "49990", "sz": "0.5"}, {"px": "49980", "sz": "1.0"}],
            [{"px": "50010", "sz": "0.3"}, {"px": "50020", "sz": "0.8"}],
        ]
    }
    result = get_orderbook(mock_client, "btc", depth=2)
    assert result["coin"] == "BTC"
    assert len(result["bids"]) == 2
    assert len(result["asks"]) == 2
    assert result["bids"][0]["price"] == 49990.0
    assert result["asks"][0]["price"] == 50010.0
    assert result["spread"] == pytest.approx(20.0)
    assert result["mid"] == pytest.approx(50000.0)


def test_get_orderbook_empty(mock_client):
    mock_client.info.l2_snapshot.return_value = {"levels": [[], []]}
    result = get_orderbook(mock_client, "BTC")
    assert result["bids"] == []
    assert result["asks"] == []
    assert result["mid"] is None
    assert result["spread"] is None


def test_get_meta(mock_client):
    mock_client.info.meta.return_value = {
        "universe": [
            {"name": "BTC", "szDecimals": 5, "maxLeverage": 50},
            {"name": "ETH", "szDecimals": 4, "maxLeverage": 50},
        ]
    }
    result = get_meta(mock_client)
    assert result["count"] == 2
    assert result["markets"][0]["name"] == "BTC"
    assert result["markets"][0]["max_leverage"] == 50


def test_get_candles(mock_client):
    mock_client.info.candles_snapshot.return_value = [
        {"t": 1700000000000, "o": "49000", "h": "51000", "l": "48000", "c": "50000", "v": "100"},
    ]
    result = get_candles(mock_client, "btc", "1h", 1)
    assert result["coin"] == "BTC"
    assert result["interval"] == "1h"
    assert result["count"] == 1
    assert result["candles"][0]["open"] == 49000.0
    assert result["candles"][0]["close"] == 50000.0


def test_get_user_state(mock_client):
    mock_client.info.user_state.return_value = {
        "marginSummary": {"accountValue": "10000", "totalMarginUsed": "500", "totalNtlPos": "5000"},
        "withdrawable": "9500",
        "assetPositions": [{"position": {
            "coin": "BTC", "szi": "0.1", "entryPx": "48000",
            "leverage": {"value": 10}, "unrealizedPnl": "200",
            "liquidationPx": "40000", "marginUsed": "480"
        }}],
    }
    result = get_user_state(mock_client)
    assert result["account_value"] == 10000.0
    assert result["positions_count"] == 1
    assert result["positions"][0]["coin"] == "BTC"
    assert result["positions"][0]["side"] == "long"


def test_get_user_state_no_address():
    client = MagicMock(spec=HyperliquidClient)
    client.address = None
    with pytest.raises(ValueError, match="Wallet address required"):
        get_user_state(client)


def test_get_open_orders(mock_client):
    mock_client.info.open_orders.return_value = [
        {"oid": 123, "coin": "ETH", "side": "B", "limitPx": "3000",
         "sz": "0.5", "origSz": "1.0", "orderType": "Limit", "timestamp": 1700000000},
    ]
    result = get_open_orders(mock_client)
    assert result["count"] == 1
    assert result["orders"][0]["coin"] == "ETH"
    assert result["orders"][0]["limit_px"] == 3000.0


def test_get_fills(mock_client):
    mock_client.info.user_fills.return_value = [
        {"coin": "BTC", "side": "B", "px": "50000", "sz": "0.1",
         "fee": "2.5", "closedPnl": "0", "time": 1700000000, "oid": 456},
    ]
    result = get_fills(mock_client, limit=10)
    assert result["count"] == 1
    assert result["fills"][0]["price"] == 50000.0
    assert result["fills"][0]["coin"] == "BTC"


def test_get_funding_history(mock_client):
    mock_client.info.funding_history.return_value = [
        {"time": 1700000000000, "fundingRate": "0.0001", "premium": "0.00005"},
        {"time": 1700028800000, "fundingRate": "0.00015", "premium": "0.00008"},
    ]
    result = get_funding_history(mock_client, "BTC", days=1)
    assert result["coin"] == "BTC"
    assert result["count"] == 2
    assert result["avg_funding_rate"] == pytest.approx(0.000125)
    assert result["annualized_pct"] > 0
