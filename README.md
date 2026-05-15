# Agora Prediction Agent 🏛️

AI Prediction Market Trading Agent on **Arc** — [Agora Agents Hackathon](https://agora.thecanteenapp.com/) (Canteen × Circle)

**RFB 02 — Prediction Market Trader Intelligence**

> *"Find +EV bets across noisy news, data, and sentiment. Size positions properly."*

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

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Settlement | Arc (Circle L1) + Polygon |
| Data | Binance WS + Chainlink Oracle |
| Trading | Polymarket CLOB v2 |
| Strategy | 3-Tier Kelly Criterion |
| Identity | ERC-8004 Agent NFT |
| Monetization | Builder Code (per-fill fee share) |
| Risk | Auto-hedge + Safety Score + Onchain Redeem |

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

## .env 变量说明

| 变量 | 必填 | 说明 |
|------|------|------|
| `POLY_PRIVATE_KEY` | ✅ | Polymarket 钱包私钥 |
| `POLY_FUNDER_ADDRESS` | ✅ | Polymarket 钱包地址 |
| `POLY_BUILDER_API_KEY` | ⬜ | Builder API Key (分成用) |
| `POLY_BUILDER_SECRET` | ⬜ | Builder API Secret |
| `POLY_BUILDER_PASSPHRASE` | ⬜ | Builder API Passphrase |
| `ARC_PRIVATE_KEY` | ⬜ | Arc 测试网私钥 |

## Onchain Records

所有 Agent 活动记录在 Arc 测试网：

- **Agent ID**: 7824-7841 (ERC-8004)
- **Identity**: `0x8004A818BFB912233c491871b3d84c89A494BD9e`
- **Reputation**: `0x8004B663056A597Dffe9eCcC1965A193B7388713`
- **CCTP Bridge**: `0x8FE6B999Dc680CcFDD5Bf7EB0974218be2542DAA`

查看: https://testnet.arcscan.app

## Author

- GitHub: [HUhonh](https://github.com/HUhonh)
- X: [@huhongshan8](https://x.com/huhongshan8)
- Discord: @klortoy

## License

MIT
