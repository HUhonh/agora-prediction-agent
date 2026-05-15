# Agora Prediction Agent 🏛️

AI Prediction Market Trading Agent on **Arc** — [Agora Agents Hackathon](https://agora.thecanteenapp.com/) (Canteen × Circle)

**RFB 02 — Prediction Market Trader Intelligence**

> *"Find +EV bets across noisy news, data, and sentiment. Size positions properly."*

---

## Settlement Flow (Arc → Polygon → Arc)

评委看重的 *"settled on Arc"* 设计 — USDC 通过 Circle 全栈平台在整个交易生命周期中流转：

```
┌─────────────────────────────────────────────────────────────────────┐
│                        SETTLEMENT ON ARC                            │
│                                                                     │
│  ┌─────────┐    CCTP Bridge    ┌──────────┐    交易盈利             │
│  │  Arc    │ ────────────────▶ │ Polygon  │ ──────────┐            │
│  │ 资金池  │                   │ 交易账户  │            │            │
│  │ (USDC)  │ ◀──────────────── │ (USDC)   │ ◀──────────┘            │
│  └─────────┘    CCTP Bridge    └──────────┘   利润回流               │
│       │                                                             │
│       │ ERC-8004 Agent Identity                                     │
│       ▼                                                             │
│  ┌─────────────────────────────────────────────────────┐            │
│  │  IdentityRegistry  → Agent NFT (onchain identity)   │            │
│  │  ReputationRegistry → Trade performance records     │            │
│  │  ValidationRegistry → Agent verification            │            │
│  └─────────────────────────────────────────────────────┘            │
│                                                                     │
│  Future: Gateway 统一余额 — 跨链 USDC 余额统一管理，               │
│  所有链上的 USDC 看作一个聚合余额，即时跨链支出。                   │
│  Sub-500ms cross-chain transfers, gas-free nanopayments.           │
└─────────────────────────────────────────────────────────────────────┘
```

### 交易生命周期

```
Phase 1: 资金部署 (Arc → Polygon)
  USDC 通过 CCTP TokenMessengerV2 从 Arc 测试网桥接到 Polygon
  TX: https://testnet.arcscan.app

Phase 2: Agent 执行 (Polygon)
  Binance WebSocket BTC 价格 → 三档 Kelly 策略 → Polymarket CLOB 下单
  自动对冲 + 安全分数监控

Phase 3: 利润结算 (Polygon → Arc)
  盈利 USDC 通过 CCTP 从 Polygon 回流 Arc
  Builder Code 分成自动归集

Phase 4: 链上声誉 (Arc)
  每笔交易记录到 ERC-8004 Agent
  ReputationRegistry 记录交易表现
```

---

## Architecture

```
┌─────────────────┐    ┌──────────────┐    ┌─────────────┐
│ Binance WS       │    │              │    │ Polymarket   │
│ (BTC Price)      │───▶│  3-Tier      │───▶│ CLOB v2      │
└─────────────────┘    │  Kelly       │    │ (Order Match)│
                       │  Strategy    │    └─────────────┘
┌─────────────────┐    │              │    ┌─────────────┐
│ Chainlink        │───▶│              │───▶│ Builder Code │
│ Oracle           │    │              │    │ (Fee Share)  │
└─────────────────┘    └──────────────┘    └─────────────┘
                               │
                               ▼
                       ┌──────────────┐
                       │ Polygon      │
                       │ Redeem       │
                       │ (Onchain)    │
                       └──────────────┘
                               │
                               ▼
                       ┌──────────────┐
                       │ Arc          │
                       │ ERC-8004     │
                       │ (Reputation) │
                       └──────────────┘
```

---

## Tech Stack

| Layer | Technology | Status |
|-------|-----------|--------|
| Settlement | Arc (Circle L1) + Polygon | ✅ |
| Bridge | CCTP TokenMessengerV2 | ✅ Deployed |
| Data | Binance WS + Chainlink Oracle | ✅ |
| Trading | Polymarket CLOB v2 | ✅ Live |
| Strategy | 3-Tier Kelly Criterion | ✅ |
| Identity | ERC-8004 Agent NFT | ✅ 11 Agents |
| Monetization | Builder Code (per-fill fee share) | ✅ |
| Risk | Auto-hedge + Safety Score + Onchain Redeem | ✅ |
| Unified Balance | Gateway (planned) | 🔮 Future |

### Circle Tools Used

| Tool | Usage | Proof |
|------|-------|-------|
| **USDC** | 交易结算 + Gas | Faucet claims |
| **CCTP** | Arc ↔ Polygon Bridge | TX on arcscan |
| **ERC-8004** | Agent Identity + Reputation | 11 agents registered |
| **ERC-8183** | Job lifecycle (escrow) | 11 jobs completed |
| **Circle SDK** | Wallet + Entity Secret | SCA wallet created |
| **Gateway** | Planned: unified cross-chain balance | Design doc |

---

## Strategy

### 三档 Kelly 交易策略

| Tier | Signal | Kelly | Description |
|------|--------|-------|-------------|
| 3 | > 70 | 1.5x | 激进 — BTC 大幅波动 |
| 2 | 40-70 | 1.0x | 标准 — 中等信号 |
| 1 | < 40 | 0.5x | 保守 — 弱信号 |

### 多条件进场逻辑

1. **价格过滤**: YES price 0.10-0.90 (避免极端)
2. **时间窗口**: 剩余 1:00-4:20 (避开开盘/收盘)
3. **BTC 波动**: |Δ| > $5 (有信号才交易)
4. **安全分数**: > 30 (风险控制在位)

### 自动对冲

- 安全分数 < 50 → 自动反向开仓 50% 仓位
- 对冲成功后恢复分数 +30

---

## Quick Start

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 填入你的密钥
```

需要申请的服务：

| 服务 | 地址 | 说明 |
|------|------|------|
| Polymarket Builder API | https://developers.polymarket.com | Builder Code 分成 |
| Polymarket CLOB | https://clob.polymarket.com | 交易接口 |

### 3. 运行

```bash
python agent.py
```

---

## .env 变量说明

| 变量 | 必填 | 说明 |
|------|------|------|
| `PRIVATE_KEY` | ✅ | Polymarket 钱包私钥 |
| `FUNDER_ADDRESS` | ✅ | Polymarket 钱包地址 |
| `POLY_BUILDER_API_KEY` | ⬜ | Builder API Key (分成用) |
| `POLY_BUILDER_SECRET` | ⬜ | Builder API Secret |
| `POLY_BUILDER_PASSPHRASE` | ⬜ | Builder API Passphrase |

---

## Onchain Records (Arc Testnet)

所有 Agent 活动记录在 Arc 测试网：

| Contract | Address | Usage |
|----------|---------|-------|
| IdentityRegistry | `0x8004A818...494BD9e` | Agent NFT |
| ReputationRegistry | `0x8004B663...88713` | Trade records |
| ValidationRegistry | `0x8004Cb1B...B4272` | Verification |
| TokenMessengerV2 | `0x8FE6B999...2542DAA` | CCTP Bridge |
| AgenticCommerce | `0x0747EEf0...e4583` | ERC-8183 Jobs |

查看: https://testnet.arcscan.app

---

## Traction

- **Agent IDs**: 7824-7841 (11 registered)
- **CCTP Bridge**: 11 cross-chain transfers completed
- **ERC-8183 Jobs**: 11 completed (create → fund → submit → complete)
- **Real Trading**: Production Polymarket BTC 5-min trading with live funds

---

## Author

- GitHub: [HUhonh](https://github.com/HUhonh)
- X: [@huhongshan8](https://x.com/huhongshan8)
- Discord: @klortoy

## License

MIT
