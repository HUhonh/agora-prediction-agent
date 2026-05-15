# agora-prediction-agent

Polymarket BTC prediction market trading agent, settled on **Arc** (Circle's L1).

Built for [Agora Agents Hackathon](https://agora.thecanteenapp.com/) RFB 02 — Prediction Market Trader Intelligence.

---

## How it works

Uses USDC through Circle's developer stack across the full trade lifecycle:

```
                   CCTP Bridge
     Arc (资金池) ──────────▶ Polygon (交易)
          ▲                       │
          │    CCTP Bridge        │ 盈利
          └───────────────────────┘ 回流

     链上身份 (Arc)
     ├─ ERC-8004 Agent NFT
     ├─ ReputationRegistry (交易记录)
     └─ ValidationRegistry (验证)
```

### Trade flow

1. **Fund** — USDC bridges from Arc to Polygon via CCTP
2. **Trade** — Binance WebSocket BTC price → Kelly sizing → Polymarket CLOB order
3. **Settle** — Profit bridges back from Polygon to Arc via CCTP
4. **Record** — Every trade logged to Arc ERC-8004 Agent for onchain reputation

---

## Architecture

```
Binance WS ──┐
(BTC price)  │    ┌──────────────┐     ┌─────────────┐
             ├───▶│ 3-tier Kelly │────▶│ Polymarket  │
Chainlink ───┘    │ strategy     │     │ CLOB v2     │
(oracle)          └──────────────┘     └─────────────┘
                                              │
                              ┌───────────────┘
                              ▼
                    ┌──────────────────┐
                    │ Polygon redeem   │
                    │ (onchain)        │
                    └──────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │ Arc ERC-8004     │
                    │ (identity/log)   │
                    └──────────────────┘
```

---

## Strategy

3-tier Kelly Criterion based on signal strength:

| Tier | Signal | Kelly | When |
|------|--------|-------|------|
| 3 | > 70 | 1.5x | Large BTC swing |
| 2 | 40-70 | 1x | Normal signal |
| 1 | < 40 | 0.5x | Weak signal |

### Entry rules

1. YES price between 0.10-0.90
2. Time remaining: 1:00-4:20
3. BTC change > $5
4. Safety score > 30

### Auto-hedge

When safety score drops below 50, opens opposite position at 50% size.

---

## Circle tools used

| Tool | What for | Status |
|------|----------|--------|
| USDC | Settlement + gas | ✅ |
| CCTP | Arc ↔ Polygon bridge | ✅ 11 transfers |
| ERC-8004 | Agent identity onchain | ✅ 11 agents |
| ERC-8183 | Job lifecycle (escrow) | ✅ 11 jobs |
| SDK | Wallet + Entity Secret | ✅ |
| Gateway | Cross-chain balance (planned) | 🔮 |

---

## Onchain records (Arc Testnet)

```
IdentityRegistry    0x8004A818...494BD9e   Agent NFTs
ReputationRegistry  0x8004B663...88713    Trade records
TokenMessengerV2    0x8FE6B999...2542DAA   CCTP bridge
AgenticCommerce     0x0747EEf0...e4583     ERC-8183 jobs
```

All on [testnet.arcscan.app](https://testnet.arcscan.app)

---

## Run

```bash
pip install -r requirements.txt
cp .env.example .env   # fill in your keys
python agent.py
```

### Env vars

| Var | Required | For |
|-----|----------|-----|
| `PRIVATE_KEY` | Yes | Polymarket wallet |
| `FUNDER_ADDRESS` / `PROXY_ADDRESS` | Yes | Wallet address |
| `POLY_BUILDER_API_KEY` | Optional | Fee share |
| `POLY_BUILDER_SECRET` | Optional | Fee share |
| `POLY_BUILDER_PASSPHRASE` | Optional | Fee share |

---

## Traction

- **11 agents** registered on Arc (ERC-8004)
- **11 CCTP bridges** completed
- **11 ERC-8183 jobs** completed
- **Live trading** on Polymarket BTC 5-min markets

---

## Links

- Author: [@HUhonh](https://github.com/HUhonh)
- X: [@huhongshan8](https://x.com/huhongshan8)
- Discord: @klortoy

MIT
