# 🤖 EmTeamTrackerBot

A powerful Telegram bot that tracks and reports user activity across multiple Telegram communities.

![Python](https://img.shields.io/badge/Python-3.9-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Telegram Bot](https://img.shields.io/badge/Telegram-Bot-blue)

---

## 📌 Features

- 🔍 Track user messages across Telegram groups
- 📈 Generate total and last 24h message reports
- 📊 Group message stats via command
- 🧑‍💻 User-friendly interface in DM with buttons
- 🗂️ SQLite-based local database
- ✅ Inline keyboard support
- 🔐 Admin-safe group access logic

---

## 🚀 How It Works

This bot listens to group messages and logs user activity in a local SQLite database. Users can check their own or others' activity via DM commands like `/check @username`.

---

## 🧰 Requirements

- Python 3.9+
- `python-telegram-bot` v13+
- `python-dotenv`
- `sqlite3`

Install with:

```bash
pip install -r requirements.txt


⚙️ Setup

    Clone this repository:

git clone https://github.com/Emranrx02/emteam-tracker-bot.git
cd emteam-tracker-bot

    Create a .env file and add your bot token:

BOT_TOKEN=your_telegram_bot_token_here

    Run the bot:

python main.py

🧪 Commands
Command	Description
/start	Show bot menu in DM
/check @user	Check a user’s activity (DM only)
/groups	Show tracked group list
🛠 Deployment

You can deploy the bot on:

    🧑‍💻 Replit (needs UptimeRobot to stay awake)

    🚂 Railway (recommended for 24/7 deployment)

    ☁️ Render, VPS, or any Python-supporting server

📄 License

MIT License © Emran Haque
🌐 Links

    🔗 Telegram Bot: @EmTrack_bot

    🌍 Author: Emranrx02

💬 Support

For setup help or customization, message @Emranrx on Telegram.
