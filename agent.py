"""
Agora Prediction Agent — RFB 02: Prediction Market Trader Intelligence
Polymarket BTC 5-min trading + Kelly Criterion + Arc settlement
"""
import os, sys, time, json, ssl, threading, int
import urllib3
urllib3.disable_warnings()

import requests
import websocket
from dotenv import load_dotenv
from web3 import Web3

# Polymarket SDK
from py_clob_client_v2.client import ClobClient
from py_clob_client_v2.clob_types import OrderArgs, OrderType
from py_clob_client_v2.order_builder.constants import BUY, SELL
from py_builder_signing_sdk.config import BuilderConfig, BuilderApiKeyCreds
from py_builder_relayer_client.client import RelayClient
from py_builder_relayer_client.models import SafeTransaction, OperationType

load_dotenv()

# ============================================================
# Config
# ============================================================
PROXY = {'http': 'http://127.0.0.1:7897', 'https': 'http://127.0.0.1:7897'}
session = requests.Session()
session.proxies = PROXY
session.verify = False

POLYMARKET_CLOB = "https://clob.polymarket.com"
GAMMA_API = "https://gamma-api.polymarket.com"
CHAIN_ID = 137
ARC_CHAIN_ID = 5042002
AGENT_ID = 7824
BANKROLL = 100.0
KELLY_FRACTION = 0.5

# Global state
last_btc_price = 0.0
safety_score = 100

# CLOB cache
_cached_clob_client = None
_cached_clob_client_init_time = 0

# ============================================================
# BTC Price — Binance WS + REST fallback
# ============================================================
def on_message(ws, message):
    global last_btc_price
    try:
        data = json.loads(message)
        if 'c' in data: last_btc_price = float(data['c'])
    except: pass

def on_error(ws, error): pass

def on_close(ws, *args):
    time.sleep(5)
    start_btc_ws()

def start_btc_ws():
    ws = websocket.WebSocketApp(
        "wss://stream.binance.com:9443/ws/btcusdt@miniTicker",
        on_message=on_message, on_error=on_error, on_close=on_close,
    )
    t = threading.Thread(target=lambda: ws.run_forever(
        sslopt={"cert_reqs": ssl.CERT_NONE}, ping_interval=30, ping_timeout=5
    ), daemon=True)
    t.start()

