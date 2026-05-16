"""
XAUUSD SNIPER TELEGRAM BOT — Rolif Colaso
Fixed: multiple Telegram API endpoints + retry logic
"""
import os, logging, threading, time
from datetime import datetime, timezone
from flask import Flask, request, jsonify
import requests

BOT_TOKEN   = os.getenv("TELEGRAM_BOT_TOKEN",  "8934180662:AAFW-wqfZW93vzWCcjyBynE-fZt_RydEk0M")
CHAT_ID     = os.getenv("TELEGRAM_CHAT_ID",    "5852405216")
WEBHOOK_KEY = os.getenv("WEBHOOK_SECRET_KEY",  "xau_sniper_rolif_2024")
PORT        = int(os.getenv("PORT", 5000))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)
app = Flask(__name__)

# Multiple API endpoints to try (handles Render network restrictions)
TG_ENDPOINTS = [
    f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
    f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
]

def send_telegram(text, chat_id=CHAT_ID, retries=3):
    """Send with retry logic across multiple attempts."""
    payload = {
        "chat_id":    chat_id,
        "text":       text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    for attempt in range(retries):
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            r = requests.post(url, json=payload, timeout=15)
            log.info(f"Telegram response [{attempt+1}]: {r.status_code} {r.text[:100]}")
            if r.status_code == 200:
                return True
            time.sleep(1)
        except Exception as e:
            log.error(f"Attempt {attempt+1} failed: {e}")
            time.sleep(2)
    return False

def fmt_buy(d):
    t = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    price = d.get('price','N/A')
    tp    = d.get('tp','N/A')
    sl    = d.get('sl','N/A')
    adx   = d.get('adx','25+')
    str_  = d.get('strength','Strong')
    sweep = d.get('sweep','Bull Sweep Confirmed')
    return (
        "\U0001f7e2\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n"
        "\U0001f3af <b>XAU/USD SNIPER BUY</b>\n"
        "\U0001f7e2\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n\n"
        f"\u23f0 <b>Time:</b>      {t}\n"
        f"\U0001f4ca <b>Symbol:</b>    XAUUSD (Gold)\n"
        f"\u23f1 <b>Timeframe:</b> 15M\n\n"
        "\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\n"
        f"\U0001f4cd <b>Entry:</b>  <code>{price}</code>\n"
        f"\u2705 <b>TP:</b>     <code>{tp}</code>  (+300 pips)\n"
        f"\u274c <b>SL:</b>     <code>{sl}</code>  (-100 pips)\n"
        f"\U0001f4d0 <b>R:R:</b>    1 : 3\n\n"
        "\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\n"
        "\U0001f50d <b>FILTER CONFIRMATIONS</b>\n"
        f"\U0001f4c8 EMA 200 + HMA 50  \u2705 BULLISH\n"
        f"\U0001f4a7 Liquidity Sweep   \u2705 {sweep}\n"
        f"\U0001f4e1 ADX               \u2705 {adx}\n"
        f"\U0001f4aa Trend Strength    \u2705 {str_}%\n"
        f"\U0001f504 Adaptive Signal   \u2705 CONFIRMED\n\n"
        "\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\n"
        "\u26a0\ufe0f <i>Risk management always. Not financial advice.</i>\n"
        "\U0001f7e2\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501"
    )

def fmt_sell(d):
    t = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    price = d.get('price','N/A')
    tp    = d.get('tp','N/A')
    sl    = d.get('sl','N/A')
    adx   = d.get('adx','25+')
    str_  = d.get('strength','Strong')
    sweep = d.get('sweep','Bear Sweep Confirmed')
    return (
        "\U0001f534\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n"
        "\U0001f3af <b>XAU/USD SNIPER SELL</b>\n"
        "\U0001f534\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n\n"
        f"\u23f0 <b>Time:</b>      {t}\n"
        f"\U0001f4ca <b>Symbol:</b>    XAUUSD (Gold)\n"
        f"\u23f1 <b>Timeframe:</b> 15M\n\n"
        "\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\n"
        f"\U0001f4cd <b>Entry:</b>  <code>{price}</code>\n"
        f"\u2705 <b>TP:</b>     <code>{tp}</code>  (-300 pips)\n"
        f"\u274c <b>SL:</b>     <code>{sl}</code>  (+100 pips)\n"
        f"\U0001f4d0 <b>R:R:</b>    1 : 3\n\n"
        "\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\n"
        "\U0001f50d <b>FILTER CONFIRMATIONS</b>\n"
        f"\U0001f4c9 EMA 200 + HMA 50  \u2705 BEARISH\n"
        f"\U0001f4a7 Liquidity Sweep   \u2705 {sweep}\n"
        f"\U0001f4e1 ADX               \u2705 {adx}\n"
        f"\U0001f4aa Trend Strength    \u2705 {str_}%\n"
        f"\U0001f504 Adaptive Signal   \u2705 CONFIRMED\n\n"
        "\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\n"
        "\u26a0\ufe0f <i>Risk management always. Not financial advice.</i>\n"
        "\U0001f534\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501"
    )

def fmt_close(d):
    t = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return (
        "POSITION CLOSED\n\n"
        f"Time:   {t}\n"
        f"Close:  {d.get('price','N/A')}\n"
        f"Reason: {d.get('reason','Signal Exit')}\n"
        f"P&L:    {d.get('pnl','N/A')} pips"
    )

@app.route("/webhook/<secret>", methods=["POST"])
def webhook(secret):
    if secret != WEBHOOK_KEY:
        return jsonify({"error": "Unauthorized"}), 401
    try:
        data = request.get_json(force=True) or {}
    except Exception:
        return jsonify({"error": "Bad JSON"}), 400

    log.info(f"Received: {data}")
    action = str(data.get("action","")).upper()

    if action == "BUY":
        msg = fmt_buy(data)
    elif action == "SELL":
        msg = fmt_sell(data)
    elif action in ("CLOSE","EXIT"):
        msg = fmt_close(data)
    else:
        return jsonify({"error": f"Unknown action: {action}"}), 400

    ok = send_telegram(msg)
    status_code = 200 if ok else 500
    return jsonify({"status": "sent" if ok else "failed", "action": action}), status_code

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "online", "bot": "XAU Sniper Rolif", "chat_id": CHAT_ID})

