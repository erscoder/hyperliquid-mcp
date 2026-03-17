"""
Hyperliquid client wrapper.
Handles both read-only (no wallet) and trading (wallet required) modes.
"""
import os
from typing import Optional
from hyperliquid.info import Info
from hyperliquid.exchange import Exchange
import eth_account


class HyperliquidClient:
    """
    Wrapper around Hyperliquid SDK.
    - Read-only mode: no private key needed
    - Trading mode: requires HL_PRIVATE_KEY env var
    """

    def __init__(self):
        self.info = Info(skip_ws=True)
        self._exchange: Optional[Exchange] = None
        self._wallet_address: Optional[str] = None

        private_key = os.getenv("HL_PRIVATE_KEY")
        if private_key:
            try:
                account = eth_account.Account.from_key(private_key)
                self._wallet_address = account.address
                self._exchange = Exchange(account, base_url="https://api.hyperliquid.xyz")
            except Exception as e:
                import sys
                print(f"[hyperliquid-mcp] Warning: failed to init Exchange: {e}", file=sys.stderr)

    @property
    def address(self) -> Optional[str]:
        """Wallet address from HL_PRIVATE_KEY, or HL_WALLET_ADDRESS for read-only."""
        if self._wallet_address:
            return self._wallet_address
        return os.getenv("HL_WALLET_ADDRESS")

    @property
    def exchange(self) -> Exchange:
        if not self._exchange:
            raise RuntimeError(
                "Trading requires HL_PRIVATE_KEY env var. "
                "Set it in your .env file or MCP client config."
            )
        return self._exchange

    def is_trading_enabled(self) -> bool:
        return self._exchange is not None
