import os
import requests
import yfinance as yf
import pandas_ta as ta

# GitHub Secrets'dan ma'lumotlarni olish
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

# Tahlil qilinadigan aktivlar ro'yxati
ASSETS = {
    "BTC-USD": "Bitcoin (BTC)",
    "GC=F": "Oltin (XAUUSD)",
    "EURUSD=X": "EUR/USD",
    "AAPL": "Apple (AAPL)",
    "NVDA": "Nvidia (NVDA)",
    "TSLA": "Tesla (TSLA)",
    "MSFT": "Microsoft (MSFT)"
}

def send_telegram_msg(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

def analyze_market():
    signals = []
    
    for symbol, name in ASSETS.items():
        try:
            # So'nggi narxlarni bepul yuklab olish (1 soatlik taymfreym)
            df = yf.download(symbol, period="5d", interval="1h", progress=False)
            if df.empty:
                continue

            # Indikatorlarni hisoblash
            df['RSI'] = ta.rsi(df['Close'], length=14)
            df['EMA20'] = ta.ema(df['Close'], length=20)
            
            latest = df.iloc[-1]
            close_price = round(float(latest['Close']), 2)
            rsi = round(float(latest['RSI']), 2)
            
            # Signal shartlari
            # RSI 30 dan past va narx EMA dan yuqori bo'lsa -> BUY Signal
            if rsi < 35:
                signals.append(f"🟢 **BUY SIGNAL**: {name}\nJoriy narx: ${close_price}\nRSI: {rsi} (Oversold)")
            # RSI 70 dan baland bo'lsa -> SELL Signal
            elif rsi > 65:
                signals.append(f"🔴 **SELL SIGNAL**: {name}\nJoriy narx: ${close_price}\nRSI: {rsi} (Overbought)")
                
        except Exception as e:
            print(f"Xatolik {symbol} da: {e}")

    # Agar signallar bo'lsa Telegramga yuborish
    if signals:
        full_message = "📊 **YANGI TRADING SIGNALLAR** 📊\n\n" + "\n\n---\n\n".join(signals)
        send_telegram_msg(full_message)
    else:
        print("Hozircha xavfsiz signal yo'q.")

if __name__ == "__main__":
    analyze_market()
