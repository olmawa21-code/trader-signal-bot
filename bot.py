import os
import requests
import yfinance as yf
import pandas as pd

# GitHub Secrets'dan token va chat ID'larni olish
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

# Tahlil qilinadigan top aktivlar ro'yxati
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
    """Telegram kanal/guruhga xabar yuborish funksiyasi"""
    if not BOT_TOKEN or not CHAT_ID:
        print("Xatolik: BOT_TOKEN yoki CHAT_ID topilmadi!")
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("Xabar Telegram'ga muvaffaqiyatli yuborildi!")
        else:
            print(f"Telegram API xatosi: {response.text}")
    except Exception as e:
        print(f"Xabar yuborishda xatolik: {e}")

def calculate_rsi(series, period=14):
    """RSI indikatorini hisoblash"""
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def analyze_market():
    """Bozorni tahlil qilish va signal hosil qilish"""
    signals = []

    for symbol, name in ASSETS.items():
        try:
            # So'nggi 5 kunlik 1 soatlik intervaldagi ma'lumotlarni yuklab olish
            df = yf.download(symbol, period="5d", interval="1h", progress=False)
            if df.empty:
                continue

            close_prices = df['Close']
            if isinstance(close_prices, pd.DataFrame):
                close_prices = close_prices.iloc[:, 0]

            # Indikatorlar
            rsi_series = calculate_rsi(close_prices)
            sma20_series = close_prices.rolling(window=20).mean()

            latest_price = round(float(close_prices.iloc[-1]), 2)
            latest_rsi = round(float(rsi_series.iloc[-1]), 2)
            latest_sma = round(float(sma20_series.iloc[-1]), 2)

            # Signal berish shartlari:
            # RSI < 38 va narx SMA20 dan past bo'lsa -> BUY Signal
            if latest_rsi < 38 and latest_price < latest_sma:
                signals.append(
                    f"🟢 **SOTIB OLISH (BUY) SIGNALI**\n"
                    f"📌 **Aktiv:** {name}\n"
                    f"💵 **Joriy narx:** `${latest_price}`\n"
                    f"📊 **RSI ko'rsatkichi:** `{latest_rsi}` (Bozor arzonlashgan)"
                )
            # RSI > 62 va narx SMA20 dan yuqori bo'lsa -> SELL Signal
            elif latest_rsi > 62 and latest_price > latest_sma:
                signals.append(
                    f"🔴 **SOTISH (SELL) SIGNALI**\n"
                    f"📌 **Aktiv:** {name}\n"
                    f"💵 **Joriy narx:** `${latest_price}`\n"
                    f"📊 **RSI ko'rsatkichi:** `{latest_rsi}` (Bozor qimmatlashgan)"
                )

        except Exception as e:
            print(f"{symbol} tahlilida xatolik: {e}")

    # Agar signallar bo'lsa, xabarga samimiy eslatma va tilaklarni qo'shib yuborish
    if signals:
        header = (
            "✨ **Kanalimiz a'zolariga samimiy qutlov!** ✨\n"
            "Xush kelibsiz! Bizning maqsdimiz — bozor tahlilida sizga yordam berish.\n\n"
            "⚠️ **Muhim eslatma:**\n"
            "• Berilayotgan signallar faqat analitik ma'lumot hisoblanadi.\n"
            "• **Bitim ochish mutlaqo majburiy emas** va faqat o'z xohishingizga bog'liq.\n"
            "• Har doim xatarlarni boshqarish (Risk Management) qoidalariga rioya qiling.\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        )

        footer = (
            "\n\n━━━━━━━━━━━━━━━━━━━━━━\n"
            "🕊 *Omad va muvaffaqiyatli savdo tilaymiz! O'z qaroringiz va bilimingizga tayanib ish tuting.*"
        )

        full_message = header + "\n\n---\n\n".join(signals) + footer
        send_telegram_msg(full_message)
    else:
        print("Hozircha bozorda aniq va xavfsiz signal mavjud emas.")

if __name__ == "__main__":
    # Kod ishga tushganda avtomatik bozor tahlil qilinadi
    analyze_market()