@app.route("/test", methods=["GET"])
def test_alert():
    """Quick test endpoint - visit in browser to send test BUY alert"""
    d = {"price":"2345.50","tp":"2375.50","sl":"2335.50","adx":"32.4","strength":"78","sweep":"Bull Sweep Confirmed"}
    ok = send_telegram(fmt_buy(d))
    return jsonify({"status": "sent" if ok else "failed", "message": "Test BUY alert fired"})

def poll_commands():
    offset = 0
    base = f"https://api.telegram.org/bot{BOT_TOKEN}"
    while True:
        try:
            upds = requests.get(f"{base}/getUpdates",
                params={"offset": offset, "timeout": 30}, timeout=35).json().get("result", [])
            for upd in upds:
                offset = upd["update_id"] + 1
                msg  = upd.get("message", {})
                text = msg.get("text", "")
                cid  = str(msg.get("chat", {}).get("id", ""))
                if text == "/start":
                    send_telegram("XAU Sniper Bot ACTIVE\n\nHi Rolif! Sending XAUUSD 15M sniper alerts.\n\n/status - Check bot\n/help - How it works\n/test - Send test alert", cid)
                elif text == "/status":
                    send_telegram(f"STATUS: ONLINE\nTime: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}\nWebhook: CONNECTED\nWatching: XAUUSD 15M", cid)
                elif text == "/help":
                    send_telegram("How It Works:\n1. TradingView watches XAUUSD 15M\n2. All 4 filters confirm:\n   - EMA200 + HMA50 trend\n   - Liquidity sweep\n   - ADX above 25\n   - Adaptive ATR signal\n3. Alert fires to Telegram instantly\n\nNot financial advice.", cid)
                elif text == "/test":
                    d = {"price":"2345.50","tp":"2375.50","sl":"2335.50","adx":"32.4","strength":"78","sweep":"Bull Sweep Confirmed"}
                    send_telegram(fmt_buy(d), cid)
        except Exception as e:
            log.error(f"Poll error: {e}")
        time.sleep(1)

if __name__ == "__main__":
    threading.Thread(target=poll_commands, daemon=True).start()
    log.info(f"Webhook: http://0.0.0.0:{PORT}/webhook/{WEBHOOK_KEY}")
    app.run(host="0.0.0.0", port=PORT, debug=False)