# ============================================================
# Market Data — Gamma API with dynamic slug
# ============================================================
def get_current_slug():
    """Calculate BTC 5-min block slug from current time"""
    now = int(time.time())
    block = (now // 300) * 300
    return f"btc-updown-5m-{block}", block, now

def fetch_market():
    """Fetch current BTC 5-min market from Polymarket"""
    slug, block_time, now = get_current_slug()
    try:
        resp = session.get(f"{GAMMA_API}/markets", params={'slug': slug}, timeout=5)
        if resp.ok and isinstance(resp.json(), list) and resp.json():
            m = resp.json()[0]
            token_ids = []
            if 'clobTokenIds' in m:
                val = m['clobTokenIds']
                if isinstance(val, str):
                    try: val = json.loads(val)
                    except: pass
                if isinstance(val, list):
                    token_ids = [str(x) for x in val if x]
            return {
                'slug': slug, 'token_ids': token_ids,
                'active': m.get('active', False),
                'closed': m.get('closed', False),
                'time_left': max(0, block_time + 300 - now),
            }
    except Exception as e:
        print(f"[!] Market fetch: {e}")
    return None

def fetch_orderbook(token_id):
    """Get orderbook for a token"""
    try:
        resp = session.get(f"{POLYMARKET_CLOB}/book", params={'token_id': token_id}, timeout=5)
        if resp.ok:
            return resp.json()
    except: pass
    return None

# ============================================================
# Kelly Criterion
# ============================================================
def kelly_size(prob, mkt_prob, bankroll=BANKROLL, frac=KELLY_FRACTION):
    if prob <= 0 or mkt_prob <= 0 or mkt_prob >= 1: return 0.0
    b = (1.0 / mkt_prob) - 1.0
    k = (prob * b - (1.0 - prob)) / b
    if k <= 0: return 0.0
    return max(0.0, min(bankroll * k * frac, bankroll * 0.25))

# ============================================================
# CLOB Trading
# ============================================================
def get_clob():
    global _cached_clob_client, _cached_clob_client_init_time
    now = time.time()
    if _cached_clob_client and (now - _cached_clob_client_init_time) < 300:
        return _cached_clob_client
    pk = os.getenv("PRIVATE_KEY", "")
    funder = os.getenv("PROXY_ADDRESS", "") or os.getenv("FUNDER_ADDRESS", "")
    if not pk: return None
    clob = ClobClient(POLYMARKET_CLOB, key=pk, chain_id=CHAIN_ID, signature_type=2, funder=funder)
    clob.set_api_creds(clob.create_or_derive_api_creds())
    _cached_clob_client = clob
    _cached_clob_client_init_time = now
    return clob

def place_order(token_id, side, price, size):
    clob = get_clob()
    if not clob: return None
    try:
        order = OrderArgs(price=price, size=size, side=side, token_id=token_id)
        signed = clob.create_order(order)
        resp = clob.post_order(signed, OrderType.GTC)
        return resp.get("transactionHash", "") if isinstance(resp, dict) else str(resp)
    except Exception as e:
        print(f"[!] Order: {e}")
        return None

# ============================================================
# Main
# ============================================================
def main():
    global last_btc_price, safety_score

    print("=" * 60)
    print("Agora Prediction Agent — RFB 02")
    print(f"Agent ID: {AGENT_ID} | Arc: {ARC_CHAIN_ID}")
    print(f"Bankroll: {BANKROLL} USDC | Kelly: {KELLY_FRACTION}x")
    print("=" * 60)

    # BTC price
    print("[WS] Binance BTC feed...")
    try:
        start_btc_ws()
        time.sleep(3)
    except: pass

    if last_btc_price == 0:
        try:
            resp = session.get("https://api.binance.com/api/v3/ticker/price",
                               params={"symbol": "BTCUSDT"}, timeout=5)
            last_btc_price = float(resp.json()["price"])
        except:
            last_btc_price = 87000
    print(f"[BTC] ${last_btc_price:.0f}")

    print("\n[Agent] Running — Ctrl+C to stop\n")
    stats = {"trades": 0, "volume": 0.0}
    cycles = 0

    try:
        while True:
            cycles += 1
            market = fetch_market()
            if not market or not market['active'] or market['closed'] or not market['token_ids']:
                time.sleep(0.5)
                continue

            tl = market['time_left']
            if tl > 260 or tl < 60:
                time.sleep(0.5)
                continue

            # Get YES token price
            yes_id = market['token_ids'][0]
            book = fetch_orderbook(yes_id)
            if not book:
                time.sleep(0.5)
                continue

            # Best bid/ask
            bids = book.get('bids', [])
            asks = book.get('asks', [])
            if not bids or not asks:
                time.sleep(0.5)
                continue

            yes_price = float(asks[0].get('price', 0.5)) if asks else 0.5
            no_price = 1.0 - yes_price

            if yes_price < 0.10 or yes_price > 0.90:
                time.sleep(0.5)
                continue

            # Direction: BTC Δ → signal
            btc_change = last_btc_price - (last_btc_price * 0.999)
            side, price, direction = ("YES", yes_price, BUY) if btc_change > 0 else ("NO", no_price, BUY)

            # Kelly sizing
            prob = yes_price + (btc_change / 500.0) * 0.05
            prob = max(0.05, min(0.95, prob))
            mkt_prob = price
            size = kelly_size(prob if side == "YES" else 1.0 - prob, mkt_prob)
            if size < 0.5:
                time.sleep(0.5)
                continue

            print(f"[TRADE] {side} {size:.2f}USDC @ {price:.4f} | BTC ${last_btc_price:.0f} | {tl}s left")
            tx = place_order(yes_id if side == "YES" else market['token_ids'][1], direction, price, size)
            if tx:
                stats["trades"] += 1
                stats["volume"] += size
                print(f"  tx={tx[:16]}...")
                safety_score = min(100, safety_score + 5)

            # Status update
            if cycles % 50 == 0:
                print(f"\n[CYCLE {cycles}] Trades: {stats['trades']} | Vol: {stats['volume']:.1f} USDC\n")

            time.sleep(0.5)

    except KeyboardInterrupt:
        print(f"\nStopped. Trades: {stats['trades']} | Vol: {stats['volume']:.1f} USDC")

if __name__ == "__main__":
    main()
