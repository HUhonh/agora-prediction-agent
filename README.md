# Agora Prediction Agent 🏛️

AI Prediction Market Trading Agent on **Arc** — for the [Agora Agents Hackathon](https://agora.thecanteenapp.com/) (Canteen × Circle).

An autonomous AI agent that analyzes Polymarket odds, identifies +EV betting opportunities with Kelly Criterion position sizing, and settles trades on Arc using USDC. Built with Circle's developer stack and ERC-8004 agent identity for onchain reputation.

## RFB 02 — Prediction Market Trader Intelligence

> "Find +EV bets across noisy news, data, and sentiment. Size positions properly."

## Architecture

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│ Polymarket  │───▶│ AI Analysis  │───▶│ Execution   │
│ Data Feed   │    │ Engine       │    │ on Arc      │
└─────────────┘    └──────────────┘    └─────────────┘
                         │
                         ▼
                  ┌──────────────┐
                  │ Builder Code │
                  │ Monetization │
                  └──────────────┘
```

## Tech Stack

- **Settlement**: Arc (Circle's stablecoin-native L1)
- **Data**: Polymarket CLOB API
- **Identity**: ERC-8004 Agent NFT
- **Payments**: USDC / CCTP
- **Framework**: Python + Web3

## Quick Start

```bash
pip install -r requirements.txt
python agent.py
```

## Author

- GitHub: [HUhonh](https://github.com/HUhonh)
- X: [@huhongshan8](https://x.com/huhongshan8)
- Discord: @klortoy

## License

MIT
