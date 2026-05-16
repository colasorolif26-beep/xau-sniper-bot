"""
XAUUSD SNIPER TELEGRAM BOT — Pre-configured for Rolif Colaso
TradingView Webhook -> Telegram Alerts
"""
import os, json, logging, threading, time
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

def send_telegram(text, chat_id=CHAT_ID):
    try:
        r = requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={"chat_id": chat_id, "text": text, "parse_mode": "HTML", "disable_web_page_preview": True}, timeout=10)
        r.raise_for_status(); return True
    except Exception as e:
        log.error(f"Telegram failed: {e}"); return False

def fmt_buy(d):
    t = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return (
        "🟢━━━━━━━━━━━━━━━━━━━━━━\n🎯 <b>XAU/USD SNIPER BUY</b>\n🟢━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"⏰ <b>Time:</b>      {t}\n📊 <b>Symbol:</b>    XAUUSD (Gold)\n⏱ <b>Timeframe:</b> 15M\n\n"
        "─────────────────────────\n"
        f"📍 <b>Entry:</b>  <code>{d.get('price','N/A')}</code>\n"
        f"✅ <b>TP:</b>     <code>{d.get('tp','N/A')}</code>  (+300 pips)\n"
        f"❌ <b>SL:</b>     <code>{d.get('sl','N/A')}</code>  (-100 pips)\n📐 <b>R:R:</b>    1 : 3\n\n"
        "─────────────────────────\n🔍 <b>FILTER CONFIRMATIONS</b>\n"
        f"📈 EMA 200 + HMA 50  ✅ BULLISH\n💧 Liquidity Sweep   ✅ {d.get('sweep','Bull Sweep OK')}\n"
        f"📡 ADX               ✅ {d.get('adx','25+')}\n💪 Trend Strength    ✅ {d.get('strength','Strong')}%\n"
        "🔄 Adaptive Signal   ✅ CONFIRMED\n\n─────────────────────────\n"
        "⚠️ <i>Risk management always. Not financial advice.</i>\n🟢━━━━━━━━━━━━━━━━━━━━━━")

def fmt_sell(d):
    t = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return (
        "🔴━━━━━━━━━━━━━━━━━━━━━━\n🎯 <b>XAU/USD SNIPER SELL</b>\n🔴━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"⏰ <b>Time:</b>      {t}\n📊 <b>Symbol:</b>    XAUUSD (Gold)\n⏱ <b>Timeframe:</b> 15M\n\n"
        "─────────────────────────\n"
        f"📍 <b>Entry:</b>  <code>{d.get('price','N/A')}</code>\n"
        f"✅ <b>TP:</b>     <code>{d.get('tp','N/A')}</code>  (-300 pips)\n"
        f"❌ <b>SL:</b>     <code>{d.get('sl','N/A')}</code>  (+100 pips)\n📐 <b>R:R:</b>    1 : 3\n\n"
        "─────────────────────────\n🔍 <b>FILTER CONFIRMATIONS</b>\n"
        f"📉 EMA 200 + HMA 50  ✅ BEARISH\n💧 Liquidity Sweep   ✅ {d.get('sweep','Bear Sweep OK')}\n"
        f"📡 ADX               ✅ {d.get('adx','25+')}\n💪 Trend Strength    ✅ {d.get('strength','Strong')}%\n"
        "🔄 Adaptive Signal   ✅ CONFIRMED\n\n─────────────────────────\n"
        "⚠️ <i>Risk management always. Not financial advice.</i>\n🔴━━━━━━━━━━━━━━━━━━━━━━")

def fmt_close(d):
    t = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return (
        "⚪️━━━━━━━━━━━━━━━━━━━━━━\n📤 <b>XAU/USD POSITION CLOSED</b>\n⚪️━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"⏰ <b>Time:</b>    {t}\n📍 <b>Close:</b>  <code>{d.get('price','N/A')}</code>\n"
        f"📝 <b>Reason:</b> {d.get('reason','Signal Exit')}\n💰 <b>P&L:</b>    {d.get('pnl','N/A')} pips\n"
        "⚪️━━━━━━━━━━━━━━━━━━━━━━")

@app.route("/webhook/<secret>", methods=["POST"])
def webhook(secret):
    if secret != WEBHOOK_KEY:
        return jsonify({"error": "Unauthorized"}), 401
    try:
        data = request.get_json(force=True) or {}
    except Exception:
        return jsonify({"error": "Bad JSON"}), 400
    action = str(data.get("action","")).upper()
    if action == "BUY":       msg = fmt_buy(data)
    elif action == "SELL":    msg = fmt_sell(data)
    elif action in ("CLOSE","EXIT"): msg = fmt_close(data)
    else: return jsonify({"error": f"Unknown action: {action}"}), 400
    ok = send_telegram(msg)
    return jsonify({"status": "sent" if ok else "failed"}), 200 if ok else 500

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "online", "bot": "XAU Sniper Rolif", "chat_id": CHAT_ID})

def poll_commands():
    offset = 0
    base = f"https://api.telegram.org/bot{BOT_TOKEN}"
    while True:
        try:
            upds = requests.get(f"{base}/getUpdates", params={"offset": offset, "timeout": 30}, timeout=35).json().get("result", [])
            for upd in upds:
                offset = upd["update_id"] + 1
                msg  = upd.get("message", {})
                text = msg.get("text", "")
                cid  = str(msg.get("chat", {}).get("id", ""))
                if text == "/start":
                    send_telegram("🎯 <b>XAU Sniper Bot — ACTIVE</b>\n\nHi Rolif! I'll notify you the moment\na sniper entry fires on XAUUSD 15M.\n\n/status — Check bot\n/help — How it works", cid)
                elif text == "/status":
                    send_telegram(f"✅ <b>ONLINE</b>\n⏰ {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}\n📡 Webhook: CONNECTED\n🎯 Watching: XAUUSD 15M", cid)
                elif text == "/help":
                    send_telegram("📖 <b>How It Works</b>\n\n1. TradingView watches XAUUSD 15M\n2. All 4 filters must confirm:\n   ✅ EMA200 + HMA50 trend\n   ✅ Liquidity sweep\n   ✅ ADX above 25\n   ✅ Adaptive ATR signal\n3. Alert fires instantly to Telegram\n4. You get Entry + TP + SL\n\n⚠️ Not financial advice.", cid)
        except Exception as e:
            log.error(f"Poll error: {e}")
        time.sleep(1)

if __name__ == "__main__":
    threading.Thread(target=poll_commands, daemon=True).start()
    log.info(f"Webhook: http://0.0.0.0:{PORT}/webhook/{WEBHOOK_KEY}")
    app.run(host="0.0.0.0", port=PORT, debug=False)
