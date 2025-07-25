import logging
import os
import sqlite3
from dotenv import load_dotenv
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Updater,
    MessageHandler,
    Filters,
    CommandHandler,
    CallbackContext,
    ChatMemberHandler,
    CallbackQueryHandler,
)
from datetime import datetime, timedelta
from telegram.error import TelegramError

# === Flask Keep-Alive Setup ===
app = Flask('')


@app.route('/')
def home():
    return "🤖 Bot is running!"


def run():
    app.run(host='0.0.0.0', port=8080)


def keep_alive():
    t = Thread(target=run)
    t.start()


# === Config ===
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
BOT_USERNAME = "EmTrack_bot"  # 🔁 Replace with your actual bot username

# === Logging Setup ===
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)


# === DB Setup ===
def init_db():
    conn = sqlite3.connect("messages.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            user_id INTEGER,
            username TEXT,
            group_id INTEGER,
            group_title TEXT,
            timestamp TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS groups (
            group_id INTEGER PRIMARY KEY,
            title TEXT
        )
    """)
    conn.commit()
    conn.close()


# === DB Functions ===
def log_message(user_id, username, group_id, group_title):
    conn = sqlite3.connect("messages.db")
    c = conn.cursor()
    c.execute(
        "INSERT INTO messages (user_id, username, group_id, group_title, timestamp) VALUES (?, ?, ?, ?, ?)",
        (user_id, username, group_id, group_title,
         datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()


def store_group(group_id, title):
    conn = sqlite3.connect("messages.db")
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO groups (group_id, title) VALUES (?, ?)",
              (group_id, title))
    conn.commit()
    conn.close()


def get_all_groups():
    conn = sqlite3.connect("messages.db")
    c = conn.cursor()
    c.execute("SELECT group_id, title FROM groups")
    results = c.fetchall()
    conn.close()
    return results


def get_group_message_count(username, group_id):
    conn = sqlite3.connect("messages.db")
    c = conn.cursor()
    c.execute(
        "SELECT COUNT(*) FROM messages WHERE username = ? AND group_id = ?",
        (username, group_id))
    total = c.fetchone()[0]

    since = datetime.utcnow() - timedelta(days=1)
    c.execute(
        "SELECT COUNT(*) FROM messages WHERE username = ? AND group_id = ? AND timestamp >= ?",
        (username, group_id, since.isoformat()))
    last24 = c.fetchone()[0]

    conn.close()
    return total, last24


# === Helpers ===
def is_private_chat(update: Update):
    if update.effective_chat:
        return update.effective_chat.type == "private"
    return False


def dm_redirect_buttons():
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("🧑‍💻 Open Bot in DM",
                             url=f"https://t.me/{BOT_USERNAME}")
    ], [InlineKeyboardButton("🆘 Help", callback_data='help')]])


# === Command: /check ===
def check_user(update: Update, context: CallbackContext):
    if not is_private_chat(update):
        update.message.reply_text("⚠️ For full features, please DM me.",
                                  reply_markup=dm_redirect_buttons())
        return

    if not context.args:
        update.message.reply_text("Usage: /check @username")
        return

    if update.effective_user is None:
        update.message.reply_text("Error: Could not identify user.")
        return

    username = context.args[0].lstrip('@')
    caller_id = update.effective_user.id
    groups = get_all_groups()

    msg = f"📊 *User Activity Report*\n👤 Username: @{username}\n\n"
    shown_any = False

    for group_id, title in groups:
        try:
            member = context.bot.get_chat_member(group_id, caller_id)
            if member.status not in ["left", "kicked"]:
                total, last24 = get_group_message_count(username, group_id)
                msg += f"🏘️ *Community:* {title}\n📨 Total Messages: {total}\n⏱️ Last 24h: {last24}\n\n"
                shown_any = True
        except TelegramError:
            continue

    if not shown_any:
        msg = "❌ You don’t have access to any communities with this user’s messages."

    keyboard = [[
        InlineKeyboardButton("🔙 Back to Menu", callback_data='back_to_menu')
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(msg,
                              parse_mode='Markdown',
                              reply_markup=reply_markup)


# === Command: /groups ===
def list_groups(update: Update, context: CallbackContext):
    if not is_private_chat(update):
        update.message.reply_text("⚠️ Please use this command in DM.",
                                  reply_markup=dm_redirect_buttons())
        return

    groups = get_all_groups()
    if not groups:
        update.message.reply_text("No tracked groups found.")
        return

    msg = "🌐 *Communities I'm tracking:*\n\n"
    for gid, title in groups:
        msg += f"🔸 {title} (`{gid}`)\n"
    update.message.reply_text(msg, parse_mode='Markdown')


# === Command: /start ===
def start(update: Update, context: CallbackContext):
    if not is_private_chat(update):
        update.message.reply_text(
            "⚠️ This bot works best in DM. Click below to continue:",
            reply_markup=dm_redirect_buttons())
        return

    keyboard = [
        [InlineKeyboardButton("👤 Check User", callback_data='check_user')],
        [
            InlineKeyboardButton("🌐 Select Community",
                                 callback_data='select_community')
        ],
        [
            InlineKeyboardButton("📊 Weekly Report",
                                 callback_data='weekly_report')
        ],
        [InlineKeyboardButton("🆘 Help", callback_data='help')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        "👋 Welcome to *EmTeamTrackerBot!*\n\nUse the buttons below to navigate.",
        parse_mode="Markdown",
        reply_markup=reply_markup)


# === Button Callbacks ===
def handle_buttons(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    if query.data == 'check_user':
        query.edit_message_text(
            "🔍 Please type the command: `/check @username`",
            parse_mode='Markdown')

    elif query.data == 'select_community':
        groups = get_all_groups()
        if not groups:
            query.edit_message_text("❌ No communities found.")
            return

        msg = "🌐 *Communities I'm tracking:*\n\n"
        for gid, title in groups:
            msg += f"🔸 {title} (`{gid}`)\n"
        query.edit_message_text(msg, parse_mode='Markdown')

    elif query.data == 'weekly_report':
        query.edit_message_text("📊 Weekly report feature is coming soon!")

    elif query.data == 'help':
        help_text = (
            "📌 *EmTeamTrackerBot Help*\n\n"
            "🔸 `/check @username` — See messages from your allowed communities\n"
            "🔸 `/groups` — View tracked group list\n"
            "🔸 Use only in DM for full functionality\n\n"
            "💬 Contact @Emranrx for support")
        query.edit_message_text(help_text, parse_mode='Markdown')

    elif query.data == 'back_to_menu':
        keyboard = [
            [InlineKeyboardButton("👤 Check User", callback_data='check_user')],
            [
                InlineKeyboardButton("🌐 Select Community",
                                     callback_data='select_community')
            ],
            [
                InlineKeyboardButton("📊 Weekly Report",
                                     callback_data='weekly_report')
            ],
            [InlineKeyboardButton("🆘 Help", callback_data='help')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text("🔙 Back to Main Menu:",
                                reply_markup=reply_markup)


# === Log messages ===
def handle_message(update: Update, context: CallbackContext):
    chat = update.effective_chat
    if chat and chat.type in ['group', 'supergroup']:
        user = update.effective_user
        if user:
            username = user.username if user.username else f"user_{user.id}"
            log_message(user.id, username, chat.id, chat.title)
            store_group(chat.id, chat.title)


# === Group Join Event ===
def new_chat_member(update: Update, context: CallbackContext):
    member = update.chat_member
    if member.new_chat_member.user.id == context.bot.id:
        store_group(member.chat.id, member.chat.title)
        welcome_text = (
            "👋 *Hello Everyone!*\n\n"
            "Thank you for adding *EmTeamTrackerBot* to this community.\n\n"
            "🔎 This bot helps track and analyze user message activity across groups.\n"
            "To use advanced features, please DM me directly.")
        buttons = dm_redirect_buttons()
        context.bot.send_message(chat_id=member.chat.id,
                                 text=welcome_text,
                                 parse_mode='Markdown',
                                 reply_markup=buttons)


# === Start Bot ===
def main():
    init_db()
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("check", check_user))
    dp.add_handler(CommandHandler("groups", list_groups))
    dp.add_handler(CallbackQueryHandler(handle_buttons))
    dp.add_handler(
        MessageHandler(Filters.text & (~Filters.command), handle_message))
    dp.add_handler(
        ChatMemberHandler(new_chat_member, ChatMemberHandler.MY_CHAT_MEMBER))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    keep_alive()  # 🔁 Keeps bot active via UptimeRobot ping
    main()
