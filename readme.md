# 📊 Telegram Bot: MEXC Market Data + Beginner Trading Tips

This is a Python Telegram bot that fetches **random crypto market data from MEXC Exchange** and provides **beginner-friendly trading advice** in Bahasa Indonesia.

## 🔧 Features

- `/start`: Simple welcome message and how-to-use instructions
- `/randomcoin`:
  - Picks a random USDT trading pair from MEXC
  - Shows detailed market stats (24h stats, order book, price averages)
  - Includes 12-hour trend analysis based on hourly candlestick data
  - Shows context-aware beginner trading tips when trend is stable or data is unavailable

## 🔐 Access Control

- In **group/channel**: Anyone in the allowed chat(s) can use the bot
- In **private chat**: Only the bot owner (specified via `.env`) can use it

## 📦 Deployment (e.g., Railway)

1. Clone the repo.
2. Set environment variables **directly in Railway**, _not_ in the code:
   - `TELEGRAM_BOT_TOKEN`
   - `ALLOWED_USER_ID`
   - `ALLOWED_CHAT_IDS` (comma-separated)
3. Deploy with `requirements.txt` included.

## 📁 Environment Setup

```bash
pip install -r requirements.txt
