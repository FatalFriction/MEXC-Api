import os
import requests
import random
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Load environment variables
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
ALLOWED_USER_ID = int(os.getenv('ALLOWED_USER_ID'))
ALLOWED_CHAT_IDS = [int(chat_id) for chat_id in os.getenv('ALLOWED_CHAT_IDS', '').split(',') if chat_id.strip().isdigit()]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (compatible; MyTelegramBot/1.0)'
}

tip_pool = [
    "💡 Perhatikan pergerakan volume—lonjakan volume bisa menandakan perubahan tren.",
    "📉 Jangan terburu-buru membeli saat harga turun—tunggu sinyal pembalikan yang jelas.",
    "📈 Hindari FOMO—jangan beli hanya karena harga naik cepat.",
    "🔍 Gunakan indikator teknikal sederhana seperti RSI atau MACD untuk bantu keputusan.",
    "🧭 Selalu tetapkan target profit dan stop loss sebelum masuk posisi.",
    "🔄 Gunakan time frame yang sesuai—hindari keputusan hanya dari grafik 1 menit.",
    "📌 Lihat pola candlestick seperti Doji, Engulfing, atau Hammer untuk deteksi pembalikan.",
    "📊 Jangan trading berdasarkan emosi—gunakan data dan analisis.",
    "🕵️ Periksa sentimen pasar di komunitas seperti Twitter atau Telegram.",
    "⚖️ Diversifikasi—jangan taruh semua modal di satu koin.",
    "📚 Pelajari support dan resistance—itu dasar penting analisis teknikal.",
    "⏳ Sabar adalah kunci—tunggu setup terbaik, jangan asal masuk.",
    "🎯 Gunakan akun demo untuk uji strategi sebelum live trading.",
    "🧮 Gunakan kalkulator risiko untuk atur besar posisi berdasarkan modal.",
    "⚠️ Jangan kejar kerugian—lebih baik evaluasi dan tunggu peluang baru.",
    "📆 Hindari trading saat rilis berita besar kalau belum berpengalaman.",
    "🧰 Gunakan alat bantu seperti TradingView untuk melihat chart dengan lengkap.",
    "📌 Catat setiap transaksi agar bisa belajar dari pengalaman.",
    "🌐 Jangan lupakan faktor global seperti inflasi, suku bunga, dan regulasi.",
    "🚫 Jangan gunakan uang kebutuhan harian untuk trading.",
    "🧠 Tetap belajar—pasar selalu berubah dan strategi juga perlu berkembang.",
    "🧊 Saat market sideways, pertimbangkan strategi scalping atau swing.",
    "🔐 Simpan aset secara aman di wallet jika tidak digunakan untuk trading.",
    "📈 Volume tinggi + harga naik bisa tandakan tren kuat.",
    "🔻 Jangan asal beli coin murah—murah bukan berarti undervalued.",
    "📎 Pantau berita dari proyek coin yang ditradingkan.",
    "⚙️ Coba gunakan bot untuk bantu eksekusi strategi otomatis.",
    "🚧 Jangan terlalu sering ganti strategi, fokus pada yang dipahami dulu.",
    "📉 Harga koreksi setelah naik tinggi itu normal—hindari panik.",
    "🌱 Trading bukan jalan cepat kaya—fokus pada konsistensi jangka panjang."
]

def is_allowed(update: Update) -> bool:
    chat = update.effective_chat
    user = update.effective_user

    logging.info(f"Checking access: user_id={user.id}, chat_id={chat.id}, chat_type={chat.type}")
    
    if chat.type == "private":
        return user.id == ALLOWED_USER_ID
    else:
        return chat.id in ALLOWED_CHAT_IDS

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info(f"/start command received from user_id={update.effective_user.id}, chat_id={update.effective_chat.id}")
    if not is_allowed(update):
        logging.warning("Unauthorized access attempt to /start")
        return
    await update.message.reply_text("👋 Selamat datang! Gunakan /randomcoin untuk mendapatkan koin acak dan statistik pasar dari MEXC.")

