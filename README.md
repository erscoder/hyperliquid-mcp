# 🟢 Hyperliquid MCP

> Control your Hyperliquid perps from Claude (or any MCP client) using natural language.

**"What's my BTC PnL?"** → Claude fetches your positions and answers in seconds.  
**"Buy 0.1 ETH at market"** → Claude places the order via Hyperliquid API.

Built with the [Model Context Protocol](https://modelcontextprotocol.io/) — the open standard for connecting AI to external tools.

---

## ✨ Features

| Tool | Description |
|------|-------------|
| `hl_get_all_mids` | Prices for all assets |
| `hl_get_orderbook` | L2 bids/asks for any asset |
| `hl_get_meta` | Market info (leverage, tick size) |
| `hl_get_candles` | OHLCV history (1m → 1d) |
| `hl_get_user_state` | Positions, equity, margin, PnL |
| `hl_get_open_orders` | Active orders |
| `hl_get_fills` | Trade history |
| `hl_get_funding_history` | Funding rate history |
| `hl_place_order` | Place limit or market orders |
| `hl_cancel_order` | Cancel specific order |
| `hl_cancel_all_orders` | Cancel all orders (optional: by coin) |
| `hl_close_position` | Close entire position |
| `hl_set_leverage` | Set leverage (cross or isolated) |

---

## 🚀 Quick Start

### 1. Install

```bash
pip install hyperliquid-mcp
```

Or run directly without installing:

```bash
uvx hyperliquid-mcp
```

### 2. Configure Claude Desktop

Open `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows) and add:

**Read-only mode** (positions, prices, history — no private key needed):

```json
{
  "mcpServers": {
    "hyperliquid": {
      "command": "uvx",
      "args": ["hyperliquid-mcp"],
      "env": {
        "HL_WALLET_ADDRESS": "0xYourWalletAddressHere"
      }
    }
  }
}
```

**Trading mode** (place orders, cancel, close positions):

```json
{
  "mcpServers": {
    "hyperliquid": {
      "command": "uvx",
      "args": ["hyperliquid-mcp"],
      "env": {
        "HL_PRIVATE_KEY": "0xYourPrivateKeyHere"
      }
    }
  }
}
```

> ⚠️ **Never share your private key.** It stays on your machine — this server runs locally via stdio, no data is sent anywhere except Hyperliquid's official API.

### 3. Restart Claude Desktop and start chatting

```
What are my open positions?
What's the ETH funding rate this week?
Place a limit order to buy 0.5 SOL at $150
```

---

## 🔧 Manual Setup (from source)

```bash
git clone https://github.com/erscoder/hyperliquid-mcp
cd hyperliquid-mcp
pip install -e .
cp .env.example .env
# Edit .env with your wallet address or private key
```

Then in `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "hyperliquid": {
      "command": "python",
      "args": ["-m", "hyperliquid_mcp"],
      "cwd": "/path/to/hyperliquid-mcp",
      "env": {
        "HL_WALLET_ADDRESS": "0xYourWalletAddressHere"
      }
    }
  }
}
```

---

## 🔒 Security

- **Your keys never leave your machine.** The server runs locally via stdio transport.
- **Read-only by default.** Set only `HL_WALLET_ADDRESS` if you don't want trading enabled.
- **Trading requires `HL_PRIVATE_KEY`.** Without it, all trading tools return an error.
- Use a **dedicated trading wallet** with limited funds for extra safety.

---

## 🤖 Use in AI Agents

MCP is not just for chat clients. Use hyperliquid-mcp as the trading layer inside any autonomous agent.

### LangChain / LangGraph

```python
from langchain_mcp_adapters.client import MultiServerMCPClient

client = MultiServerMCPClient({
    "hyperliquid": {
        "command": "uvx",
        "args": ["hyperliquid-mcp"],
        "transport": "stdio",
        "env": {"HL_WALLET_ADDRESS": "0xYourWallet"}
    }
})

tools = await client.get_tools()
# tools now includes hl_get_user_state, hl_get_orderbook, etc.
# Pass them to any LangChain agent or LangGraph node
```

### CrewAI

```python
from crewai import Agent
from crewai_tools import MCPTool

hl_tools = MCPTool.from_server(
    command="uvx",
    args=["hyperliquid-mcp"],
    env={"HL_WALLET_ADDRESS": "0xYourWallet"}
)

trader = Agent(
    role="Trading Analyst",
    goal="Monitor Hyperliquid positions and funding rates",
    tools=hl_tools
)
```

### Custom agent (MCP Python SDK)

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

server_params = StdioServerParameters(
    command="uvx",
    args=["hyperliquid-mcp"],
    env={"HL_WALLET_ADDRESS": "0xYourWallet"}
)

async with stdio_client(server_params) as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()
        result = await session.call_tool("hl_get_user_state", {})
        print(result.content)
```

**Agent ideas:**
- Portfolio monitor that alerts when funding rates spike above threshold
- Risk manager that auto-closes positions when drawdown exceeds limit
- Arbitrage scanner comparing funding across assets
- Morning briefing agent that summarizes overnight PnL and open positions

---

## 💬 Other MCP Clients

Works with any MCP-compatible client:

- **Claude Desktop** — see Quick Start above
- **VS Code** (Copilot) — add to `.vscode/mcp.json`
- **Cursor** — add to MCP settings
- **Continue.dev** — add to config

---

## 📄 License

MIT — free to use, fork, and contribute.

---

## 🌟 Star History

If this saved you time, a ⭐ goes a long way!
