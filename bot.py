import os
import requests
import yfinance as yf
import pandas as pd

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

def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def analyze_market():
    signals = []
    
    for symbol, name in ASSETS.items():
        try:
            # Ma'lumotlarni bepul yuklab olish (1 soatlik taymfreym)
            df = yf.download(symbol, period="5d", interval="1h", progress=False)
            if df.empty:
                continue

            # RSI indikatorini sodda formula bilan hisoblash
            close_prices = df['Close']
            if isinstance(close_prices, pd.DataFrame):
                close_prices = close_prices.iloc[:, 0]
                
            rsi_series = calculate_rsi(close_prices)
            latest_price = round(float(close_prices.iloc[-1]), 2)
            latest_rsi = round(float(rsi_series.iloc[-1]), 2)
            
            # Signal shartlari
            if latest_rsi < 35:
                signals.append(f"🟢 **BUY SIGNAL**: {name}\nJoriy narx: ${latest_price}\nRSI: {latest_rsi} (Arzonlashgan)")
            elif latest_rsi > 65:
                signals.append(f"🔴 **SELL SIGNAL**: {name}\nJoriy narx: ${latest_price}\nRSI: {latest_rsi} (Qimmatlashgan)")
                
        except Exception as e:
            print(f"Xatolik {symbol} da: {e}")

    # Agar signallar topsa Telegram'ga yuboradi
    if signals:
        full_message = "📊 **YANGI TRADING SIGNALLAR** 📊\n\n" + "\n\n---\n\n".join(signals)
        send_telegram_msg(full_message)
    else:
        print("Hozircha mos signal yo'q.")

if __name__ == "__main__":
    analyze_market()
