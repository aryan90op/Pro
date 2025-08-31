# bot.py
import os
import re
import json
import io
import pathlib
from telegram import Update, InputFile
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
)

TOKEN = os.getenv("BOT_TOKEN")
MASTER_KEY = "Aryan9936"
BOT_OWNER_ID = 6497509361  # Replace with your Telegram ID
USERS_FILE = "allowed_users.json"
DOWNLOAD_DIR = "downloads"
pathlib.Path(DOWNLOAD_DIR).mkdir(parents=True, exist_ok=True)

def load_users():
    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)

ALLOWED_USERS = load_users()

def is_allowed(uid):
    return uid == BOT_OWNER_ID or uid in ALLOWED_USERS

user_data = {}

def get_defaults():
    return {
        "mode": None,
        "step": None,
        "numbers": [],
        "contacts_per_file": 100,
        "filename_gen": None,
        "contact_prefix": "Contact",
        "contact_start": 1,
        "vcf_files": []
    }

def check_access(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        uid = update.effective_user.id
        if not is_allowed(uid):
            await update.message.reply_text("❌ Buy premium from @random_0988")
            return
        return await func(update, context)
    return wrapper

def increment_filename(base_name):
    match = re.search(r'(\d+)', base_name)
    if not match:
        def gen(n): return f"{base_name}{n}.vcf"
        return gen
    num_str = match.group(1)
    prefix = base_name[:match.start(1)]
    suffix = base_name[match.end(1):]
    start = int(num_str)
    def gen(n):
        return f"{prefix}{start+n}{suffix}.vcf"
    return gen

@check_access
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_data[chat_id] = get_defaults()
    await update.message.reply_text("👋 Welcome! Type /help to see commands.")

@check_access
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    menu = """
🔄 𝗙𝗶𝗹𝗲 𝗖𝗼𝗻𝘃𝗲𝗿𝘀𝗶𝗼𝗻
/cv_txt_to_vcf - TXT → VCF
/cv_vcf_to_txt - VCF → TXT

📁 𝗙𝗶𝗹𝗲 𝗠𝗮𝗻𝗮𝗴𝗲𝗺𝗲𝗻𝘁
/joining - Merge TXT
/joinvcf - Merge VCF

⚙️ 𝗢𝘁𝗵𝗲𝗿
/reset_conversions - Reset
/reportbug - Report bug
"""
    await update.message.reply_text(menu)

async def admin_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /admin <key>")
        return
    if context.args[0] == MASTER_KEY:
        uid = update.effective_user.id
        if uid not in ALLOWED_USERS and uid != BOT_OWNER_ID:
            ALLOWED_USERS.append(uid)
            save_users(ALLOWED_USERS)
        await update.message.reply_text("✅ You are now admin.")
    else:
        await update.message.reply_text("❌ Wrong key.")

async def add_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != BOT_OWNER_ID:
        await update.message.reply_text("Owner only.")
        return
    try:
        uid = int(context.args[0])
        if uid not in ALLOWED_USERS: ALLOWED_USERS.append(uid)
        save_users(ALLOWED_USERS)
        await update.message.reply_text(f"Added {uid}")
    except:
        await update.message.reply_text("Usage: /add <id>")

async def remove_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != BOT_OWNER_ID:
        await update.message.reply_text("Owner only.")
        return
    try:
        uid = int(context.args[0])
        if uid == BOT_OWNER_ID:
            await update.message.reply_text("😎 BAAP SE PANGA NHI")
            return
        if uid in ALLOWED_USERS:
            ALLOWED_USERS.remove(uid)
            save_users(ALLOWED_USERS)
            await update.message.reply_text(f"Removed {uid}")
        else:
            await update.message.reply_text("Not found.")
    except:
        await update.message.reply_text("Usage: /remove <id>")

async def list_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != BOT_OWNER_ID:
        await update.message.reply_text("Owner only.")
        return
    await update.message.reply_text(f"Users: {ALLOWED_USERS}")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("admin", admin_cmd))
    app.add_handler(CommandHandler("add", add_user))
    app.add_handler(CommandHandler("remove", remove_user))
    app.add_handler(CommandHandler("list", list_users))
    app.run_polling()

if __name__ == "__main__":
    main()
