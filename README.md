# agora-prediction-agent

Polymarket BTC prediction market trading agent, settled on **Arc** (Circle's L1).

Built for [Agora Agents Hackathon](https://agora.thecanteenapp.com/) RFB 02 — Prediction Market Trader Intelligence.

---

## Settlement Flow (Arc → Polygon → Arc)

```
Polygon (Polymarket)               Arc (Settlement)
─────────────────────              ─────────────────
                                 
  Binance WS → Kelly strategy  →   CCTP Bridge (verified)
         │                         │
         ▼                         ▼
  Polymarket CLOB order        ERC-20 Mint Proof
         │                         │
         ▼                         ▼
  +$0.18 PnL (Live)           arcscan.app/tx/...

  Every trade → 1 ATT token minted on Arc ✅
```

### Trade → Arc Proof

Each Polymarket trade mints an ERC-20 token on Arc as immutable proof:

```
[Arc] TX: https://testnet.arcscan.app/tx/1934e977ac34...
[Arc] TX: https://testnet.arcscan.app/tx/6b69a50e51b4...
[Arc] TX: https://testnet.arcscan.app/tx/9eaf948cb9a8...
[Arc] TX: https://testnet.arcscan.app/tx/a8d51433db4c...
```

---

## Architecture

```
Binance WS ──┐
(BTC price)  │    ┌──────────────┐     ┌─────────────┐
             ├───▶│ Multi-combo  │────▶│ Polymarket  │
Chainlink ───┘    │ strategy     │     │ CLOB v2     │
(oracle)          └──────────────┘     └─────────────┘
                                              │
                              ┌───────────────┘
                              ▼
                    ┌──────────────────┐
                    │ Arc ERC-20 Mint  │  ← 每笔交易铸 ATT
                    │ (onchain proof)  │
                    └──────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │ ERC-8004 Agent   │
                    │ (identity/reputation)│
                    └──────────────────┘
```

---

## Strategy

Multi-combo trading with stop-loss/take-profit:

| Combo | Conditions | Size |
|-------|-----------|------|
| 1 | Time<2min, Price 0.8-0.97, BTC>30 | 3.6 |
| 2 | Time<3min, Price 0.8-0.97, BTC>55 | 3.6 |
| 3 | Time<1min, Price 0.7-0.97, BTC>15 | 3.6 |
| Hedge | Auto-hedge at 0.95 | 1.2 |

---

## Circle Tools Used

| Tool | What for | Proof |
|------|----------|-------|
| USDC | Settlement | Arc wallet balance |
| CCTP | Bridge path | 11 verified transfers |
| ERC-8004 | Agent identity | 11 agents registered |
| ERC-8183 | Job lifecycle | 11 jobs completed |
| ERC-20 Mint | Trade proof | 5+ real-time txs |
| Circle SDK | Wallet setup | SCA wallet created |

All on [testnet.arcscan.app](https://testnet.arcscan.app)

---

## Live Trading

- **Platform**: Polymarket BTC 5-min
- **Trades**: 5+ verified on Arc
- **PnL**: +$0.18 USDC
- **Proof**: Attachments on arcscan

---

## Quick Start

```bash
pip install -r requirements.txt
cp .env.example .env   # fill in keys
python trading_agent.py          # v2 - optimized entry
python trading_agent_v1.py       # v1 - with stop-loss
```

---

## Author

- GitHub: [HUhonh](https://github.com/HUhonh)
- X: [@huhongshan8](https://x.com/huhongshan8)
- Discord: @klortoy

MIT