# /randomcoin command
async def random_coin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    logging.info(f"/screen command received from user_id={user_id}, chat_id={chat_id}")

    if not is_allowed(update):
        logging.warning(f"Unauthorized access to /screen by user_id={user_id}")
        return

    try:
        logging.info("Fetching symbol list...")
        response = requests.get('https://api.mexc.com/api/v3/defaultSymbols', headers=HEADERS, timeout=20)
        symbol_list = response.json().get("data", [])
        usdt_pairs = [s for s in symbol_list if s.endswith("USDT")]
        logging.info(f"Found {len(usdt_pairs)} USDT pairs.")

        if not usdt_pairs:
            logging.warning("No USDT pairs found.")
            await update.message.reply_text("⚠️ Tidak ada pasangan USDT ditemukan.")
            return

        symbol = random.choice(usdt_pairs)
        logging.info(f"Selected symbol: {symbol}")

        # Fetch market data
        logging.info("Fetching market data for selected symbol...")
        depth = requests.get('https://api.mexc.com/api/v3/depth', params={'symbol': symbol, 'limit': 5}, headers=HEADERS).json()
        ticker_24h = requests.get('https://api.mexc.com/api/v3/ticker/24hr', params={'symbol': symbol}, headers=HEADERS).json()
        ticker_price = requests.get('https://api.mexc.com/api/v3/ticker/price', params={'symbol': symbol}, headers=HEADERS).json()
        book_ticker = requests.get('https://api.mexc.com/api/v3/ticker/bookTicker', params={'symbol': symbol}, headers=HEADERS).json()
        avg_price = requests.get('https://api.mexc.com/api/v3/avgPrice', params={'symbol': symbol}, headers=HEADERS).json()
        klines = requests.get('https://api.mexc.com/api/v3/klines', params={'symbol': symbol, 'interval': '1h', 'limit': 13}, headers=HEADERS).json()

        logging.info("Building response message...")
        message = f"🎯 *Today Coin:* `{symbol}`\n\n"

        if "asks" in depth and "bids" in depth:
            message += (
                "📘 *Order Book Depth (Teratas)*\n"
                f"   • Ask: `{depth['asks'][0][0]}` @ {depth['asks'][0][1]}\n"
                f"   • Bid: `{depth['bids'][0][0]}` @ {depth['bids'][0][1]}\n\n"
            )

        if "lastPrice" in ticker_24h:
            message += (
                "📊 *Statistik 24 Jam*\n"
                f"   • Terakhir: `{ticker_24h['lastPrice']}`\n"
                f"   • Tertinggi: `{ticker_24h['highPrice']}`\n"
                f"   • Terendah: `{ticker_24h['lowPrice']}`\n"
                f"   • Volume: `{ticker_24h['volume']}`\n\n"
            )

        if "price" in ticker_price:
            message += f"💰 *Harga Saat Ini*\n   • `{ticker_price['price']}`\n\n"

        if "bidPrice" in book_ticker and "askPrice" in book_ticker:
            message += (
                "📒 *Book Ticker*\n"
                f"   • Bid Terbaik: `{book_ticker['bidPrice']}` ({book_ticker['bidQty']})\n"
                f"   • Ask Terbaik: `{book_ticker['askPrice']}` ({book_ticker['askQty']})\n\n"
            )

        if "price" in avg_price:
            message += f"📈 *Harga Rata-Rata*\n   • `{avg_price['price']}` (Interval: {avg_price['mins']} menit)\n\n"

        tip_text = "*🧠 Ringkasan untuk Pemula:*\n"
        if isinstance(klines, list) and len(klines) >= 13:
            open_price = float(klines[0][1])
            close_price = float(klines[-1][4])
            pct_change = ((close_price - open_price) / open_price) * 100

            logging.info(f"Kline analysis: open={open_price}, close={close_price}, change={pct_change:.2f}%")

            message += (
                "🕒 *Analisis 12 Jam Terakhir (1H Candles)*\n"
                f"   • Harga Buka: `{open_price}`\n"
                f"   • Harga Tutup: `{close_price}`\n"
                f"   • Perubahan: `{pct_change:.2f}%`\n\n"
            )

            if pct_change > 3:
                tip_text += (
                    "📌 *Saran:* Harga naik tajam selama 12 jam terakhir.\n"
                    "🚀 Potensi tren naik, tapi tetap waspada terhadap pembalikan.\n"
                    "💡 Pertimbangkan untuk menunggu penurunan harga sebelum beli.\n"
                )
            elif pct_change < -3:
                tip_text += (
                    "📌 *Saran:* Harga turun cukup besar selama 12 jam terakhir.\n"
                    "📉 Waspadai tren menurun yang masih berlanjut.\n"
                    "💡 Tunggu konfirmasi pembalikan arah sebelum masuk.\n"
                )
            else:
                tip_text += (
                    "📌 *Saran:* Harga bergerak stabil dalam 12 jam terakhir.\n"
                    "🔄 Cocok untuk strategi jangka pendek atau sideway trading.\n"
                )
        else:
            logging.warning("Not enough klines for trend analysis.")
            tip_text += f"\n{random.choice(tip_pool)}\n"

        message += tip_text
        await update.message.reply_text(message, parse_mode="Markdown")

    except Exception as e:
        logging.exception("Error in /screen command")

# Start the bot
def main():
    logging.info("Starting bot...")
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("screen", random_coin))
    logging.info("🚀 Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()
